#import statements
from tkinter import Canvas, Tk
from sys import exit, executable
import subprocess
from time import sleep, time
from random import randint, uniform, choice
from math import sqrt, ceil
import os

try:
    from PIL import Image, ImageTk 
except ModuleNotFoundError:
    print("\nMODULE `PILLOW` NOT FOUND, INSTALLING NOW...\n")
    # print("\n******ERROR******\nplease run `pip install pillow`, to make this work\n")
    # exit()
    try:
        subprocess.check_call([executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, ImageTk
    except ModuleNotFoundError:
        print("\n******ERROR******\nFAILED TO AUTOMATICALLY INSTALL PILLOW, PLEASE RUN `pip install pillow` IN THE TERMINAL\n")
        exit()

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
    def __init__(self, nextScreen, X=3, Y=3, quantum=True, effects=0, people = 2, horde=False, connect=3):
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

        #how many symbols need to be connected in order to win
        self.connect = connect

        #the height of each individual square
        self.height = 800/Y

        #keeps track of how many turns have been made
        self.turns = 0

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

        #how long to wait beore closing the game
        self.winDelay = 30

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

        #if somedody has won, and we don't need to show the board any more
        if self.winner and self.winDelay <= 0:

            #reset the list of qbits so they don't show on the win announcement
            qbits = []

            #change the colour based on who won
            colour = ""
            if self.winner == 'T':
                colour = "gray40"
            else:
                colour = self.players[self.winner][2]

            dump.append(screen.create_text(800/2, 800/2, text=self.winner, font="Arial 400", fill=colour))

        #if we should be still showing the board
        else:
            #draw any effects that might be needed on the bottom
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
                    #if there's a measured move here
                    if self.board[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, 
                                                       (y + 0.5)*self.height, 
                                                       text=self.board[x][y], 
                                                       font="Arial " + str(int(self.width) - 5), #this changes the text size to better match the whole square
                                                       fill=self.players[self.board[x][y]][1]))

                    #if there's a move that hasn't been placed yet
                    if self.currMove[x][y] != 0:
                        dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, 
                                                       text=str(self.currMove[x][y]/100), 
                                                       anchor="n", font="Arial " + ("60" if self.people < 5 else "40"), 
                                                       fill=self.players[self.turn][1]))

                    #then go through all the previous moves
                    for j in range(len(self.moves)):
                        current = self.moves[j][x][y]
                        if current != 0:
                            # i = list(self.players.keys()).index(self.moves[j][-1])
                            dump.append(screen.create_text(x*self.width + 2 + 50*(j// (5 if self.people < 5 else 4)), #in the current square, ofset by more every 5 moves
                                                           y*self.height + (j% (5 if self.people < 5 else 4) +0.5)*15, #in the current square, ofset by more each move, reseting each 5
                                                           text=str(int(current)/100), #the value of the square divided by 100 to make it 0 -> 1
                                                           anchor="nw", font="Arial 1" + ("6" if self.people < 5 else "2"), 
                                                           fill=self.players[self.moves[j][-1]][0])) #fill it based on the colours given at the start

            #show how much move the player can still make
            dump.append(screen.create_text(mouseX, mouseY, 
                                           text=str(self.moveLeft/100),
                                           anchor="ne", font= " Arial 32", 
                                           fill=self.players[self.turn][2]))

    def getCurrSquare(self):
        """
        Gets which square the mouse is currently in 
        """
        x = mouseX // self.width
        y = mouseY // self.height
        
        return [int(x), int(y)]
        
    def getSquare(self, x, y):
        """
        Returns how full a given square is. This means all the previous additions are summed, not counting anything for the current turn
        """
        #if there's a measured move 
        if self.board[x][y] != 0:
            return 100

        total = self.currMove[x][y]

        for turn in self.moves:
            total += turn[x][y]

        return total

    def measuringBits(self, x, y, r):
        """
        Creates a bunch of qbits at a given square (x, y) with a given range (r). More qbits are made if effects is higher. Effects=0 means no qbits
        """
        global qbits

        #convert the x and y from the board into x and y on the screen
        x = (x+0.5)*(self.width)
        y = (y+0.5)*(self.height)

        #create to*effects qbits. This makes sure not to add qbits if the max has been reached. 
        for i in range(self.effects*10):
            if len(qbits) < maxQbits:
                qbits.append(qbit(x, y, r))


    def resolve(self, t, x, y, found):
        """
        Sets a given square (turn t, pos (x, y)) to either 0 (if found == False) or 100 (if found == True)
        """
        global hit
        hit = []

        #create a group of qbits with a large range
        self.measuringBits(x, y, self.width/2)

        #if we should set the value to 100
        if found:
            #set the square (x, y) to have the symbol for the turn t
            self.board[x][y] = self.moves[t][-1]

            #remove the whole move
            self.moves.pop(t)

            #go through each of the other turns, and make sure they don't have anything in this square
            for turn in range(len(self.moves)):
                self.resolve(turn, x, y, False)

        #if we should set the value to 0
        else:
            #set this square and turn to 0
            self.moves[t][x][y] = 0

            #find the sum of this move after removing the thing we needed to remove
            S = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    S += self.moves[t][X][Y]

            #the try is neccecary in case S is 0. This is a very unusual case since it means we are setting a 100 to 0, but it happened so I added the try/except
            try:
                #delta when multipied by each square summing to S, should make the new sum equal 100
                delta = 100 / S
            except ZeroDivisionError:
                delta = 0

            #multiply each other square of this turn by delta so the move still sums to 100
            for X in range(self.X):
                for Y in range(self.Y):
                    #this isn't really neccecary since changing a square that's already 0 does nothing, but it makes computations faster
                    if self.moves[t][X][Y] != 0:
                        #change the square at this turn to what it currently is times delta
                        self.changeSquare(t, X, Y, self.moves[t][X][Y]*delta)

    def changeSquare(self, t, x, y, newVal):
        """
        Change a specific part of a move to newVal, but only affect the other parts of the square
        """

        #this stops infinite loops by making sure we haven't done this before
        if (t, x, y) in hit:
            return

        else:
            #create qbits at this spot, but make it smaller
            self.measuringBits(x, y, 20)

            #log that this has been done
            hit.append((t, x, y))

            #set what we want to change to what it should be
            self.moves[t][x][y] = newVal

            #find the sum of this square
            S = self.getSquare(x, y)

            #if S <= 100 then everyhting is legal and nothing needs to be done
            if S > 100:

                #once again, the try/except block is for when S-newVal = 0. I just put a 
                try:
                    delta = (100 - newVal) / (S - newVal)
                except ZeroDivisionError:
                    delta = 0

                #go through each other turn and change it to what it should be
                for turn in range(len(self.moves)):
                    if turn != t and self.moves[turn][x][y] != 0:
                        self.changeMove(turn, x, y, self.moves[turn][x][y]*delta)

    def changeMove(self, t, x, y, newVal):
        """
        Works in largely the same way as changeSquare except this changes other parts of the move so they stay summing to 100
        """
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
            
            #this is the part that is different. Since it must be exactly 100, we check for that
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
        """
        Checks if a player has won the game, or if the game is tied
        """

        #go through each X value and Y value, keeping track of how many of a single symbol in a row are encountered
        for X in range(self.X):
            prog = [0, 0] #the first is the number in a row, and the second is the symbol
            for Y in range(self.Y):

                #if this is the same symbol as before and that symbol isn't 0
                if self.board[X][Y] == prog[1] and prog[1] != 0:

                    #increase the progress, and if we hit the required symbols in a row, there's a winner!
                    prog[0] += 1
                    if prog[0] == self.connect:
                        print(prog[1], "is the winner!")
                        return prog[1]

                #if it was a 0, reset the counter
                elif self.board[X][Y] == 0:
                    prog = [0, 0]

                #if it was a different symbol, re-start the counter with one of the new symbol
                else:
                    prog = [1, self.board[X][Y]]

        #the same but horizontally
        for Y in range(self.Y):
            prog = [0, 0]
            for X in range(self.X):
                if self.board[X][Y] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == self.connect:
                        print(prog[1], "is the winner!")
                        return prog[1]
                elif self.board[X][Y] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[X][Y]]

        #this one works by looping diagonally changin pos unitill it is nolonger in the square
        for X in range(self.X):
            prog = [0, 0]
            pos = [X, 0]
            while 0 <= pos[0] < self.Y and 0 <= pos[1] < self.Y:
                if self.board[pos[0]][pos[1]] == prog[1] and prog[1] != 0:
                    prog[0] += 1
                    if prog[0] == self.connect:
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
                    if prog[0] == self.connect:
                        print(prog[1], "is the winner")
                        return prog[1]
                elif self.board[pos[0]][pos[1]] == 0:
                    prog = [0, 0]
                else:
                    prog = [1, self.board[pos[0]][pos[1]]]

                pos[0] += 1
                pos[1] -= 1

        #this checks if it has tied. If every square is full and we haven't already detected a win, it must be a tie
        tied = True
        for X in range(self.X):
            for Y in range(self.Y):
                if self.board[X][Y] not in list(self.players.keys()):
                    tied = False

        if tied:
            return "T"
        
        #if nobody has won, just return a falsy value. False would also work here
        return None

    def passTurn(self):
        """
        Changes the current turn symbol based on a number of internal factors
        """

        #keeps track of how many turns have passed
        self.turns += 1

        #horde means we are fighting a group of zombies
        if self.horde:
            #if the number modulo number of people, that is X's turn, otherwise it's a zombie turn
            if self.turns%self.people == 0:
                self.turn = 'X'
            else:
                self.turn = 'Z'

        else:
            #find the current turn number and add one
            current = list(self.players.keys()).index(self.turn)

            current = current + 1

            #then get the symbol that coresponds to this new number
            self.turn = list(self.players.keys())[current%self.people]

    def update(self):
        """
        To be run every frame, handles movement, sensing, and measurment
        """
        global qbits, scrollD

        #if we have a winner, show the board for a while, wait a little longer with the win screen, and finally go to the specified next page
        if self.winner:
            if self.winDelay <= 0:
                self.winTimer -= 1
                if self.winTimer <= 0:
                    changePage(self.nextScreen)
            else:
                self.winDelay -= 1
        else:

            #find the sum of the moves made so far
            totalPlaced = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    totalPlaced += self.getSquare(X, Y)

            #if this sum won't fit another full move, then allow the active player to measure. Once they measure, pass the turn
            if totalPlaced > self.X*self.Y*100-100:
                if self.measured:
                    self.moves.append(self.currMove + [self.turn])
                    self.passTurn()
                    self.currMove = self.generateBoard()
                    self.moveLeft = 100
                    self.measured = False

            #check for any squares with all 100 of a move in them. This means there is no un-certainty and it is effectively measured
            resolved = []
            for t in range(len(self.moves)):
                for x in range(self.X):
                    for y in range(self.Y):
                        if round(self.moves[t][x][y]) == 100:
                            self.board[x][y] = self.moves[t][-1]
                            resolved.append(t)
            
            #fully remove each turn that has been measured
            for turn in sorted(resolved, reverse=True):
                self.moves.pop(turn)

            #this checks if an arrow key has been pressed
            delta = False
            if "Up" in keysPressed:
                delta = self.placeIncrement
            elif "Down" in keysPressed:
                delta = -1*self.placeIncrement

            #if the mouse is being scrolled, or if the arrow keys are being pressed
            if scrollD != 0 or delta:

                #change the amount of scrolling by scrollD. scrollD is just how much to add every frame if the mouse is being scrolled
                self.scrollTotal += scrollD

                #if the scrolling has passed the threshold or if an arrow key is being pressed
                if abs(self.scrollTotal) >= self.scrollThreshold or delta:

                    #if the arrow key isn't being pressed, set delta to self.placeIncrement times the direction of the scroll
                    if not delta:
                        self.scrollTotal = 0
                        delta = scrollD//abs(scrollD)*self.placeIncrement

                    #get the mouse's x and y in terms of the board
                    currSquare = self.getCurrSquare()
                    x = currSquare[0]
                    y = currSquare[1]

                    #make sure the mouse is on the screen
                    if 0 <= x < self.X and 0 <= y < self.Y:

                        #make sure that adding this move won't send it over or under the limits
                        if self.currMove[x][y] + delta >= 0 and 0 <= self.getSquare(x, y) + delta <= 100:
                            #make the move and keep track of how much was moved
                            self.moveLeft -= delta
                            self.currMove[x][y] += delta

                            #if you used more than or less than allowed, undo the move
                            if self.moveLeft < 0:
                                self.currMove[x][y] -= delta
                                self.moveLeft = 0
                            elif self.moveLeft > 100:
                                self.currMove[x][y] -= delta
                                self.moveLeft = 100

                            #if everything is fine, make some qbits based on the effect level
                            else:
                                for i in range(self.effects*3):
                                    if len(qbits) < maxQbits:
                                        qbits.append(qbit(mouseX, mouseY, 15))

            #check the turn should be passed            
            if "Return" in keysPressed and self.moveLeft == 0:

                #add the current set of probabillities to the list of moves
                self.moves.append(self.currMove + [self.turn])

                #change the symbol
                self.passTurn()

                #reset values to their defaults
                self.currMove = self.generateBoard()
                self.moveLeft = 100
                self.measured = False

            #check if measurment should be done
            if clicked and self.moveLeft == 100 and not self.measured:
                #store x and y of the mouse in terms of board
                currSquare = self.getCurrSquare()
                x = currSquare[0]
                y = currSquare[1]

                #don't measure a square with nothing in it, there's no point and it mitigates accidental presses
                if self.getSquare(x, y) > 0:
                    #remember that a measurment has been done this turn so we can not do it again
                    self.measured = True

                    die = randint(0, 100)

                    #loop through the parts of this square, subtracting their value from die. If it ever gets below 0, that's the one that was chosen
                    for turn in range(len(self.moves)):
                        #the try/except is since the self.moves often gets smaller, so eventually self.moves[turn] will throw an error
                        try:
                            die -= self.moves[turn][x][y]
                        except IndexError:
                            continue            

                        #if the die reached 0, make sure it won't again and set that part to 100
                        if die < 0:
                            die = 1000000
                            self.resolve(turn, x, y, True)

                        #if it didn't, set this part to 0
                        else:
                            self.resolve(turn, x, y, False)

            #check if a winner was found
            self.winner = self.checkWin()

        self.draw()

