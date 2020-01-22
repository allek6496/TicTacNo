#import statements
from tkinter import *
from PIL import Image, ImageTk #if you are getting an error, run `pip install pillow`, and then it should work
from time import sleep
from random import randint, uniform, choice
from math import inf, sqrt, ceil
import os

#initialize tkinter and canvas
root = Tk()
screen = Canvas(root, width = 800, height = 800)

class qbit:
    """
    A qbit normally means the smallest piece of quantum information that can have two states (or a superposition of those two statements)

    Here, a qbit is a small particle that dissipates, and will swap from blue to red randomly
    """
    def __init__(self, x, y, range):
        """
        x - The x portion of the particle's starting position
        y - The y portion of the particle's starting position
        range - The distance the particle can go before being deleted
        """
        #store the current position
        self.x = x
        self.y = y

        #keep track of where the particle was made
        self.startX = x
        self.startY = y

        #how far from the origin the particle can go before being deleted
        self.range = range

        #init the velocity components
        self.xVel = uniform(-6, 6)
        self.yVel = uniform(-6, 6)

        #these change over time, but it's important to init them here
        self.colour = "red"
        self.radius = 6

        #this normalizes the velocity to make sure that they all dissipate in aprox the same amount of time
        self.normalizeVel()

    def normalizeVel(self):
        """
        This sets the magnitude of the velocity vector to 1, then multiplies it by a scalar to get all particles going at the same speed
        """

        #there's a miniscule chance the velocities add to 0, so try/catch blocks are needed
        try:
            newX = self.xVel/(self.xVel**2 + self.yVel**2)
        except ZeroDivisionError:
            newX = 0
        try:
            newY = self.yVel/(self.xVel**2 + self.yVel**2)
        except ZeroDivisionError:
            newY = 0

        #as previously stated, vel of 1 was too slow, so it's 8
        self.xVel = newX*8
        self.yVel = newY*8

    def draw(self):
        """
        Draws the qbit in it's current position, radius, and colour
        """
        global dump
        
        dump.append(screen.create_oval(self.x - self.radius,
                                       self.y - self.radius,
                                       self.x + self.radius,
                                       self.y + self.radius, fill=self.colour, outline=self.colour))

    def update(self):
        """
        Called every frame, this handles movement, randomness and pretty much everything neccecary
        """
        global qbits

        #update position based on velocity
        self.x += self.xVel
        self.y += self.yVel

        #calculate the distance from where the particle started
        distance = sqrt((self.x - self.startX)**2 + (self.y - self.startY)**2)

        #if the particle surpasses the allowable range, it removes itself from the list of qbits
        if distance >= self.range:
            qbits.remove(self)

        #the radius gets progressively smaller the further from the origin the qbit gets
        self.radius = 6*(distance/self.range - 1)

        #a chance to switch colours every frame
        if randint(0, 10) == 0:
            self.colour = "red" if self.colour == "blue" else "blue"

        #draws the particle
        self.draw()

