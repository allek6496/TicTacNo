from tkinter import Tk, Canvas
from time import sleep
from random import randint
from math import inf
root = Tk()
screenWidth = 800
screenHeight = 800
screen = Canvas(root, width = screenWidth, height = screenHeight, background = "#616161")

class game:
    
    def __init__(self, X=3, Y=3, quantum=True, effects=0):
        self.X = X
        self.Y = Y
        self.width = screenWidth/X
        self.height = screenHeight/Y
        self.quantum = quantum
        self.effects = effects
        self.board = self.generateBoard()
        self.currMove = self.generateBoard()
        self.moves = []
        self.moveLeft = 100
        self.turn = "X"
        self.placeIncrement = 5
        self.scrollThreshold = 2
        self.scrollTotal = 0
        self.measured = False
        
    #draw fancy effects behind board and stuff
    def drawEffects(self):
        pass

    def generateBoard(self):
        newBoard = []
        for x in range(self.X):
            newBoard.append([])
            for y in range(self.Y):
                newBoard[-1].append(0)
        return newBoard

    #draws the board on the screen
    def draw(self):
        global dump
        
        self.drawEffects()

        #horizontal lines
        for i in range(1, self.X):
            dump.append(screen.create_line(i*self.width, 0, i*self.width, screenHeight, width=2))
        
        #vertical lines
        for i in range(1, self.Y):
            dump.append(screen.create_line(0, i*self.height, screenWidth, i*self.height, width=2))

        #fills in the info for each square
        for x in range(self.X):
            for y in range(self.Y):
                if self.board[x][y] != 0:
                    dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=self.board[x][y], font="Arial 200", fill="#ab000d" if self.board[x][y]=="X" else "#001970"))

                if self.currMove[x][y] != 0:
                    dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=str(self.currMove[x][y]/100), anchor="n", font="Arial 64", fill="#b71c1c" if self.turn=="X" else "#1a237e"))

                for j in range(len(self.moves)):
                    current = self.moves[j][x][y]
                    if current != 0:
                        if self.moves[j][-1] == 'X':
                            # textSize(16);
                            # textAlign(LEFT, TOP);
                            # text(moves[i][j]/100, j%3*200+10, int(j/3)*200 + 10+ 10*i)
                            dump.append(screen.create_text(x*self.width + 10, y*self.height + (j+1)*10, text=str(int(current)/100), anchor="nw", font="Arial 16", fill="#7f0000"))
                        else:
                            # textSize(16);
                            # textAlign(RIGHT, TOP);
                            # text(moves[i][j]/100, j%3*200+190, int(j/3)*200 + 10 + 10*i)
                            dump.append(screen.create_text(x*self.width + 190, y*self.height + (j+1)*10, text=str(int(current)/100), anchor="ne", font="Arial 16", fill="#000051"))

        dump.append(screen.create_text(mouseX, mouseY, text=str(self.moveLeft/100), anchor="ne", font= " Arial 32", fill="#b71c1c" if self.turn=="X" else "#1a237e"))

    #gets which square the mouse is in 
    def getCurrSquare(self):
        x = mouseX // self.width
        y = mouseY // self.height
        
        return [int(x), int(y)]

    #returns how full a given square is. This means all the previous additions are summed, not counting anything for the current turn
    def getSquare(self, x, y):
        if self.board[x][y] != 0:
            return 100

        total = self.currMove[x][y]

        for turn in self.moves:
            total += turn[x][y]

        return total

    # def fix(self, turn):
    #     for x in range(self.X):
    #         for y in range(self.Y):
    #             for t in range(len(self.moves)):
    #                 if self.moves[turn][x][y] == 100:
    #                     if t != turn:
    #                         self.change(t, x, y, 0)
    #                         break
    #             else:
    #                 if self.getSquare(x, y) > 100:
    #                     A = self.moves[turn][x][y]
    #                     a = []

    #                     for t in range(len(self.moves)):
    #                         if t != turn:
    #                             a.append(self.moves[t][x][y])

    #                     S = sum(a)
    #                     try:
    #                         delta = (100-A)/S
    #                     except ZeroDivisionError:
    #                         delta = 0

    #                     for t in range(len(self.moves)):
    #                         if t != turn:
    #                             self.change(t, x, y, self.moves[t][x][y]*delta)

    def resolve(self, t, x, y, found):
        if found:
            self.board[x][y] = self.moves[t][-1]

            self.moves.pop(t)

            for turn in range(len(self.moves)):
                self.resolve(turn, x, y, False)
        else:
            A = self.moves[t][x][y]
            self.moves[t][x][y] = 0

            S = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    S += self.moves[t][X][Y]

            delta = 100 / S

            for X in range(self.X):
                for Y in range(self.Y):
                    if self.moves[t][X][Y] != 0:
                        self.changeSquare(t, X, Y, self.moves[t][X][Y]*delta)

    def changeSquare(self, t, x, y, newVal):
        self.moves[t][x][y] = newVal

        S = self.getSquare(x, y)
        if S > 100:
            delta = (100 - newVal) / (S - newVal)

            for turn in range(len(self.moves)):
                if turn != t:
                    self.changeMove(turn, x, y, self.moves[turn][x][y]*delta)

    def changeMove(self, t, x, y, newVal):
        self.moves[t][x][y] = newVal

        S = 0
        for X in range(self.X):
            for Y in range(self.Y):
                S += self.moves[t][X][Y]
        
        if int(S*10000)/10000 != 100:
            delta = (100 - newVal) / (S - newVal)

            for X in range(self.X):
                for Y in range(self.Y):
                    if not(X == x and Y == y):
                        self.changeSquare(t, X, Y, self.moves[t][X][Y]*delta)

    #set a specific number to 0 while keeping the rest of the move the same

    # def changed(self, t, x, y):
    #     queue = [(t, x, y)]
    #     done = []
        
    #     while len(queue) > 0:
    #         print(queue)
    #         print(self.moves, end="\n")
            
    #         if queue[0] in done:
    #             queue.pop(0)
    #             continue
            
    #         t = queue[0][0]
    #         x = queue[0][1]
    #         y = queue[0][2]
    #         A = self.moves[t][x][y]

    #         done.append(queue.pop(0))

    #         #square
    #         S = 0
    #         for turn in range(len(self.moves)):
    #             if turn != t:
    #                 S += self.moves[turn][x][y]

    #         try:
    #             delta = (100 - A) / S
    #         except ZeroDivisionError:
    #             delta = 0

    #         if S + A > 100:
    #             for turn in range(len(self.moves)):
    #                 if turn != t and self.moves[turn][x][y] != 0:
    #                     self.moves[turn][x][y] *= delta
                        
    #                     new = (turn, x, y)
    #                     if new not in queue:
    #                         queue.append(new)

    #         #move:
    #         S = 0
    #         for X in range(self.X):
    #             for Y in range(self.Y):
    #                 if not(X == x and Y == y):
    #                     S += self.moves[t][X][Y]

    #         try:
    #             delta = (100 - A) / S
    #         except ZeroDivisionError:
    #             delta = 0

    #         if S + A != 100:
    #             for X in range(self.X):
    #                 for Y in range(self.Y):
    #                     if not (X == x and Y == y) and self.moves[turn][x][y] != 0:
    #                         self.moves[turn][x][y] *= delta

    #                         new = (t, X, Y)
    #                         if new not in queue:
    #                             queue.append(new)


    #queue is like [(t, x, y, prev), ...]
    # def fix(self, resolved, queued):
    #     queue = queued[:]
    #     done = resolved[:]
    #     if len(queue) == 0:
    #         return
    #     if queue[0] in resolved:
    #         queue.pop(0)
    #         self.fix(done, queue)
    #         return

    #     print(queue)
    #     print(self.moves)
    #     print()
    #     t = queue[0][0]
    #     x = queue[0][1]
    #     y = queue[0][2]
    #     newVal = self.moves[t][x][y]

    #     A = queue[0][3]
    #     self.moves[t][x][y] = newVal

    #     if A == newVal:
    #         done.append(queue.pop(0))
    #         self.fix(done, queue)
    #         return
        
    #     done.append(queue.pop(0))

    #     #square
    #     S = 0
    #     for turn in range(len(self.moves)):
    #         S += self.moves[turn][x][y]

    #     try:    
    #         delta = (100 - newVal) / (S - A)
    #     except ZeroDivisionError:
    #         delta = 0
        
    #     if S - A + newVal > 100:
    #         for turn in range(len(self.moves)):
    #             if turn != t and self.moves[turn][x][y] != 0:
    #                 queue.append((turn, x, y, self.moves[turn][x][y]))
    #                 self.moves[turn][x][y] = self.moves[turn][x][y]*delta

    #     #move
    #     S = 0
    #     for X in range(self.X):
    #         for Y in range(self.Y):
    #             S += self.moves[t][X][Y]

    #     try:    
    #         delta = (100 - newVal) / (S - A)
    #     except ZeroDivisionError:
    #         delta = 0

    #     if S - A + newVal != 100:
    #         for X in range(self.X):
    #             for Y in range(self.Y):
    #                 if not(X == x and Y == y) and self.moves[t][X][Y] != 0:
    #                     queue.append((turn, X, Y, self.moves[turn][X][Y]))
    #                     self.moves[turn][X][Y] = self.moves[turn][X][Y]*delta

    #     self.fix(done, queue)

    # def change(self, t, x, y, newVal, square = False, move = False):
    #     try:
    #         A = self.moves[t][x][y]
    #     except IndexError:
    #         return 

    #     if A == newVal:
    #         return

    #     # if newVal > 100:
    #     #     newVal = 100

    #     self.moves[t][x][y] = newVal
    #     # done.append((t, x, y))

    #     if move:
    #         S = 0
    #         for X in range(self.X):
    #             for Y in range(self.Y):
    #                 S += self.moves[t][X][Y]

    #         if S != 100:
    #             # print(S)
    #             try:    
    #                 delta = (100 - newVal) / (100 - A)
    #             except ZeroDivisionError:
    #                 delta = 0
            
    #             for X in range(3):
    #                 for Y in range(3):
    #                     if not (X == x and Y == y):
    #                         # print(self.moves[t][X][Y], delta, end='\n')
    #                         self.change(t, X, Y, self.moves[t][X][Y]*delta, square = True)
    #                         # print(self.moves[t][X][Y])

    #     if square:
    #         S = 0
    #         for turn in range(len(self.moves)):
    #             S += self.moves[turn][x][y]

    #         if S != S - newVal + A:
    #             try:
    #                 delta = (S - newVal + A - newVal) / (S - newVal)
    #             except ZeroDivisionError:
    #                 delta = 0

    #             for turn in range(len(self.moves)):
    #                 if turn != t:
    #                     self.change(turn, x, y, self.moves[turn][x][y]*delta, move = True)

        # print("im good")

        # print(moves, '\n')
        
    # def change(self, t, x, y, newVal):  
    #     current = self.getSquare(x, y)
    #     A = self.moves[t][x][y]

    #     if current - A + newVal <= 100:
    #         self.moves[t][x][y] = newVal
    #     else:
    #         delta = (100 - newVal)/(current - A)

    #         for turn in range(len(self.moves)):
    #             if turn != t:
    #                 self.change(turn, x, y, self.moves[turn][x][y]*delta)
            
    #         otherSum = 0

    #         for X in range(self.X):
    #             for Y in range(self.Y):
    #                 if not(X == x and Y == y):
    #                     otherSum += self.moves[t][X][Y]

    #         otherDelta = (100 - newVal)/otherSum

    #         for X in range(self.X):
    #             for Y in range(self.Y):
    #                 if  not(X == x and Y == y):
    #                     self.change(t, X, Y, self.moves[t][X][Y]*otherDelta)

    #         self.moves[t][x][y] = newVal

        # a = []
        # for X in range(self.X):
        #     a += self.moves[t][X]

        # a.pop(x*self.X + y)

        # # print(b)
        # S = sum(a)

        # try:
        #     R = (S + self.moves[t][x][y] - newVal)/S
        # except ZeroDivisionError:
        #     R = 0
        #     print(self.moves)

        # for X in range(self.X):
        #     for Y in range(self.Y):
        #         if not(X == x and Y == y):
        #             # self.moves[t][X][Y] *= R
        #             self.change(t, X, Y, self.moves[t][X][Y]*R)

        # self.moves[t][x][y] = newVal

        # # self.fix(t)

    #To be run every frame
    def update(self):
        global scrollD

        resolved = []
        for t in range(len(self.moves)):
            for x in range(self.X):
                for y in range(self.Y):
                    if round(self.moves[t][x][y]) == 100:
                        self.board[x][y] = self.moves[t][-1]
                        resolved.append(t)
        
        for turn in sorted(resolved, reverse=True):
            self.moves.pop(turn)

        # print(self.currMove)

        delta = False
        if "Up" in keysPressed:
            delta = self.placeIncrement
        elif "Down" in keysPressed:
            delta = -1*self.placeIncrement

        if scrollD != 0 or delta:
            self.scrollTotal += scrollD
            if abs(self.scrollTotal) >= self.scrollThreshold or delta:
                if not delta:
                    self.scrollTotal = 0
                    delta = scrollD//abs(scrollD)*self.placeIncrement
                currSquare = self.getCurrSquare()
                x = currSquare[0]
                y = currSquare[1]

                if 0 <= x < self.X and 0 <= y < self.Y:
                    if self.currMove[x][y] + delta >= 0 and 0 <= self.getSquare(x, y) + delta <= 100:
                        self.moveLeft -= delta
                        self.currMove[x][y] += delta

                        if self.moveLeft < 0:
                            self.currMove[x][y] -= delta
                            self.moveLeft = 0
                        elif self.moveLeft > 100:
                            self.currMove[x][y] -= delta
                            self.moveLeft = 100
        
        if "Return" in keysPressed and self.moveLeft == 0:
            self.moves.append(self.currMove + [self.turn])
            self.turn = 'O' if self.turn == 'X' else 'X'
            self.currMove = self.generateBoard()
            self.moveLeft = 100
            self.measured = False

        if clicked and self.moveLeft == 100 and not self.measured:
            currSquare = self.getCurrSquare()
            x = currSquare[0]
            y = currSquare[1]

            if self.getSquare(x, y) > 0:
                self.measured = True
                die = randint(0, 100)
                # picked = None
                for turn in range(len(self.moves)):
                    try:
                        die -= self.moves[turn][x][y]
                    except IndexError:
                        continue            
                    # self.moves[turn][x][y] = 0

                    # self.change(turn, x, y, 0)

                    if die < 0:
                        die = 1000000
                        self.resolve(turn, x, y, True)
                    else:
                        self.resolve(turn, x, y, False)

                # if picked:
                #     self.moves.pop(picked)

        self.draw()