class campaignGame(game):
    """
    A subclass of game that supports single player
    """
    def __init__(self, nextScreen, X=3, Y=3, quantum=True, effects=0, people = 2, horde = False, He=False, coop=False, connect=3):
        game.__init__(self, nextScreen, X, Y, quantum, effects, people, horde, connect=connect)

        #if He is true, we should use strategy, otherwise make decisions randomly
        self.He = He

        #the first game isn't quantum, if it isn't quantum then the placeIncrement is 1
        self.quantum=quantum

        #the secret version has a coop mode, this means there are two X players
        self.coop = coop

        #some counter variables that need to be used throughout the class
        self.delayTimer = 0
        self.turnProgression = 0
        self.coopProgression = 0

    def passTurn(self):
        """
        Calculates which symbol comes next after passing the turn
        """

        #if we are playing coop, make there be 2 Xs and otherwise just use the normal pass method
        if self.coop:
            if self.turn == "X" and self.coopProgression == 0:
                self.turns += 1
                self.turn = "X"
                self.coopProgression = 1
            else:
                game.passTurn(self)
                self.coopProgression = 0
        else:
            game.passTurn(self)

        #restet the move delay so the opponents don't start their turn instantly
        self.delayTimer = randint(2, 6)*15

    def findHoles(self, player, connect):
        """
        Finds the holes that will form a `connect` long line of `player` symbols
        
        For example, when connect is 3, you find where to go that will make a 3 in a row line
        """
        moves = []

        #go through each horizontal group of `connect`, and check if there's just one 0 and the others are `player` symbols. If this is the case, log this as one of the places to go
        for X in range(self.X):
            for Y in range(self.Y-(connect - 1)):
                group = [self.board[X][Y+i] for i in range(connect)]
                if group.count(0) == 1 and group.count(player) == connect - 1:
                    moves.append([X, Y+group.index(0)])

        #vertical groups of `connect`
        for Y in range(self.Y):
            for X in range(self.X-(connect - 1)):
                group = [self.board[X+i][Y] for i in range(connect)]
                if group.count(0) == 1 and group.count(player) == connect - 1:
                    moves.append([X+group.index(0), Y])

        #diagonal groups
        for X in range(self.X-(connect - 1)):
            for Y in range(self.Y-(connect - 1)):
                group = [self.board[X+i][Y+i] for i in range(connect)]
                if group.count(0) == 1 and group.count(player) == connect - 1:
                    moves.append([X+group.index(0), Y+group.index(0)])

        for Y in range(self.Y-(connect - 1)):
            for X in range((connect - 1), self.X):
                group = [self.board[X-i][Y+i] for i in range(connect)]
                if group.count(0) == 1 and group.count(player) == connect - 1:
                    moves.append([X-group.index(0), Y+group.index(0)])
            
        return moves

    def fixMap(self):
        """
        This funcion is used in update to prevent trying to add to full squares
        """
        toRemove = []

        #go through each square we want to try, if it's full remove it
        for square in self.moveMap:
            if self.getSquare(square[0], square[1]) > 95:
                toRemove.append(square)
        
        for square in toRemove:
            self.moveMap.remove(square)
                        
    def update(self):
        """
        To be run every frame, handles basically everthin
        """

        #the cut to story4 needs to be instant, otherwise do what is normally done
        if self.winner:
            if self.nextScreen == "story4" and self.winner == "X":
                changePage("story4")
            elif self.winDelay <= 0:
                self.winTimer -= 1
                if self.winTimer <= 0:
                    if self.winner != "X":  
                       changePage("death1")
                    else:
                        changePage(self.nextScreen)
            else:
                self.winDelay -= 1
        else:
            #check if any squares have resovled, and remove them
            resolved = []
            for t in range(len(self.moves)):
                for x in range(self.X):
                    for y in range(self.Y):
                        if round(self.moves[t][x][y]) == 100:
                            self.board[x][y] = self.moves[t][-1]
                            resolved.append(t)

            #remove all the turns that were marked to remove
            for turn in sorted(resolved, reverse=True):
                self.moves.pop(turn)

            #find the sum of the moves made so far
            totalPlaced = 0
            for X in range(self.X):
                for Y in range(self.Y):
                    totalPlaced += self.getSquare(X, Y)

            #if this sum won't fit another full move, then allow the active player to measure. Once they measure, pass the turn
            if totalPlaced > self.X*self.Y*100-100:
                if self.measured:
                    self.moves.append(self.currMove + [self.turn])
                    self.passTurn()
                    self.currMove = self.generateBoard()
                    self.moveLeft = 100
                    self.measured = False
            
            #somewhat randomly pick a legal move
            if self.horde and self.turn == "Z":
                #this makes sure it doesn't start instantly, and only runs once
                if self.delayTimer <= 0 and self.turnProgression == 0:
                    #reset timer
                    self.delayTimer = randint(1, 2)*15
                    
                    #favPos is the place more likely to be added to
                    self.favPos = [randint(0, self.X-1), randint(0, self.Y-1)]

                    #make sure that this doesn't happen again this update, and the next one is run instead
                    self.turnProgression = 1

                    #random chance to measure. It probably will, but there's a chance it won't
                    if randint(0, 5) != 0:
                        #pick a square to try and measure
                        x = randint(0, self.X-1)
                        y = randint(0, self.Y-1)

                        #this is the same as the previous block in game's update
                        if self.getSquare(x, y) > 0 and self.board[x][y] == 0:
                            self.measuringBits(x, y, self.width/2)
                            self.measured = True
                            die = randint(0, 100)

                            for turn in range(len(self.moves)):
                                try:
                                    die -= self.moves[turn][x][y]
                                except IndexError:
                                    continue            

                                if die < 0:
                                    die = 1000000
                                    self.resolve(turn, x, y, True)
                                else:
                                    self.resolve(turn, x, y, False)
                #if we aren't ready to start that yet, reduce the timer
                elif self.turnProgression == 0:
                    self.delayTimer -= 1

                #next phase, this is run many times, placing 0.05 at a time
                if self.delayTimer <= 0 and self.turnProgression == 1:
                    #check we need to keep going
                    if self.moveLeft > 0:
                        #small chance to pick a new favPos
                        if randint(0, 12) == 0:
                            x = randint(0, self.X-1)
                            y = randint(0, self.Y-1)
                            self.favPos = [x, y]

                            #try and add 0.05 to this random square
                            if self.getSquare(x, y) <= 95:
                                self.delayTimer = randint(2, 15)
                                self.currMove[x][y] += 5
                                self.moveLeft -= 5

                        #if we didn't pick a new favPos, just keep adding to that one square
                        else:
                            x = self.favPos[0]
                            y = self.favPos[1]

                            #try and add to this square
                            if self.getSquare(x, y) <= 95:
                                self.delayTimer = randint(2, 15)
                                self.currMove[x][y] += 5
                                self.moveLeft -= 5
                    else:
                        self.turnProgression = 2
                else:
                    self.delayTimer -= 1

                #after a small delay, end the turn
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

            #this is playing against the more intelligent He
            elif self.He and self.turn == "O":
                #He has a different strategy depending on whether or not the game is quantum
                if self.quantum:
                    #the delayTimer and turnProgression works the same as before
                    if self.delayTimer <= 0 and self.turnProgression == 0:
                        self.delayTimer = randint(1, 2)*15
                        
                        #try and find the moves that must be made
                        self.moveMap = self.findHoles("O", self.connect)
                        self.fixMap()

                        #if there is nothing in this list, try something else
                        if len(self.moveMap) == 0:
                            self.moveMap = self.findHoles("X", self.connect)
                            self.fixMap()                      

                            if len(self.moveMap) == 0:
                                #try and look ahead a few moves
                                self.moveMap = self.findHoles("O", self.connect-1) + self.findHoles("X", self.connect-1)
                                self.fixMap()

                                if len(self.moveMap) == 0:
                                    #a list of generally good squares. These corespond to the centers and the corners
                                    self.moveMap = [
                                            [int((self.X-1)/2), int((self.Y-1)/2)],
                                            [int((self.X-1)/2), ceil((self.Y-1)/2)],
                                            [ceil((self.X-1)/2), int((self.Y-1)/2)],
                                            [ceil((self.X-1)/2), ceil((self.Y-1)/2)],
                                            [0, 0],
                                            [0, self.Y-1],
                                            [self.X-1, 0],
                                            [self.X-1, self.Y-1]
                                        ]

                                    self.fixMap()

                        #if we have a valid moveMap, pick a random favPos
                        if len(self.moveMap) > 0:
                            self.favPos = choice(self.moveMap)

                        #if there is still no valid moveMap, just pick a random square
                        else:
                            self.favPos = [randint(0, self.X-1), randint(0, self.Y-1)]

                        self.turnProgression = 1

                        #chance to measure something
                        if randint(0, 5) != 0:
                            x = randint(0, self.X-1)
                            y = randint(0, self.Y-1)

                            #this works the same as with the zombies/horde
                            if self.getSquare(x, y) > 0 and self.board[x][y] == 0:
                                self.measuringBits(x, y, self.width/2)
                                self.measured = True
                                die = randint(0, 100)

                                for turn in range(len(self.moves)):
                                    try:
                                        die -= self.moves[turn][x][y]
                                    except IndexError:
                                        continue            

                                    if die < 0:
                                        die = 1000000
                                        self.resolve(turn, x, y, True)
                                    else:
                                        self.resolve(turn, x, y, False)

                    elif self.turnProgression == 0:
                        self.delayTimer -= 1

                    if self.delayTimer <= 0 and self.turnProgression == 1:
                        if self.moveLeft > 0:
                            #He has a much higher chance to switch favPos, this means more of self.moveMap is covered
                            if randint(0, 3) == 0:
                                #if moveMap was never filled, just pick something random
                                try:
                                    self.fixMap()
                                    newPos = choice(self.moveMap)
                                except IndexError:
                                    newPos = [randint(0, self.X-1), randint(0, self.Y-1)]

                                x = newPos[0]
                                y = newPos[1]

                                self.favPos = [x, y]

                                #try and place in the new square. If you can't, it will just keep trying something random untill it gets it right
                                if self.getSquare(x, y) <= 95:
                                    self.delayTimer = randint(2, 15)
                                    self.currMove[x][y] += 5
                                    self.moveLeft -= 5

                            #if we don't need a new favPos, just add to the old one
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

                    #end the turn
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

                #if there is no quantum effects, i.e. all moves are 100 or 0
                else:
                    if self.delayTimer <= 0:
                        #try to find a move that will lead to He winning
                        try:
                            bestMove = choice(self.findHoles(self.turn, self.connect))

                        except IndexError:
                            #try and find something that will let the oppoent win, and go there
                            try:
                                bestMove = choice(self.findHoles('X', self.connect))

                            #pick from a list of good moves
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

                                #find the first one that is un-occupied
                                for move in goodMoves:
                                    if self.board[move[0]][move[1]] == 0:
                                        bestMove = move
                                        break

                                #if they were all occupied, find a value that works
                                else:
                                    for X in range(self.X):
                                        for Y in range(self.Y):
                                            if self.board[X][Y] == 0:
                                                bestMove = [X, Y]

                        #make the move. This is much simpler than other end statements since there's no quantum
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
    """
    Set the inital values required for the program
    """
    global maxQbits, code, codeProgress, prevTime, checkpoint, deathTimer, games, buttons, pics, qbits, mouseX, mouseY, scrollD, running, page, clicked, board, dump, keysPressed
    #store the keys currently pressed
    keysPressed = [] 

    #the steps in the Konami code
    code = ["Up", "Up", "Down", "Down", "Left", "Right", "Left", "Right", "b", "a", "Return"]
    
    #how far through the code the user have gotten
    codeProgress = 0

    #the particle limit of the screen
    maxQbits = 1500

    #store all the qbits to be updated
    qbits = []

    #how long to wait after deat
    deathTimer = 30

    #stores the most recent checkpoint that the player resets to when they lose in campaign mode
    checkpoint = None

    #dump is deleted from the screen at the end of every update
    dump = []

    #global variable that tells whether or not the mouse is clicked
    clicked = False
    
    #this keeps the main while loop going
    running = True

    #stores the mouse's x position
    mouseX = 0
    
    #stores the mouse's y position
    mouseY = 0

    #stores the state of the mouse-wheel
    scrollD = 0

    #stores the current page to be shown as the background
    page = 0

    #stores the board that needs to be updated every frame
    board = None

    #keeps track of the time the previous gameloop finished
    prevTime = time()

    #special functions to be run at the start of each game-type
    games = {"3 X 3": pvp3, 
             "4 X 4": pvp4,
             "5 X 5": pvp5,
             "nonQuantum": nonQuantum,
             "oneZombie": oneZombie,
             "threeZombies": threeZombies,
             "He": He,
             "coop": coop}

    #the invisible buttons that controll the menu. The format is ["page from", "page to", x1, y1, x2, y2]
    buttons = [["start", "close", 334, 678, 475, 753],
               ["start", "mode", 95, 85, 370, 195],
               ["start", "info1", 437, 85, 711, 195],
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
               ["sizes", "3 X 3", 86, 93, 359, 198],
               ["sizes", "4 X 4", 420, 82, 695, 191],
               ["sizes", "5 X 5", 93, 262, 362, 367],
               ["story1", "story2", 0, 0, 800, 800],
               ["story2", "story3", 0, 0, 800, 800],
               ["story3", "nonQuantum", 0, 0, 800, 800],
               ["story4", "story5", 0, 0, 800, 800],
               ["story5", "story6", 0, 0, 800, 800],
               ["story6", "story7", 0, 0, 800, 800],
               ["story7", "oneZombie", 0, 0, 800, 800],
               ["story8", "threeZombies", 0, 0, 800, 800],
               ["story9", "He", 0, 0, 800, 800],
               ["story10", "start", 0, 0, 800, 800]]

    #load the pictures
    loadPics()

