from multiprocessing import Process, Queue
import asyncio
import chess
import chess.pgn
import chess.engine
import csv
import time
import io

#engines = {}

def find_first_blunder(input, output):
    """
    me = current_process().name
    if me not in engines:
        engines[me] = chess.engine.SimpleEngine.popen_uci("../stockfish")
    engine = engines[me]
    """
    engine = chess.engine.SimpleEngine.popen_uci("../stockfish")

    for sgame in iter(input.get, 'STOP'):
        game = chess.pgn.read_game(io.StringIO(sgame))
        sf_prev_eval = None
        sf_eval = None
        counter = 0

        while True:
            if game.is_end():
                counter = 0
                break
            if counter > 60:
                break
            if sf_eval is not None and sf_eval.is_mate():
                break
            if sf_prev_eval is not None and abs(sf_eval.white().score() - sf_prev_eval.white().score()) >= 300:
                break

            sf_prev_eval = sf_eval
            info = engine.analyse(game.board(), chess.engine.Limit(depth=12))
            sf_eval = info["score"]
            game = game.next()
            counter += 1

        if counter < 12: #skip throws
            output.put((0, None, None, None, None, None, None, None))
        else:
            last_board = str(game.parent.parent.board().fen())
            last_move = str(game.parent.move.uci())
            white_elo = int(game.game().headers['WhiteElo'])
            black_elo = int(game.game().headers['BlackElo'])
            turn = 1 if game.turn() == chess.WHITE else 0
            if game.clock() is None:
                output.put((0, None, None, None, None, None, None, None))
            else:
                clock = int(game.clock())
                output.put((counter, last_board, last_move, int(sf_eval.white().score(mate_score=10000)), white_elo, black_elo, turn, clock))
    engine.quit()

CPU_COUNT = 24
TOTAL_GAMES = 50000
BATCH_SIZE = 20*CPU_COUNT

def analyze_games():
    i_f = open("../../raid-storage/filtered2.pgn")
    o_f = open("../../raid-storage/reduced.csv", "w")

    #ignore N games (already collected)
    i = 0
    while i > 0:
        game = chess.pgn.read_game(i_f)
        i -= 1

    writer = csv.writer(o_f)

    start_time = time.time()
    games_processed = 0
    while games_processed < TOTAL_GAMES:

        games = []
        while len(games) < BATCH_SIZE:
            game = chess.pgn.read_game(i_f)
            if game is None:
                break
            games.append(str(game))

        if games == []:
            break

        task_queue = Queue()
        done_queue = Queue()

        for game in games:
            try:
                task_queue.put(game)
            except:
                pass

        for i in range(CPU_COUNT):
            try:
                mp = Process(target=find_first_blunder, args=(task_queue, done_queue), name=i).start()
            except:
                pass

        for i in range(len(games)):
            try:
                counter, last_board, last_move, score, white_elo, black_elo, turn, clock = done_queue.get()
                if counter == 0 or counter >= 60:
                    continue

                writer.writerow([counter, last_board, last_move, score, white_elo, black_elo, turn, clock])
                games_processed += 1
            except:
                pass


        for i in range(CPU_COUNT):
            task_queue.put('STOP')

        print(f"processed {games_processed} / {TOTAL_GAMES}, {time.time() - start_time}")


analyze_games()
