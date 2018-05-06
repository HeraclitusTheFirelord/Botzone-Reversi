'''
黑白棋（Reversi）
作者：ljzh
策略：alpha-beta剪枝
游戏信息：http://www.botzone.org/games#Reversi
'''
import json
import numpy
import random
import datetime

# 3个对手
# AlphaBeta样例AI（ID=5a5b2587fe46681ed452af8e）
# 简单的MCTSAI（ID=5a9bf32bed7b6b4cf832a3ea）
# 估值经过调优的AlphaBetaAI（ID=568a8f1aab52a4573d07a45b）

# 参数
# 最大值与最小值
MAXSCORE = 10000000
MINSCORE = -10000000
# 占点分数
BOARDSCORE = [
[500, 1, 15, 10, 10, 15, 1, 500],
[  1, 0,  2,  2,  2,  2, 0,   1],
[ 15, 2,  2,  2,  2,  2, 2,  15],
[ 10, 2,  2,  5,  5,  2, 2,  10],
[ 10, 2,  2,  5,  5,  2, 2,  10],
[ 15, 2,  2,  2,  2,  2, 2,  15],
[  1, 0,  2,  2,  2,  2, 0,   1],
[500, 1, 15, 10, 10, 15, 1, 500]]
# 下棋位置，按照分数从大到小排序，不包括有子的位置。在主代码中初始化
BOARDDICT = dict()
BOARDLIST = []
# 边缘点分数
FRONTIERSCORE = -5
# 行动力分数
MOVESCORE = 10
USINGOTHERSCORE = True #最后15个点只使用boardscore
# 算法层数
LAYER = 5
# 空位数
REMAIN = 63
# 时间是否已到
TIMELIMIT = 5.8
TIMECHECK = False

# 求时间
def CheckTime():
    global TIMECHECK
    if TIMECHECK:
        return True
    time = datetime.datetime.now()
    passTime = time - startTime
    timePassed = passTime.seconds + passTime.microseconds / 1000000
    if timePassed > TIMELIMIT:
        TIMECHECK = True
        return True
    return False

# 求对局双方边缘点个数之差
def GetFrontierDiffer(board, color):
    boardWithEdge = numpy.zeros((10, 10), dtype=numpy.int)
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                boardWithEdge[i+2][j+1] = 1
                boardWithEdge[i+1][j+2] = 1
                boardWithEdge[i][j+1] = 1
                boardWithEdge[i+1][j] = 1
    differ = 0
    for i in range(8):
        for j in range(8):
            if boardWithEdge[i+1][j+1] == 1:
                differ += board[i][j]
    return differ * color

# 看看谁赢了
def Winner(board):
    colorScore = 0
    for i in range(8):
        for j in range(8):
            colorScore += board[i][j]
    if colorScore == 0:
        return 0
    return colorScore / abs(colorScore)

# 估值
def EstimateValue(board, color):
    # 计算占点分数
    boardScore = 0
    for i in range(8):
        for j in range(8):
            boardScore += board[i][j] * BOARDSCORE[i][j]
    boardScore *= color
    # 计算行动力分数和边缘点分数
    moveScore = 0
    frontierScore = 0
    if USINGOTHERSCORE:
        #moveScore = (FindPlaceLen(board, color) - FindPlaceLen(board, -color)) * MOVESCORE
        frontierScore = GetFrontierDiffer(board, color) * FRONTIERSCORE
        pass
    return (boardScore + moveScore + frontierScore)

# alpha-beta剪枝
def GetValue(board, layer, alpha, beta, color, remain):
    if remain == 0:
        return Winner(board) * color * (MAXSCORE-1)
    if layer == 0:
        return EstimateValue(board, color)
    moves = 0
    v = MINSCORE
    newBoard = board.copy()
    for item in BOARDLIST:
        x = item[0][0]
        y = item[0][1]
        if board[x][y] == 0:
            #newBoard = board.copy()
             if Place(newBoard, x, y, color):
                moves += 1
                nextV = -GetValue(newBoard, layer-1, -beta, -max(alpha, v), -color, remain-1)
                # 时间到了！！！
                if CheckTime():
                    break
                v = max(v, nextV)
                if v > beta:
                    return v
                newBoard = board.copy()
    if moves == 0:
        # color方无棋可下，检查-color方是否有棋可下
        if FindPlaceLen(board, -color) != 0:
            return -GetValue(newBoard, layer, -beta, -alpha, -color, remain)
        else:
            return Winner(board) * color * (MAXSCORE-1)
    return v

DIR = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)) # 方向向量
# 放置棋子，计算新局面，注意如果该位置无效的话board不会改变
def Place(board, x, y, color):
    if x < 0:
        return False
    valid = False
    for d in range(8):
        xStep, yStep = DIR[d][0], DIR[d][1]
        i = x + xStep
        j = y + yStep
        while 0 <= i and i < 8 and 0 <= j and j < 8 and board[i][j] == -color:
            i += xStep
            j += yStep
        if 0 <= i and i < 8 and 0 <= j and j < 8 and board[i][j] == color:
            while True:
                i -= xStep
                j -= yStep
                if i == x and j == y:
                    break
                valid = True
                board[i][j] = color
    if valid == True:
        board[x][y] = color
    return valid

# 求可移动步的个数（行动力）
def FindPlaceLen(board, color):
    moves = 0
    newBoard = board.copy()
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                #newBoard = board.copy()
                if Place(newBoard, i, j, color):
                    moves += 1
                    newBoard = board.copy()
    return moves

