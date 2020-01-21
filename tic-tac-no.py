from tkinter import Tk, Canvas, PhotoImage
from time import sleep
from random import randint, uniform
from math import inf, sqrt
root = Tk()
screenWidth = 800
screenHeight = 800
screen = Canvas(root, width = screenWidth, height = screenHeight, background = "#616161")

class qbit:

    def __init__(self, x, y, range):
        self.x = x
        self.y = y
        self.startX = x
        self.startY = y
        self.range = range
        self.xVel = uniform(-6, 6)
        self.xVel += self.xVel/abs(self.xVel)
        self.yVel = uniform(-6, 6)
        self.yVel += self.yVel/abs(self.yVel)
        self.colour = "red"
        self.radius = 6
        self.normalizeVel()

    def normalizeVel(self):
        try:
            newX = self.xVel/(self.xVel**2 + self.yVel**2)
        except ZeroDivisionError:
            newX = 0
        try:
            newY = self.yVel/(self.xVel**2 + self.yVel**2)
        except ZeroDivisionError:
            newY = 0
        self.xVel = newX*8
        self.yVel = newY*8

    def draw(self):
        global dump
        
        dump.append(screen.create_oval(self.x - self.radius,
                                       self.y - self.radius,
                                       self.x + self.radius,
                                       self.y + self.radius, fill=self.colour, outline=self.colour))

    def update(self):
        global qbits

        self.x += self.xVel
        self.y += self.yVel

        distance = sqrt((self.x - self.startX)**2 + (self.y - self.startY)**2)

        if distance >= self.range:
            qbits.remove(self)

        self.radius = 6*(distance/self.range - 1)

        if randint(0, 10) == 0:
            self.colour = "red" if self.colour == "blue" else "blue"

        # if randint(0, 5) == 0:
        #     self.xVel += uniform(-0.5, 0.5)
        # if randint(0, 5) == 0:
        #     self.yVel += uniform(-0.5, 0.5)

        self.draw()