def loadPics():
    """
    This is a special function that loads all the pictures needed for the game
    """
    global pics

    #the loading can take quite long, so the loading image is loaded first to act as a temporary background
    loadingImage = Image.open("assets/loading.gif")
    loadingImage = loadingImage.resize((800, 800), Image.ANTIALIAS)
    loadingImage = ImageTk.PhotoImage(image=loadingImage)

    #draw this image on the screen
    screen.create_image(400, 400, image=loadingImage)
    screen.update()

    pics = {}
    prog = 0
    for file in os.listdir("assets"):
        #makes sure only .gif files are being loaded
        if file[-4:] != ".gif":
            continue

        #this is the variable shown on the screen that marks the progress
        prog += 1

        #give the user an update of how things are progressing
        screen.create_image(400, 400, image=loadingImage)
        text = screen.create_text(400, 400, anchor="center", font = "Arial 200", text=str(prog) + '/' + str(len(os.listdir("assets"))))
        print(file[:-4])
        screen.update()
        
        #load the image
        image = Image.open("assets/" + file)

        #the game.gif file needs to be larger since the lines didn't work out
        if file == "game.gif":
            image = image.resize((1000, 1000), Image.ANTIALIAS)
        else:
            image = image.resize((800, 800), Image.ANTIALIAS)
        pics[file[:-4]] = ImageTk.PhotoImage(image=image)

        screen.delete(text)
        
