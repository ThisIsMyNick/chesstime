from multiprocessing import Process, Queue, current_process
import asyncio
import chess
import chess.pgn
import chess.engine
import csv
import time

engines = {}

def find_first_blunder(input, output):
    """
    me = current_process().name
    if me not in engines:
        engines[me] = chess.engine.SimpleEngine.popen_uci("../stockfish")
    engine = engines[me]
    """
    engine = chess.engine.SimpleEngine.popen_uci("../stockfish")

    for game in iter(input.get, 'STOP'):
        sf_prev_eval = None
        sf_eval = None
        counter = 0

        while True:
            if game.is_end():
                break
            if counter > 60:
                break
            if sf_eval is not None and sf_eval.is_mate():
                break
            if sf_prev_eval is not None and abs(sf_eval.white().score() - sf_prev_eval.white().score()) >= 300:
                break

            sf_prev_eval = sf_eval
            info = engine.analyse(game.board(), chess.engine.Limit(time=0.1))
            sf_eval = info["score"]
            game = game.next()
            counter += 1

        if counter < 12: #skip throws
            output.put((game, 0, None, None))
        else:
            last_board = game.parent.board()
            output.put((game, counter, last_board, sf_eval.relative.score()))
    engine.quit()

CPU_COUNT = 3
TOTAL_GAMES = 10000
BATCH_SIZE = 20*CPU_COUNT

def analyze_games():
    #i_f = open("../data/2020-11.pgn")
    i_f = open("filtered.pgn")
    o_f = open("reduced.csv", "a")

    #skip N we already read
    i = 0
    while i > 0:
        game = chess.pgn.read_game(i_f)
        if game.headers['Event'] != "Rated Blitz game":
            continue
        white_elo = int(game.headers['WhiteElo'])
        black_elo = int(game.headers['BlackElo'])

        if not (1000 <= white_elo < 2000) or \
           not (1000 <= black_elo < 2000):
           continue
        i -= 1

    writer = csv.writer(o_f)

    start_time = time.time()
    games_processed = 0
    while games_processed < TOTAL_GAMES:

        games = []
        while len(games) < BATCH_SIZE:
            game = chess.pgn.read_game(i_f)
            if game.headers['Event'] != "Rated Blitz game":
                continue
            white_elo = int(game.headers['WhiteElo'])
            black_elo = int(game.headers['BlackElo'])

            if not (1000 <= white_elo < 2000) or \
               not (1000 <= black_elo < 2000):
               continue
            games.append(game)

        task_queue = Queue()
        done_queue = Queue()

        for game in games:
            task_queue.put(game)

        for i in range(CPU_COUNT):
            mp = Process(target=find_first_blunder, args=(task_queue, done_queue), name=i).start()

        for i in range(len(games)):
            game, counter, last_board, score = done_queue.get()
            if counter == 0 or counter == 60:
                continue

            white_elo = int(game.game().headers['WhiteElo'])
            black_elo = int(game.game().headers['BlackElo'])
            turn = 1 if game.turn() == chess.WHITE else 0
            clock = game.clock()
            writer.writerow([counter, last_board.fen(), score, white_elo, black_elo, turn, clock])

            games_processed += 1

        for i in range(CPU_COUNT):
            task_queue.put('STOP')

        print(f"processed {games_processed} / {TOTAL_GAMES}, {time.time() - start_time}")


analyze_games()