class game:
    """
    This is the base class that represents a game of tic-tac-toe. 
    """
    def __init__(self, nextScreen, X=3, Y=3, quantum=True, effects=0, people = 2, horde=False):
        """
        nextScreen - The screen to switch to after the game is over
        X - The number of columns of the grid
        Y - The number of rows of the grid
        quantum - Whether or not partial moves are allowed
        effects - The level of vfx on the board
        people - The number of players in the game (max 4)
        horde - Whether or not the X player is playing against a horde of identical players or individual players
        """
        self.nextScreen = nextScreen
        self.X = X
        self.Y = Y
        self.effects = effects
        self.people = people
        self.horde = horde

        #a list of allowable players and the colours they use. This could be bigger, but I thought 4 was good
        self.players = {"X": ["#820c0c", "#7f0000", "#ab000d"], 'O': ["#1a237e", "#000051", "#001970"], 'Z': ["#28871b", "#154a0d", "#246134"], 'Q': ["#38115e", "#4b1085", "#412973"]}
        
        #the number of sucessive turns the horde has had. Only used if horde=True
        self.hordeProg = 0

        #the width of each individual square
        self.width = 800/X

        #the height of each individual square
        self.height = 800/Y

        #the 2d array that stores the permenant moves
        self.board = self.generateBoard()

        #the 2d array that stores the partial portions of the current player's move
        self.currMove = self.generateBoard()

        #the 3d array that stores a list of previous currMoves
        self.moves = []

        #the amount of move the active player can still place down
        self.moveLeft = 100

        #the symbol of the active player. Always starts with "X"
        self.turn = "X"

        #how much is placed down at a time. Since quantum = False means partial isn't allowed, 100 does just this
        self.placeIncrement = 5 if quantum else 100

        #the amount of mousewheel movement required to register a placeIncrement. This effectively the sensitivity of the scroll wheel
        self.scrollThreshold = 2

        #keeps track of how much has been scrolled
        self.scrollTotal = 0

        #once a square is measured, it can't me measured again this turn
        self.measured = False

        #stores the winner of the game
        self.winner = None

        #how long to show the win-screen for
        self.winTimer = 60

        #holds how much the board has an offset
        self.glitchOffset = [0, 0]

        #this sets the effect frequency based on the effects number
        if effects != 0:
            self.glitchChance = 360/effects
        else:
            self.glitchChance = 0
        
    def drawEffects(self):
        """
        Draw the special Red and Blue effects during the game
        """        
        global qbits

        #chance to set a random offset for the board
        if randint(0, self.glitchChance) == 0:
            self.glitchOffset = [randint(-10, 10), randint(-10, 10)]
            
        #if there was no offset set, reduce the curent offset and draw it
        elif not(self.glitchOffset[0] == 0 and self.glitchOffset[1] == 0):
            
            #reduce each component by an exponential amount
            for i in range(2):
                self.glitchOffset[i] /= 1.4
                
                #this is important otherwise it would take a long time to fully go away
                if self.glitchOffset[i] < 0.5:
                    self.glitchOffset[i] = 0

            #draw the grid
            for i in range(1, self.X):
                dump.append(screen.create_line(i*self.width+self.glitchOffset[0], 0, i*self.width+self.glitchOffset[0], 800, width=2, fill="red" if self.glitchOffset[0] > 0 else "blue"))
            
            for i in range(1, self.Y):
                dump.append(screen.create_line(0, i*self.height + self.glitchOffset[1], 800, i*self.height + self.glitchOffset[1], width=2, fill="red" if self.glitchOffset[0] > 0 else "blue"))

                
    def generateBoard(self):
        """
        Create a new self.X by self.Y arrray grid
        """
        newBoard = []
        for x in range(self.X):
            newBoard.append([])
            for y in range(self.Y):
                newBoard[-1].append(0)
                
        return newBoard

    
    def draw(self):
        """
        Draw the board on the screen
        """
        global dump, qbits

        if self.winner:
            if len(qbits) > 0:
                qbits = []
            if self.winner == 'T':
                dump.append(screen.create_text(800/2, 800/2, text=self.winner, font="Arial 400", fill="gray40"))
            else:
                dump.append(screen.create_text(800/2, 800/2, text=self.winner, font="Arial 400", fill=self.players[self.winner][2]))
        else:
            self.drawEffects()

            #horizontal lines
            for i in range(1, self.X):
                dump.append(screen.create_line(i*self.width, 0, i*self.width, 800, width=2))
            
            #vertical lines
            for i in range(1, self.Y):
                dump.append(screen.create_line(0, i*self.height, 800, i*self.height, width=2))

            #fills in the info for each square
            for x in range(self.X):
                for y in range(self.Y):
                    if self.board[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=self.board[x][y], font="Arial " + str(int(self.width) - 5), fill=self.players[self.board[x][y]][1]))

                    if self.currMove[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=str(self.currMove[x][y]/100), anchor="n", font="Arial 60", fill=self.players[self.turn][1]))

                    for j in range(len(self.moves)):
                        current = self.moves[j][x][y]
                        # if self.people == 2:
                        #     if current != 0:
                        #         if self.moves[j][-1] == 'X':
                        #             dump.append(screen.create_text(x*self.width + 20*(j//5) + 10, y*self.height + (j%5+1)*15, text=str(int(current)/100), anchor="nw", font="Arial 16", fill="#7f0000"))
                        #         else:
                        #             dump.append(screen.create_text(x*self.width + 20*(j//5) + 190, y*self.height + (j%5+1.5)*15, text=str(int(current)/100), anchor="ne", font="Arial 16", fill="#000051"))
                        # else:
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
                self.turn = 'Z'
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
                changePage(self.nextScreen)
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

    def __init__(self, nextScreen, X=3, Y=3, quantum=True, effects=0, people = 2, horde = False, He=False):
        game.__init__(self, nextScreen, X, Y, quantum, effects, people, horde)
        self.He = He
        self.delayTimer = 0
        self.turnProgression = 0
        self.quantum=quantum

    def passTurn(self):
        game.passTurn(self)
        self.delayTimer = randint(2, 6)*15

    def findWin(self, player):
        if self.quantum:
            return None
        else:
            moves = []
            for X in range(self.X):
                blank = None
                for Y in range(self.Y):
                    if self.board[X][Y] == 0:
                        if blank:
                            blank = None
                            break
                        else:
                            blank = [X, Y]
                    elif self.board[X][Y] != player:
                        blank = None
                        break
                if blank:
                    moves.append(blank)
            
            for Y in range(self.Y):
                blank = None
                for X in range(self.X):
                    if self.board[X][Y] == 0:
                        if blank:
                            blank = None
                            break
                        else:
                            blank = [X, Y]
                    elif self.board[X][Y] != player:
                        blank = None
                        break
                if blank:
                    moves.append(blank)
            
            for X in range(self.X):
                blank = None
                prog = 0
                pos = [X, 0]
                while 0 <= pos[0] < self.Y and 0 <= pos[1] < self.Y:
                    if self.board[pos[0]][pos[1]] == 0:
                        if blank:
                            blank = None
                            break
                        else:
                            blank = [pos[0], pos[1]]
                    elif self.board[pos[0]][pos[1]] != player:
                        blank = None
                        break
                    pos[0] += 1
                    pos[1] += 1
                    prog += 1
                if blank and prog >= 3:
                    moves.append(blank)
            
            for Y in range(self.Y):
                blank = None
                prog = 0
                pos = [0, Y]
                while self.Y > pos[1] >= 0 and 0 <= pos[0] < self.X:
                    if self.board[pos[0]][pos[1]] == 0:
                        if blank:
                            blank = None
                            break
                        else:
                            blank = [pos[0], pos[1]]
                    elif self.board[pos[0]][pos[1]] != player:
                        blank = None
                        break

                    pos[0] += 1
                    pos[1] -= 1
                    prog += 1
                if blank and prog >= 3:
                    moves.append(blank)

            print(moves)
            return moves
                        
    def update(self):
        if self.winner:
            self.winTimer -= 1
            if self.winTimer <= 0:
                if self.winner == 'X':
                    changePage(self.nextScreen)
                else:
                    changePage("death1")
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
                if self.quantum:
                    if self.delayTimer <= 0 and self.turnProgression == 0:
                        self.delayTimer = randint(1, 2)*15
                        self.favPos = [randint(0, self.X-1), randint(0, self.Y-1)]
                        self.turnProgression = 1

                        if randint(0, 5) != 0:
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
                    if self.delayTimer <= 0:
                        try:
                            bestMove = choice(self.findWin(self.turn))
                        except IndexError:
                            try:
                                bestMove = choice(self.findWin('X'))
                            except IndexError:
                                goodMoves = [
                                    [int((self.X-1)/2), int((self.Y-1)/2)],
                                    [int((self.X-1)/2), ceil((self.Y-1)/2)],
                                    [ceil((self.X-1)/2), int((self.Y-1)/2)],
                                    [ceil((self.X-1)/2), ceil((self.Y-1)/2)],
                                    [0, 0],
                                    [0, self.Y-1],
                                    [self.X-1, 0],
                                    [self.X-1, self.Y-1]
                                ]
                                for move in goodMoves:
                                    if self.board[move[0]][move[1]] == 0:
                                        bestMove = move
                                        break
                                else:
                                    for X in self.X:
                                        for Y in self.Y:
                                            if self.board[X][Y] == 0:
                                                bestMove = [X, Y]

                        self.currMove[bestMove[0]][bestMove[1]] = 100

                        self.moves.append(self.currMove + [self.turn])
                        self.passTurn()
                        self.currMove = self.generateBoard()
                    else:
                        self.delayTimer -= 1

            else:
                game.update(self)
        
            self.winner = self.checkWin()
        self.draw()
            


