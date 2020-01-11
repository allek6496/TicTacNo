from tkinter import Tk, Canvas
from time import sleep
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
                    dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=self.board[x][y]/100, font="Arial 200"))

                if self.currMove[x][y] != 0:
                    dump.append(screen.create_text((x + 0.5)*self.width, (y + 0.5)*self.height, text=str(self.currMove[x][y]/100), anchor="n", font="Arial 64"))

                for j in range(len(self.moves)):
                    current = self.moves[j][x][y]
                    if current != 0:
                        if j%2 == 0:
                            # textSize(16);
                            # textAlign(LEFT, TOP);
                            # text(moves[i][j]/100, j%3*200+10, int(j/3)*200 + 10+ 10*i)
                            dump.append(screen.create_text(x*self.width + 10, y*self.height + (j+1)*10, text=str(current/100), anchor="nw", font="Arial 16"))
                        else:
                            # textSize(16);
                            # textAlign(RIGHT, TOP);
                            # text(moves[i][j]/100, j%3*200+190, int(j/3)*200 + 10 + 10*i)
                            dump.append(screen.create_text(x*self.width + 190, y*self.height + (j+1)*10, text=str(current/100), anchor="ne", font="Arial 16"))

        dump.append(screen.create_text(mouseX, mouseY, text=str(self.moveLeft/100), anchor="ne", font= " Arial 32", fill="red" if self.turn=="X" else "blue"))

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

    #To be run every frame
    def update(self):
        global scrollD

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

                if self.currMove[x][y] + delta >= 0 and 0 <= self.getSquare(x, y) + delta <= 100:
                    print("changed")
                    self.moveLeft -= delta
                    self.currMove[x][y] += delta

                    if self.moveLeft < 0:
                        self.currMove[x][y] -= delta
                        self.moveLeft = 0
                    elif self.moveLeft > 100:
                        self.currMove[x][y] -= delta
                        self.moveLeft = 100
        
        if "Return" in keysPressed and self.moveLeft == 0:
            self.turn = 'O' if self.turn == 'X' else 'X'
            self.moves.append(self.currMove)
            self.currMove = self.generateBoard()
            self.moveLeft = 100

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
    global scrollD, keysPressed
    
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

def mouseRelease(event):
    global mouseX, mouseY, clicked
    clicked = False

root.after(1000, runGame)

screen.bind("<Motion>", mouseMove)
screen.bind("<MouseWheel>", scrollWheel)
screen.bind("<Button-1>", mouseClick)
screen.bind("<ButtonRelease-1>", mouseRelease)
screen.bind("<Key>", buttonPress)

screen.pack()
screen.focus_set()

root.mainloop()