# chesstime
MMDS project with lichess database

### Dataset

I decided to pivot to a different direction. I wanted to answer the following question: Given a board state, what is the most likely blunder a player will make? I do not want the best move, nor the most human correct move, I'm concerned only with the most human blunder.
With this in mind I analyzed games with Stockfish to find the first big blunder in a game (evaluation change by 300 centipawns)
I downloaded games played on lichess during the month of November. This turned out to be 154GB uncompressed, which is a monstrosity to work with. Of this I pulled 100k "Rated Blitz" games (games where the time format is typically 3 to 5 minutes per side) where both players were within [1000,2000) elo range. I also only look at the first 30 moves to avoid extremely complicated positions and endgames.
The first thing I noticed with the data was just how prevalent intentionally losing was, whether to inflate a friend's rating or lower their own to face easier competition. With this in mind I ignore games that took less than 6 moves to complete. (Unfortunately this means we can't demonstrate scholar's mate.)
Stockfish analysis was certainly the most painful part of this project, as I had to re-run the process multiple times fixing things one at a time. I did not catch some bugs until very late as I thought my training setup was bad or could be improved.

### Model

Its not immediately obvious how to go around representing input/output for this problem. I initially decided to represent each piece as a number evenly spaced between 0 and 1, and fed the model a 2 dimensional grid (8,8,1). After consulting Jaime I changed this to 6 8x8 arrays, one for each piece. A value of 1 would indicate a white piece present, -1 for a black piece, and 0 for nothing. The shape of my input is then (6,8,8).
I then changed it once again, this time to (8,8,6). An 8x8 array with each element being an array representing the pieces.
The output is a move. There are 64 squares on a chess board, so there are about (64^2) = 4096 possible moves.

I decided to test the effectiveness of CNN and MLP. For both of these models I attempted countless permutations of filters and layers. Before fixing my bug with stockfish analysis I achieved 12% accuracy with 46k games and 14% with 92k games. These weren't amazing, but the nature of the problem makes it impossible to have a high accuracy. I do not expect that anything close to 40% is possible, with 30% sounding like a more reasonable figure for something close to perfect.

MLP
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
dense_124 (Dense)            (None, 8, 8, 64)          448
_________________________________________________________________
dropout_82 (Dropout)         (None, 8, 8, 64)          0
_________________________________________________________________
batch_normalization_80 (Batc (None, 8, 8, 64)          256
_________________________________________________________________
dense_125 (Dense)            (None, 8, 8, 64)          4160
_________________________________________________________________
dropout_83 (Dropout)         (None, 8, 8, 64)          0
_________________________________________________________________
batch_normalization_81 (Batc (None, 8, 8, 64)          256
_________________________________________________________________
flatten_41 (Flatten)         (None, 4096)              0
_________________________________________________________________
dense_126 (Dense)            (None, 4096)              16781312
=================================================================
Total params: 16,786,432
Trainable params: 16,786,176
Non-trainable params: 256
_________________________________________________________________
```


CNN
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
conv2d_80 (Conv2D)           (None, 8, 8, 200)         19400
_________________________________________________________________
dropout_81 (Dropout)         (None, 8, 8, 200)         0
_________________________________________________________________
batch_normalization_81 (Batc (None, 8, 8, 200)         800
_________________________________________________________________
conv2d_81 (Conv2D)           (None, 8, 8, 50)          90050
_________________________________________________________________
dropout_82 (Dropout)         (None, 8, 8, 50)          0
_________________________________________________________________
batch_normalization_82 (Batc (None, 8, 8, 50)          200
_________________________________________________________________
flatten_41 (Flatten)         (None, 3200)              0
_________________________________________________________________
dense_43 (Dense)             (None, 4096)              13111296
=================================================================
Total params: 13,221,746
Trainable params: 13,221,246
Non-trainable params: 500
_________________________________________________________________
```

MLP won out over CNN with far better accuracy with the initial (flawed) training data. However, once I fixed the bug the two were difficult to distinguish from train/test results. Fortunately with k-fold validation we can conclude that CNN performs better. Running 10-fold validation on the two models gave us a 7.2% average for MLP and 7.4% for CNN. It also has slightly fewer trainable parameters.

The model is capable of 7% accuracy with 47k games. It is very clearly overfitting, as validation loss increases with epoch and nothing I do changes that. However that initial disappointment may be a good thing: The overfitting is because the sample size needs to be a lot larger, but the model has potential.

### Onward

While currently lackluster due to the small accuracy, I believe there is potential. We are trying to predict common blunders, so our output size is not actually 4096 but typically smaller than 20. This helps us cheat a little, but is no comparison to a larger dataset. I did not have time to collect more data, but I would be interested in seeing the effectiveness with, say, 1M games.
This would take several weeks to preprocess with stockfish, but the results combined with pruning of non-legal moves would certainly provide something believable.

For someone not amazing at chess, engine analysis is often nonsensical. If I were to look over my games with stockfish, it would tell me the best moves with no explanation, and I would have to figure out why 24 moves later my position is slightly better than with the move I played.
An alternative is a blunder engine: for each position, a neural net could tell you the most likely blunder at a position. This may be the move you instictively wanted to play, and can help improve your game if you see not only the best continuation but also some natural looking bad ones.
This would be hosted on a website complete with stockfish evaluations and a slick interface for navigating the game. The stockfish evaluations can be done with web assembly as lichess does, so our server cost would only be for the webserver and running predictions once the model is trained.
We could, with a thick enough wallet, download the lichess database monthly, analyze every blitz game, and retrain the model with additional data. We would store the model on a simple webserver where users can connect, put in the PGN for the game they just played, and go through it. We could sustain with ads, or train yet another model, reduce the parameters and offer it as a free tier with a paid subscription to the premium model.
