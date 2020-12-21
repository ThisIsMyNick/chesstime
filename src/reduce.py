from multiprocessing import Process, Queue, current_process
import asyncio
import chess
import chess.pgn
import chess.engine
import csv
import time

TOTAL_GAMES = 50000

def analyze_games():
    i_f = open("../data/2020-11.pgn")

    #skip N we already read
    i = 50000
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


    o_f = open("filtered2.pgn", "wb")

    start_time = time.time()
    processed_games = 0
    while processed_games < TOTAL_GAMES:
        game = chess.pgn.read_game(i_f)
        if game.headers['Event'] != "Rated Blitz game":
            continue
        white_elo = int(game.headers['WhiteElo'])
        black_elo = int(game.headers['BlackElo'])

        if not (1000 <= white_elo < 2000) or \
           not (1000 <= black_elo < 2000):
               continue
        val = str(game) + "\n\n"
        o_f.write(val.encode())
        processed_games += 1
        if processed_games % 1000 == 0:
            print(f"processed {processed_games} / {TOTAL_GAMES}, {time.time() - start_time}")


analyze_games()