# 求可移动步
def FindPlace(board, color):
    moves = []
    newBoard = board.copy()
    for item in BOARDLIST:
        x = item[0][0]
        y = item[0][1]
        if board[x][y] == 0:
            #newBoard = board.copy()
            if Place(newBoard, x, y, color):
                moves.append((x, y))
                newBoard = board.copy()
    return moves

# 求棋盘空余位置的个数
def GetRemain(board):
    remain = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                remain += 1
    return remain

# 使用Alpha-Beta剪枝产生策略
def AlphaBetaPlace(board, color, layer):
    moves = FindPlace(board, color)
    if len(moves) == 0:
        return -1, -1
    
    # heuristic searching
    shallowLayer = min(layer // 3, 5)
    heuristicDict = dict()
    for step in moves:
        newBoard = board.copy()
        Place(newBoard, step[0], step[1], color)
        v = -GetValue(newBoard, shallowLayer, MINSCORE, MAXSCORE, -color, REMAIN-1)
        if CheckTime():
            return -1, -1
        key = (step[0], step[1])
        heuristicDict[key] = v
    heuristicMoves = sorted(heuristicDict.items(), key=lambda d:d[1], reverse = True)
    moves = []
    for item in heuristicMoves:
        moves.append((item[0][0], item[0][1]))

    bestv = MINSCORE
    bestx, besty = -1, -1
    for step in moves:
        newBoard = board.copy()
        Place(newBoard, step[0], step[1], color)
        v = -GetValue(newBoard, layer, MINSCORE, -bestv, -color, REMAIN-1)
        if CheckTime():
            if bestx == -1:
                bestx, besty = step[0], step[1]
            break
        if v > bestv:
            bestv = v
            bestx, besty = step[0], step[1]
    return bestx, besty

# 随机产生决策
def RandPlace(board, color):
    moves = FindPlace(board, color)
    if len(moves) == 0:
        return -1, -1
    return random.choice(moves)

# 处理输入，还原棋盘
def InitBoard():
    #fullInput = json.loads(input())
    fullInput = json.loads('{"requests":[{"x":-1,"y":-1},{"x":5,"y":3},{"x":3,"y":1},{"x":5,"y":5},{"x":6,"y":2},{"x":3,"y":2},{"x":6,"y":5}],"responses":[{"y":4,"x":5},{"y":2,"x":4},{"x":5,"y":2},{"x":4,"y":1},{"y":0,"x":2},{"x":5,"y":6}]}')
    requests = fullInput["requests"]
    responses = fullInput["responses"]
    if "time_limit" in fullInput:
        limitTime = fullInput["time_limit"]
    else:
        limitTime = 0
    if "data" in fullInput:
        layer = fullInput["data"]
    else:
        layer = ""
    board = numpy.zeros((8, 8), dtype=numpy.int)
    board[3][4] = board[4][3] = 1
    board[3][3] = board[4][4] = -1
    myColor = 1
    if requests[0]["x"] >= 0:
        myColor = -1
        Place(board, requests[0]["x"], requests[0]["y"], -myColor)
    turn = len(responses)
    for i in range(turn):
        Place(board, responses[i]["x"], responses[i]["y"], myColor)
        Place(board, requests[i + 1]["x"], requests[i + 1]["y"], -myColor)
    return board, myColor, limitTime, layer

# 初始化棋盘
startTime = datetime.datetime.now()
board, myColor, limitTime, layer = InitBoard()
'''
for i in range(8):
    for j in range(8):
        if board[i][j] == 0: 
            print('.',end=' ')
        elif board[i][j] == -myColor:
            print('&',end=' ')
        else:
            print('o',end=' ')
    print()
print((FindPlaceLen(board, myColor) - FindPlaceLen(board, -myColor)))
print(GetFrontierDiffer(board, myColor))
'''
# 初始化全局变量
if layer != "":
    pass#LAYER = int(layer)
REMAIN = GetRemain(board)
if REMAIN < 14:
    USINGOTHERSCORE = False
for i in range(8):
    for j in range(8):
        if board[i][j] == 0:
            key = (i, j)
            value = BOARDSCORE[i][j]
            BOARDDICT[key] = value
BOARDLIST = sorted(BOARDDICT.items(), key=lambda d:d[1], reverse = True)
# 下棋
if limitTime == 0:
    startTime = datetime.datetime.now()
x, y = AlphaBetaPlace(board, myColor, LAYER)
# 计算下一次下棋时选多少层
endTime = datetime.datetime.now()
passTime = endTime - startTime
timePassed = passTime.seconds + passTime.microseconds / 1000000
nextlayer = LAYER
if timePassed < 0.05:
    nextlayer = LAYER + 3
elif timePassed < 0.2:
    nextlayer = LAYER + 2
elif timePassed < 1:
    nextlayer = LAYER + 1
elif timePassed > 5:
    nextlayer = LAYER - 1
if REMAIN < 15:
    nextlayer += 1
nextlayer = max(nextlayer, 3)
# 时间有剩，试试多一层
if not CheckTime():
    tryLayer = LAYER + 1
    while tryLayer < REMAIN:
        tx, ty = AlphaBetaPlace(board, myColor, tryLayer)
        if CheckTime():
            break
        x, y = tx, ty
        LAYER = tryLayer
        tryLayer += 1
# 输出
print(json.dumps({"response": {"x": x, "y": y}, "data" : nextlayer, "debug": {"layer": LAYER ,"timePassed": timePassed}}))