def setInitialValues(): 
    global checkpoint, deathTimer, games, buttons, pics, qbits, mouseX, mouseY, scrollD, running, page, size, clicked, board, dump, keysPressed
    keysPressed = []
    qbits = []
    deathTimer = 30
    checkpoint = None
    dump = []
    clicked = False
    running = True
    mouseX = 0
    mouseY = 0
    scrollD = 0
    page = 0
    size = None
    board = None
    games = {"3 X 3": pvp3, 
             "4 X 4": pvp4,
             "5 X 5": pvp5,
             "nonQuantum": nonQuantum,
             "oneZombie": oneZombie,
             "threeZombies": threeZombies,
             "He": He}
    buttons = [["start", "close", 334, 678, 475, 753],
               ["start", "mode", 95, 85, 370, 195],
               ["start", "info1", 437, 85, 711, 195],
               ["sizes", "3 X 3", 10, 10, 395, 95],
               ["mode", "sizes", 95, 85, 370, 195],
               ["mode", "story1", 439, 88, 711, 200],
               ["mode", "start", 336, 672, 474, 756],
               ["info1", "info2", 600, 675, 737, 746],
               ["info1", "start", 68, 680, 206, 748],
               ["info2", "info3", 580, 677, 721, 754],
               ["info2", "info1", 41, 669, 182, 745],
               ["info3", "info4", 591, 675, 730, 751],
               ["info3", "info2", 54, 668, 192, 744],
               ["info4", "start", 589, 677, 731, 750],
               ["info4", "info3", 53, 673, 191, 743],
               ["sizes", "4 X 4", 405, 10, 790, 95],
               ["sizes", "5 X 5", 10, 105, 395, 190],
               ["story1", "story2", 0, 0, 800, 800],
               ["story2", "story3", 0, 0, 800, 800],
               ["story3", "nonQuantum", 0, 0, 800, 800],
               ["story4", "story5", 0, 0, 800, 800],
               ["story5", "story6", 0, 0, 800, 800],
               ["story6", "story7", 0, 0, 800, 800],
               ["story7", "oneZombie", 0, 0, 800, 800],
               ["story8", "threeZombies", 0, 0, 800, 800],
               ["story9", "He", 0, 0, 800, 800]]

    loadPics()