def setInitialValues(): 
    global mouseX, mouseY, scrollD, running, page, size, sizes, clicked, board, dump, keysPressed
    keysPressed = []
    dump = []
    clicked = False
    running = True
    mouseX = 0
    mouseY = 0
    scrollD = 0
    page = 0
    size = None
    board = None
    sizes = [["3 X 3", 10, 10, 395, 95], ["4 X 4", 405, 10, 790, 95]]

def cleanup():
    global dump

    screen.delete(*dump)
    dump = []

def afterUpdates():
    global scrollD, keysPressed, clicked
    
    clicked = False
    scrollD = 0
    keysPressed = []

def changePage(newPage):
    global page

    screen.delete("all")
    page = newPage

def sizeSelect(): #screen 1
    global page
    changePage("selection")

    for button in sizes:
        screen.create_rectangle(button[1], button[2], button[3], button[4], outline = "", fill="#00cbcc")
        screen.create_text((button[1]+button[3])/2, (button[2]+button[4])/2, text=button[0], font="Arial 64", fill="black")

def runGame():
    global board, page, clicked, scrollD
    setInitialValues()

    sizeSelect()

    while running:
        if page == "selection":
            for button in sizes:
                if button[1] < mouseX < button[3] and button[2] < mouseY < button[4] and clicked:
                    board = game(X=int(button[0][0]), Y=int(button[0][-1]))
                    changePage("PVP")

        if page == "PVP":
            board.update()

        afterUpdates()

        screen.update()
        sleep(0.03)
        cleanup()

def mouseMove(event):
    global mouseX, mouseY
    mouseX = event.x
    mouseY = event.y
    
def scrollWheel(event):
    global scrollD
    scrollD = event.delta/100
    # print(scrollD)

def buttonPress(event):
    global scrollD, keysPressed

    keysPressed.append(event.keysym)
    # print(event.keysym)

def mouseClick(event):
    global mouseX, mouseY, clicked
    clicked = True
    # print("clicked at", mouseX, mouseY)

root.after(1000, runGame)

screen.bind("<Motion>", mouseMove)
screen.bind("<MouseWheel>", scrollWheel)
screen.bind("<Button-1>", mouseClick)
screen.bind("<Key>", buttonPress)

screen.pack()
screen.focus_set()

root.mainloop()