def cleanup():
    """
    Run at the end of each game loop, it was going to do more than this, but now it just clears the dump 
    """
    global dump

    screen.delete(*dump)
    dump = []

def afterUpdates():
    """
    Reset the key values after they are used and before the delay where they will be given a value again
    """
    global scrollD, keysPressed, clicked
    
    clicked = False
    scrollD = 0
    keysPressed = []

def explosion():
    """
    This is used on story4 to make a large explosion of qbits
    """
    global qbits

    for i in range(300):
        if len(qbits) < maxQbits:
            qbits.append(qbit(400, 400, 400))

def changePage(newPage):
    """
    Change the page to something new, call it's special function if any, and clear the screen
    """
    global page, board, running, qbits

    if newPage == "close":
        running = False
        return        

    #reset some values
    board=None
    afterUpdates()
    screen.delete("all")
    qbits = []

    #if the new page is a game, make the game image and call it game
    if newPage in list(games.keys()):
        games[newPage]()
        screen.create_image(400, 400, image=pics["game"])
        page = "game"

    #otherwise just create the appropriate image and page value
    else:
        screen.create_image(400, 400, image=pics[newPage])
        page = newPage

    #if the new page is story4, cause the explosion
    if newPage == "story4":
        explosion()

#3x3 PVP
def pvp3():
    global board
    board = game("mode", X=3, Y=3, effects=1)

