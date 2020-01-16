from tkinter import Tk, Canvas
from time import sleep
from random import randint
from math import inf
root = Tk()
screenWidth = 800
screenHeight = 800
screen = Canvas(root, width = screenWidth, height = screenHeight, background = "#616161")

class game:
    
    def __init__(self, X=3, Y=3, quantum=True, effects=0, people = 2):
        self.X = X
        self.Y = Y
        self.players = {"X": ["#b71c1c", "#7f0000", "#ab000d"], 'O': ["#1a237e", "#000051", "#001970"], 'V': ["#689f38", "#387002", "#4caf50"], 'Q': ["#5e35b1", "#1a237e", "#512da8"]}
        self.people = people
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
        self.winner = None
        self.winTimer = 60
        
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

        if self.winner:
            dump.append(screen.create_text(screenWidth/2, screenHeight/2, text=self.winner, font="Arial 400", fill=self.players[winner][2]))
        else:
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
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=self.board[x][y], font="Arial 200", fill=self.players[self.board[x][y]][1])

                    if self.currMove[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=str(self.currMove[x][y]/100), anchor="n", font="Arial 64", fill=self.players[self.turn][1]))

                    for j in range(len(self.moves)):
                        current = self.moves[j][x][y]
                        if self.people == 2:
                            if current != 0:
                                if self.moves[j][-1] == 'X':
                                    dump.append(screen.create_text(x*self.width + 10, y*self.height + (j+1)*12, text=str(int(current)/100), anchor="nw", font="Arial 8", fill="#7f0000"))
                                else:
                                    dump.append(screen.create_text(x*self.width + 190, y*self.height + (j+1)*12, text=str(int(current)/100), anchor="ne", font="Arial 8", fill="#000051"))
                        else:
                            if current != 0:
                                i = list(self.players.keys()).index(self.moves[j][-1])
                                dump.append(screen.create_text(x*self.width + 10*i, y*self.height + (j+1)*12, text=str(int(current)/100), anchor="nw", font="Arial 8", fill=self.players[self.moves[j][-1]][0])

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

    def resolve(self, t, x, y, found):
        global hit
        hit = []
        if found:
            self.board[x][y] = self.moves[t][-1]

            self.moves.pop(t)

            for turn in range(len(self.moves)):
                self.resolve(turn, x, y, False)
        else:
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
        if (t, x, y) in hit:
            return
        else:
            hit.append((t, x, y))
            self.moves[t][x][y] = newVal

            S = self.getSquare(x, y)
            if S > 100:
                delta = (100 - newVal) / (S - newVal)

                for turn in range(len(self.moves)):
                    if turn != t and self.moves[turn][x][y] != 0:
                        self.changeMove(turn, x, y, self.moves[turn][x][y]*delta)

    def changeMove(self, t, x, y, newVal):
        if (t, x, y) in hit:
            return
        else:
            hit.append((t, x, y))
            self.moves[t][x][y] = newVal

            S = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    S += self.moves[t][X][Y]
            
            if S != 100:
                delta = (100 - newVal) / (S - newVal)

                for X in range(self.X):
                    for Y in range(self.Y):
                        if not(X == x and Y == y) and self.moves[t][X][Y] != 0:
                            self.changeSquare(t, X, Y, self.moves[t][X][Y]*delta)

    def checkWin(self):
        goal = int((min(self.X, self.Y) + 3)/2)

        for X in range(self.X):
            prog = [0, 0]
            for Y in range(self.Y):
                if self.board[X][Y] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner!")
                        return prog[1]
                elif self.board[X][Y] == 0:
                    prog[0] = 0
                    prog[1] = 0
                else:
                    prog[0] = 1
                    prog[1] = self.board[X][Y]

        for Y in range(self.Y):
            prog = [0, 0]
            for X in range(self.X):
                if self.board[X][Y] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner!")
                        return prog[1]
                elif self.board[X][Y] == 0:
                    prog[0] = 0
                    prog[1] = 0
                else:
                    prog[0] = 1
                    prog[1] = self.board[X][Y]

        tied = True
        for X in range(self.X):
            for Y in range(self.Y):
                if self.board[X][Y] not in ["X", "O"]:
                    tied = False

        if tied:
            return "T"
        
        return None

    def passTurn(self):
        pass

    #To be run every frame
    def update(self):
        if self.winner:
            self.winTimer -= 1
            if self.winTimer <= 0:
                sizeSelect()
                global board
                board = None
        else:
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
                self.passTurn()
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

            self.winner = self.checkWin()

        self.draw()

def setInitialValues(): 
    global code, progression, mouseX, mouseY, scrollD, running, page, size, sizes, clicked, board, dump, keysPressed
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
    progression = 0
    code = code = {0: "Up", 1: "Up", 2: "Down", 3: "Down", 4: "Left", 5: "Right", 6: "Left", 7: "Right", 8: "b", 9: "a", 10: "Return"}
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
    changePage("selection")

    board = None

    for button in sizes:
        screen.create_rectangle(button[1], button[2], button[3], button[4], outline = "", fill="#00cbcc")
        screen.create_text((button[1]+button[3])/2, (button[2]+button[4])/2, text=button[0], font="Arial 64", fill="black")

def runGame():
    global board, page, clicked, scrollD, progression
    setInitialValues()

    sizeSelect()

    while running:
        # if progression == 11:
        #     if not board:
        #         board = game(X =)
        #     progression = 0
        # elif code[progression] in keysPressed:
        #     keysPressed.remove(code[progression])
        #     progression += 1
        # elif len(keysPressed) > 0:
        #     progression = 0

        if page == "selection":
            for button in sizes:
                if button[1] < mouseX < button[3] and button[2] < mouseY < button[4] and clicked:
                    board = game(X=int(button[0][0]), Y=int(button[0][-1]))
                    changePage("PVP")

        if page == "PVP":
            if board:
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