class game:
    
    def __init__(self, X=3, Y=3, quantum=True, effects=0, people = 2, horde=False):
        self.horde = horde
        self.hordeProg = 0
        self.X = X
        self.Y = Y
        self.players = {"X": ["#820c0c", "#7f0000", "#ab000d"], 'O': ["#1a237e", "#000051", "#001970"], 'V': ["#28871b", "#154a0d", "#246134"], 'Q': ["#38115e", "#4b1085", "#412973"]}
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

        if effects != 0:
            self.glitchChance = 360/effects
            self.glitchOffset = [0, 0]
        else:
            self.glitchChance = 0
            self.glitchOffset = [0, 0]
        
    #draw fancy effects behind board and stuff
    def drawEffects(self):
        global qbits
        # if self.effects > 1:
        #     if randint(0, int(self.glitchChance/8)) == 0:
        #         qbits.append(qbit(mouseX, mouseY, 5*self.effects))

        if randint(0, self.glitchChance) == 0:
            self.glitchOffset = [randint(-5, 5)*2, randint(-5, 5)*2]
            print("glitched", self.glitchOffset)
        elif not(self.glitchOffset[0] == 0 and self.glitchOffset[1] == 0):
            
            for i in range(2):
                self.glitchOffset[i] /= 1.4
                if self.glitchOffset[i] < 0.5:
                    self.glitchOffset[i] = 0

            for i in range(1, self.X):
                dump.append(screen.create_line(i*self.width+self.glitchOffset[0], 0, i*self.width+self.glitchOffset[0], screenHeight, width=2, fill="red" if self.glitchOffset[0] > 0 else "blue"))
            
            for i in range(1, self.Y):
                dump.append(screen.create_line(0, i*self.height + self.glitchOffset[1], screenWidth, i*self.height + self.glitchOffset[1], width=2, fill="red" if self.glitchOffset[0] > 0 else "blue"))

    def generateBoard(self):
        newBoard = []
        for x in range(self.X):
            newBoard.append([])
            for y in range(self.Y):
                newBoard[-1].append(0)
        return newBoard

    #draws the board on the screen
    def draw(self):
        global dump, qbits

        if self.winner:
            if len(qbits) > 0:
                qbits = []
            if self.winner == 'T':
                dump.append(screen.create_text(screenWidth/2, screenHeight/2, text=self.winner, font="Arial 400", fill="gray40"))
            else:
                dump.append(screen.create_text(screenWidth/2, screenHeight/2, text=self.winner, font="Arial 400", fill=self.players[self.winner][2]))
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
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=self.board[x][y], font="Arial " + str(int(self.width) - 5), fill=self.players[self.board[x][y]][1]))

                    if self.currMove[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=str(self.currMove[x][y]/100), anchor="n", font="Arial 60", fill=self.players[self.turn][1]))

                    for j in range(len(self.moves)):
                        current = self.moves[j][x][y]
                        if self.people == 2:
                            if current != 0:
                                if self.moves[j][-1] == 'X':
                                    dump.append(screen.create_text(x*self.width + 20*(j//5) + 10, y*self.height + (j%5+1)*15, text=str(int(current)/100), anchor="nw", font="Arial 16", fill="#7f0000"))
                                else:
                                    dump.append(screen.create_text(x*self.width + 20*(j//5) + 190, y*self.height + (j%5+1.5)*15, text=str(int(current)/100), anchor="ne", font="Arial 16", fill="#000051"))
                        else:
                            if current != 0:
                                i = list(self.players.keys()).index(self.moves[j][-1])
                                dump.append(screen.create_text(x*self.width + 2 + 20*(j//5), y*self.height + (j+0.5)*13, text=str(int(current)/100), anchor="nw", font="Arial 12", fill=self.players[self.moves[j][-1]][0]))

            dump.append(screen.create_text(mouseX, mouseY, text=str(self.moveLeft/100), anchor="ne", font= " Arial 32", fill=self.players[self.turn][2]))


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

    def measuringBits(self, x, y, r=0):
        global qbits

        if r == 0:
            r = self.width/2

        x = (x+0.5)*(self.width)
        y = (y+0.5)*(self.height)

        for i in range(self.effects*10):
            qbits.append(qbit(x, y, r))


    def resolve(self, t, x, y, found):
        global hit
        hit = []

        self.measuringBits(x, y, self.width/2)

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
            self.measuringBits(x, y, 20)
            hit.append((t, x, y))
            self.moves[t][x][y] = newVal

            S = self.getSquare(x, y)
            if S > 100:
                try:
                    delta = (100 - newVal) / (S - newVal)
                except ZeroDivisionError:
                    delta = 0

                for turn in range(len(self.moves)):
                    if turn != t and self.moves[turn][x][y] != 0:
                        self.changeMove(turn, x, y, self.moves[turn][x][y]*delta)
                    else:
                        self.measuringBits(x, y, 20)

    def changeMove(self, t, x, y, newVal):
        if (t, x, y) in hit:
            return
        else:
            self.measuringBits(x, y, 20)
            hit.append((t, x, y))
            self.moves[t][x][y] = newVal

            S = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    S += self.moves[t][X][Y]
            
            if S != 100:
                try:
                    delta = (100 - newVal) / (S - newVal)
                except ZeroDivisionError:
                    delta = 0

                for X in range(self.X):
                    for Y in range(self.Y):
                        if not(X == x and Y == y) and self.moves[t][X][Y] != 0:
                            self.changeSquare(t, X, Y, self.moves[t][X][Y]*delta)

    def checkWin(self):
        # goal = int((min(self.X, self.Y) + 3)/2)
        goal = 3

        for X in range(self.X):
            prog = [0, 0]
            for Y in range(self.Y):
                if self.board[X][Y] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner!")
                        return prog[1]
                elif self.board[X][Y] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[X][Y]]

        for Y in range(self.Y):
            prog = [0, 0]
            for X in range(self.X):
                if self.board[X][Y] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner!")
                        return prog[1]
                elif self.board[X][Y] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[X][Y]]

        for X in range(self.X):
            prog = [0, 0]
            pos = [X, 0]
            while 0 <= pos[0] < self.Y and 0 <= pos[1] < self.Y:
                if self.board[pos[0]][pos[1]] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner")
                        return prog[1]
                elif self.board[pos[0]][pos[1]] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[pos[0]][pos[1]]]
                
                pos[0] += 1
                pos[1] += 1
        
        for Y in range(self.Y):
            prog = [0, 0]
            pos = [0, Y]
            while self.Y > pos[1] >= 0 and 0 <= pos[0] < self.X:
                if self.board[pos[0]][pos[1]] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == goal:
                        print(prog[1], "is the winner")
                        return prog[1]
                elif self.board[pos[0]][pos[1]] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[pos[0]][pos[1]]]

                pos[0] += 1
                pos[1] -= 1

        tied = True
        for X in range(self.X):
            for Y in range(self.Y):
                if self.board[X][Y] not in list(self.players.keys()):
                    tied = False

        if tied:
            return "T"
        
        return None

    def passTurn(self):
        if self.horde:
            self.hordeProg += 1
            if self.hordeProg == self.people:
                self.turn = 'X'
                self.hordeProg = 0
            else:
                self.turn = 'V'
        else:
            current = list(self.players.keys()).index(self.turn)

            current = current + 1

            self.turn = list(self.players.keys())[current%self.people]
        print(self.turn)

    #To be run every frame
    def update(self):
        global qbits

        if self.winner:
            self.winTimer -= 1
            if self.winTimer <= 0:
                modeSelect()
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
                            else:
                                print(self.effects*3)
                                for i in range(self.effects*3):
                                    qbits.append(qbit(mouseX, mouseY, 15))
                                    print("qbit made")
            
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

class campaignGame(game):

    def __init__(self, X=3, Y=3, quantum=True, effects=0, people = 2, horde = False):
        game.__init__(self, X, Y, quantum, effects, people, horde)
        self.delayTimer = 0
        self.turnProgression = 0

    def passTurn(self):
        game.passTurn(self)
        self.delayTimer = randint(2, 6)*15

    def update(self):
        if self.winner:
            self.winTimer -= 1
            if self.winTimer <= 0:
                sizeSelect()
                global board
                board = None
        else:
            resolved = []
            for t in range(len(self.moves)):
                for x in range(self.X):
                    for y in range(self.Y):
                        if round(self.moves[t][x][y]) == 100:
                            self.board[x][y] = self.moves[t][-1]
                            resolved.append(t)
            
            for turn in sorted(resolved, reverse=True):
                self.moves.pop(turn)
            
            if self.turn != 'X':

                if self.delayTimer <= 0 and self.turnProgression == 0:
                    self.delayTimer = randint(1, 2)*15
                    self.favPos = [randint(0, self.X-1), randint(0, self.Y-1)]
                    self.turnProgression = 1

                    if randint(0, 5) != 0:
                        currSquare = self.getCurrSquare()
                        x = randint(0, self.X-1)
                        y = randint(0, self.Y-1)

                        if self.getSquare(x, y) > 0 and self.board[x][y] == 0:
                            self.measuringBits(x, y)
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
                elif self.turnProgression == 0:
                    self.delayTimer -= 1

                if self.delayTimer <= 0 and self.turnProgression == 1:
                    if self.moveLeft > 0:
                        if randint(0, 12) == 0:
                            x = randint(0, self.X-1)
                            y = randint(0, self.Y-1)
                            self.favPos = [x, y]

                            if self.getSquare(x, y) <= 95:
                                self.delayTimer = randint(2, 15)
                                self.currMove[x][y] += 5
                                self.moveLeft -= 5
                        else:
                            x = self.favPos[0]
                            y = self.favPos[1]

                            if self.getSquare(x, y) <= 95:
                                self.delayTimer = randint(2, 15)
                                self.currMove[x][y] += 5
                                self.moveLeft -= 5
                    else:
                        self.turnProgression = 2
                else:
                    self.delayTimer -= 1

                if self.delayTimer <= 0 and self.turnProgression == 2:
                    self.delayTimer = randint(2, 4)*7

                    self.turnProgression = 0
                    self.moves.append(self.currMove + [self.turn])
                    self.passTurn()
                    self.currMove = self.generateBoard()
                    self.moveLeft = 100
                    self.measured = False
                elif self.turnProgression == 2:
                    self.delayTimer -= 1
            else:
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
                        self.measuringBits(x, y)
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
        
            self.winner = self.checkWin()
        self.draw()
            


def setInitialValues(): 
    global introPics, qbits, modes, mouseX, mouseY, scrollD, running, page, size, sizes, clicked, board, dump, keysPressed
    keysPressed = []
    qbits = []
    dump = []
    clicked = False
    running = True
    mouseX = 0
    mouseY = 0
    scrollD = 0
    page = 0
    size = None
    board = None
    sizes = [["3 X 3", 10, 10, 395, 95, 2], ["4 X 4", 405, 10, 790, 95, 2], ["5 X 5", 10, 105, 395, 190, 4]]
    modes = [["PVP", 10, 10, 395, 95], ["Campaign", 405, 10, 790, 95]]
    introPics = []
    for i in range(4):
        introPics.append(PhotoImage(file="assets/intro{}.gif".format(i)))

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

    afterUpdates()
    screen.delete("all")
    page = newPage

def sizeSelect():
    global board
    changePage("sizes")

    board = None

    for button in sizes:
        screen.create_rectangle(button[1], button[2], button[3], button[4], outline = "", fill="#00cbcc")
        screen.create_text((button[1]+button[3])/2, (button[2]+button[4])/2, text=button[0], font="Arial 64", fill="black")

def startPVP(X, Y, players):
    global board
    board = game(X=X, Y=Y, people=players, effects=2)
    changePage("PVP")

def modeSelect():
    changePage("modes")
    
    for button in modes:
        screen.create_rectangle(button[1], button[2], button[3], button[4], outline = "", fill="#00cbcc")
        screen.create_text((button[1]+button[3])/2, (button[2]+button[4])/2 - 5, text=button[0], font="Arial 64", fill="black")

def intro():
    changePage("intro0")

def campaign():
    global board

    changePage("campaign")
    board = campaignGame(X=5, Y=5, people=4, effects=2, horde=True)

def runGame():
    global board, page, clicked, scrollD, dump, qbits
    setInitialValues()

    modeSelect()

    while running:
        for q in qbits:
            q.update()

        if page == "modes":
            for button in modes:
                if button[1] < mouseX < button[3] and button[2] < mouseY < button[4] and clicked:
                    if button[0] == "PVP":
                        sizeSelect()
                    elif button[0] == "Campaign":
                        intro()

        if page == "sizes":
            for button in sizes:
                if button[1] < mouseX < button[3] and button[2] < mouseY < button[4] and clicked:
                    startPVP(int(button[0][0]), int(button[0][-1]), button[-1])

        if page == "PVP":
            board.update()

        # print(page[0:4])

        if page[0:5] == "intro":

            if page[-1] >= str(len(introPics)):
                campaign()
            elif clicked:
                page = page[0:5] + str(int(page[-1]) + 1)
                clicked = False
            else:
                dump.append(screen.create_image(400, 400, image=introPics[int(page[-1])], anchor="center"))

        if page == "campaign":
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