#4x4 PVP
def pvp4():
    global board
    board = game("mode", X=4, Y=4, effects=1, connect=4)

#5x5 PVP
def pvp5():
    global board
    board = game("mode", X=5, Y=5, effects=1)

#3x3 first campaign game
def nonQuantum():
    global board, checkpoint
    checkpoint = "story3"
    board = campaignGame("story4", X=3, Y=3, effects=0, quantum=False, He=True)

#3x3 second campaign game
def oneZombie():
    global board, checkpoint
    checkpoint = "story7"
    board = campaignGame("story8", X=3, Y=3, effects=1, horde=True)

#5x5 third campaign game
def threeZombies():
    global board, checkpoint
    checkpoint = "story8"
    board = campaignGame("story9", X=5, Y=5, effects=2, people=4, horde=True)

#4x4 final campaign game
def He():
    global board, checkpoint
    checkpoint = "story9"
    board = campaignGame("story10", X=4, Y=4, effects=3, He=True, connect=4)
    
#6x6 secret game
def coop():
    global board
    board = campaignGame("start", X=6, Y=6, people=6, coop=True, horde=True, connect=4)

def runGame():
    """
    Holds the main game loop, and is called to start the program
    """
    global board, page, prevTime, clicked, scrollD, dump, qbits, deathTimer, codeProgress
    setInitialValues()

    changePage("start")

    while running:
        #update the qbits
        for q in qbits:
            q.update()

        #check for Konami code completion
        if code[codeProgress] in keysPressed and page != "game":
            codeProgress += 1
            if codeProgress >= len(code):
                changePage("coop")
                codeProgress = 0
        elif len(keysPressed) > 0:
            codeProgress = 0

        #update the board if we're playing a game
        if page == "game":
            board.update()
        #if it's not a game, make the appropriate menu buttons
        else:
            for button in buttons:
                if button[0] == page:
                    #to see the bounding boxes run the follonwing line
                    #dump.append(screen.create_rectangle(button[2], button[3], button[4], button[5], outline="red"))
                    if clicked and button[2] <= mouseX <= button[4] and button[3] <= mouseY <= button[5]:
                        changePage(button[1])
        
        #handle the death scenes
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

        #if the screen.update() took longer than 0.03 seconds there's no need to sleep. This speeds up the game a surprising large amount
        if time() - prevTime < 0.03:
            sleep(0.03)

        cleanup()
        prevTime = time()

    #close the window when it's done
    root.destroy()

#funtions to be run that take input and store it globally
def mouseMove(event):
    global mouseX, mouseY
    mouseX = event.x
    mouseY = event.y
    
def scrollWheel(event):
    global scrollD
    scrollD = event.delta/100

def buttonPress(event):
    global scrollD, keysPressed

    keysPressed.append(event.keysym)

def mouseClick(event):
    global mouseX, mouseY, clicked
    clicked = True
    print("clicked at", mouseX, mouseY)

#wait before starting the runGame
root.after(500, runGame)

#bind the inputs
screen.bind("<Motion>", mouseMove)
screen.bind("<MouseWheel>", scrollWheel)
screen.bind("<Button-1>", mouseClick)
screen.bind("<Key>", buttonPress)

screen.pack()
screen.focus_set()

root.mainloop()