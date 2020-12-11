# chesstime
MMDS project with lichess database

### WIP

This project aims to figure out when players at different skill levels blunder. However as my dataset does not contain blunder information, I will have to use stockfish to parse every game that I want to analyze. Hardware/time limitations may require I use weaker stockfish settings, so I will likely eliminate games with players above a certain rating (maybe 2200) so as to minimize misclassifications where a weak engine thinks a strong long-term move is a blunder.

The dataset comes from database.lichess.org. I am currently only using 2020-11, which is 154gb uncompressed.

After evaluating games to find the first blunder (with criteria: evaluation difference between two moves >2), I will train a neural network on the games. I will then be able to predict, based on elo of the two players as well as the opening played, which move the first blunder will occur on.
Doing this for common lines of play may be useful in determining how much preparation is needed to play a new opening well, or to quickly find tricky lines that lead to an easy win against an unsuspecting opponent.

Code to read data and analyze with stockfish is in src/main.ipynb.

Sample:
|    | White           | Black             |   WhiteElo |   BlackElo | Result   | UTCDate    | UTCStart   | UTCEnd   |   FirstBlunder |
|---:|:----------------|:------------------|-----------:|-----------:|:---------|:-----------|:-----------|:---------|---------------:|
|  0 | bernec          | glebmai           |       1770 |       1858 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |              6 |
|  1 | paranakulmichel | LordMorpheus      |       1964 |       1798 | 1-0      | 2020.11.01 | 00:00:00   | 00:00:00 |              8 |
|  2 | eli9A           | PedroSachica      |       1519 |       1864 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |             28 |
|  3 | mini10201       | jrdh11            |       1957 |       1211 | 1-0      | 2020.11.01 | 00:00:00   | 00:00:00 |             13 |
|  4 | Pevojed         | luisulloa         |       1305 |       1976 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |             22 |
|  5 | rosaliogomez    | Dennis_Vasquez    |       1985 |       1331 | 1-0      | 2020.11.01 | 00:00:00   | 00:00:00 |              1 |
|  6 | Ares-Michael    | chessnaturaleza   |       1344 |       1988 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |              0 |
|  7 | KEERT7          | reyrajam_2008     |       2009 |       1500 | 1-0      | 2020.11.01 | 00:00:00   | 00:00:00 |              1 |
|  8 | DelaCruz007     | matiasgGM         |       1750 |       2053 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |              5 |
|  9 | DiableRouge_2   | MecanismoAlterado |       2042 |       1725 | 0-1      | 2020.11.01 | 00:00:00   | 00:00:00 |              0 |
