import tensorflow as tf
from tensorflow.keras import datasets, layers, models, regularizers
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
import numpy as np

import chess
import csv
import os

class Chess:
    def __init__(self):
        pass

    @staticmethod
    def move_to_output(move):
        n1 = ord(move[0]) - ord("a")
        n2 = int(move[1]) - 1
        n3 = ord(move[2]) - ord("a")
        n4 = int(move[3]) - 1
        n = f"0o{n1}{n2}{n3}{n4}"
        return np.array(int(n, 8))

    @staticmethod
    def output_to_move(out):
        move = oct(out)[2:]
        move = move.rjust(4, "0")
        n1 = chr(int(move[0]) + ord('a'))
        n2 = int(move[1]) + 1
        n3 = chr(int(move[2]) + ord('a'))
        n4 = int(move[3]) + 1
        return f"{n1}{n2}{n3}{n4}"


class GameRow:
    def __init__(self, row):
        assert(len(row) == 8)

        self.counter = row[0]
        self.last_fen = row[1]
        self.last_move = row[2]
        self.score = row[3]
        self.white_elo = row[4]
        self.black_elo = row[5]
        self.turn = row[6]
        self.clock = row[7]

    @staticmethod
    def input_array(board_fen):
        game = chess.Board(fen=board_fen)
        image = str(game)

        pawn = lambda x: 1 if x == "P" else (-1 if x == "p" else 0)
        knight = lambda x: 1 if x == "N" else (-1 if x == "n" else 0)
        bishop = lambda x: 1 if x == "B" else (-1 if x == "b" else 0)
        rook = lambda x: 1 if x == "R" else (-1 if x == "r" else 0)
        queen = lambda x: 1 if x == "Q" else (-1 if x == "Q" else 0)
        king = lambda x: 1 if x == "K" else (-1 if x == "k" else 0)

        rows = image.splitlines()
        rows = [[[pawn(x), knight(x), bishop(x), rook(x), queen(x), king(x)]
                 for x in row if x != " "]
                 for row in rows]

        """
        pawns = [list(map(lambda x: 1 if x == "P" else (-1 if x == "p" else 0), row)) for row in rows]
        knights = [list(map(lambda x: 1 if x == "N" else (-1 if x == "n" else 0), row)) for row in rows]
        bishops = [list(map(lambda x: 1 if x == "B" else (-1 if x == "b" else 0), row)) for row in rows]
        rooks = [list(map(lambda x: 1 if x == "R" else (-1 if x == "r" else 0), row)) for row in rows]
        queens = [list(map(lambda x: 1 if x == "Q" else (-1 if x == "q" else 0), row)) for row in rows]
        kings = [list(map(lambda x: 1 if x == "K" else (-1 if x == "k" else 0), row)) for row in rows]
        """

        #arr = np.array([pawns, knights, bishops, rooks, queens, kings])
        arr = np.array(rows)
        return arr

def load_data():
    games = []
    with open("reduced-47k.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            games.append(GameRow(row))
    return games

games = load_data()

input_set = np.array([GameRow.input_array(x.last_fen) for x in games])
label_set = np.array([Chess.move_to_output(x.last_move) for x in games])


NUM_TRAINING = int(len(input_set) * 0.8)
training_input = input_set[:NUM_TRAINING]
training_label = label_set[:NUM_TRAINING]

test_input = input_set[NUM_TRAINING:]
test_label = label_set[NUM_TRAINING:]

model = models.Sequential()

USE_CNN = True

if USE_CNN:
    model.add(layers.Conv2D(filters=200, kernel_size=(4,4), activation='relu', input_shape=(8,8,6), padding="same"))
    #model.add(layers.Conv2D(filters=200, kernel_size=(4,4), activation='relu', input_shape=(6,8,8), padding="same"))
    #model.add(layers.MaxPooling2D(pool_size=(2,2)))
    model.add(layers.Dropout(0.3))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(filters=50, kernel_size=(3,3), activation='relu', padding="same"))
    model.add(layers.Dropout(0.3))
    model.add(layers.BatchNormalization())

    model.add(layers.Flatten())
    model.add(layers.Dense(4096, activation='softmax'))

else:
    model.add(layers.Dense(64, activation='relu', input_shape=(8,8,6)))
    model.add(layers.Dropout(0.2))
    model.add(layers.BatchNormalization())
    model.add(layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01), bias_regularizer=regularizers.l2(0.01)))
    model.add(layers.Dropout(0.2))
    model.add(layers.BatchNormalization())
    model.add(layers.Flatten())
    model.add(layers.Dense(4096, activation='softmax'))

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
              metrics=['accuracy'])

history = model.fit(training_input, training_label, epochs=10,
                    validation_data=(test_input, test_label))

def legal_moves(fen):
    board = chess.Board(fen)
    return map(str, board.legal_moves)

def predict_blunder(fen):
    x = GameRow.input_array(fen)
    pred = model.predict(np.array([x]))[0]
    raw_winner = np.argmax(pred)

    outputs = map(Chess.move_to_output, legal_moves(fen))
    max_i, max_v = -1, -99999
    for i in outputs:
        v = pred[i]
        if v > max_v:
            max_i = i
            max_v = v
    return Chess.output_to_move(max_i), max_v, Chess.output_to_move(raw_winner), pred[raw_winner]

predict_blunder("3rr1k1/1pq2pp1/pbp4p/4N3/1P1PbB1P/6P1/1P1Q1P2/3R1RK1 b - - 4 24")