def loadPics():
    global pics
    loadingImage = Image.open("assets/loading.gif")
    loadingImage = loadingImage.resize((800, 800), Image.ANTIALIAS)
    loadingImage = ImageTk.PhotoImage(image=loadingImage)
    screen.create_image(400, 400, image=loadingImage)
    screen.update()

    pics = {}
    prog = 0
    for file in os.listdir("assets"):
        prog += 1
        screen.create_image(400, 400, image=loadingImage)
        text = screen.create_text(400, 400, anchor="center", font = "Arial 200", text=str(prog) + '/' + str(len(os.listdir("assets"))))
        print(file[:-4])
        screen.update()
        
        image = Image.open("assets/" + file)
        if file == "game.gif":
            image = image.resize((1000, 1000), Image.ANTIALIAS)
        else:
            image = image.resize((800, 800), Image.ANTIALIAS)
        pics[file[:-4]] = ImageTk.PhotoImage(image=image)

        screen.delete(text)
        
def cleanup():
    global dump

    screen.delete(*dump)
    dump = []

def afterUpdates():
    global scrollD, keysPressed, clicked
    
    clicked = False
    scrollD = 0
    keysPressed = []

def explosion():
    global qbits

    for i in range(300):
        qbits.append(qbit(400, 400, 400))

def changePage(newPage):
    global page, board, running

    if newPage == "close":
        running = False
        return        

    board=None

    if newPage == "story4":
        explosion()

    try:
        games[newPage]()
    except KeyError:
        pass

    afterUpdates()
    screen.delete("all")
        
    if newPage in list(games.keys()):
        screen.create_image(400, 400, image=pics["game"])
        page = "game"
    else:
        screen.create_image(400, 400, image=pics[newPage])
        page = newPage

def pvp3():
    global board
    board = game("sizes", X=3, Y=3, effects=1)

def pvp4():
    global board
    board = game("sizes", X=4, Y=4, effects=1)

def pvp5():
    global board
    board = game("sizes", X=5, Y=5, effects=1)

def nonQuantum():
    global board, checkpoint
    checkpoint = "story3"
    board = campaignGame("story4", X=3, Y=3, effects=0, quantum=False, He=True)

def oneZombie():
    global board, checkpoint
    checkpoint = "story7"
    board = campaignGame("story8", X=3, Y=3, effects=1, horde=True)

def threeZombies():
    global board, checkpoint
    checkpoint = "story8"
    board = campaignGame("story9", X=5, Y=5, effects=2, people=4, horde=True)

def He():
    global board, checkpoint
    checkpoint = "story9"
    board = campaignGame("story10", X=4, Y=4, effects=3, He=True)

def runGame():
    global board, page, clicked, scrollD, dump, qbits, deathTimer
    setInitialValues()

    changePage("start")

    while running:

        for q in qbits:
            q.update()

        if page == "game":
            board.update()
        else:
            for button in buttons:
                if button[0] == page:
                    dump.append(screen.create_rectangle(button[2], button[3], button[4], button[5], outline="red"))
                    if clicked and button[2] <= mouseX <= button[4] and button[3] <= mouseY <= button[5]:
                        changePage(button[1])

        if page == "death1":
            deathTimer -= 1
            if deathTimer == 0:
                changePage("death2")
                deathTimer = 90

        elif page == "death2":
            deathTimer -= 1
            if deathTimer == 0:
                changePage("death3")
                deathTimer = 60
        
        elif page == "death3":
            deathTimer -= 1
            if deathTimer == 0:
                changePage(checkpoint)
                deathTimer = 30

        afterUpdates()

        screen.update()
        sleep(0.03)
        cleanup()
    root.destroy()

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
    print("clicked at", mouseX, mouseY)

root.after(500, runGame)

screen.bind("<Motion>", mouseMove)
screen.bind("<MouseWheel>", scrollWheel)
screen.bind("<Button-1>", mouseClick)
screen.bind("<Key>", buttonPress)

screen.pack()
screen.focus_set()

root.mainloop()
