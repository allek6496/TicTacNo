from tkinter import *
from time import sleep
root = Tk()
width = 800
height = 800
screen = Canvas(root, width = width, height = height, background = "grey20")

class game:
    
    def __init(self, width=3, height=3, quantum=True, effects=0):
        self.width = width
        self.height = height
        self.quantum = quantum
        self.effects = effects
        self.board = [0]*9
        self.moves = []
        self.currMove = [0]*9
        self.moveLeft = 1
        self.turn = "X"

        self.drawFirst()

    def effects(self):
        #draw fancy effects behind board and stuff
        pass

    def draw(self):
        global dump, width, height
        
        self.effects()

        for i in range(1, self.width):
            screen.create_line(i*width/self.width, 0, i*width/self.width, height, fill="black")
        
        for i in range(1, self.height):
            screen.create_line(0, i*height/self.height, width, i*width/self.width, fill="black")

        for 

    def update(self):
        self.draw()

def setInitialValues(): 
    global mouseX, mouseY, scrollD, running, screen, size, sizes, clicked, board, dump
    dump = []
    clicked = False
    running = True
    mouseX = 0
    mouseY = 0
    scrollD = 0
    screen = 0
    size = None
    board = None
    sizes = [["3 X 3", 10, 10, 395, 95], ["4 X 4", 405, 10, 790, 95]]

def cleanup():
    global clicked, dump
    clicked = False

    for garbage in dump:
        screen.delete(dump)

    dump = []

def sizeSelect(): #screen 1
    global screen
    screen = "selection"

    for button in sizes:
        screen.create_rectangle(button[1], button[2], button[3], button[4], outline = "", fill="red")
        screen.create_text((button[1]-button[3])/2, (button[2]-button[4])/2+10, text=button[0], font="Arial 64")

def pvp(): #screen 2
    global screen, size
    sizeSelect()

def runGame():
    global board
    setInitialValues()

    pvp()

    while running:
        if screen = "selection":
            for button in sizes:
                if button[1] < mouseX < button[3] and button[2] < mouseY < button[4] and clicked = True:
                    clicked = False
                    board = game(int(button[0][0]), int(button[0][-1]))

        screen.update()
        sleep(0.03)

        cleanup()

def mouseMove(event):
    global mouseX, mouseY
    mouseX = event.x
    mouseY = event.y
    
def scrollWheel(event):
    global scrollD
    scrollD += event.delta/100

def mouseClick(event):
    global mouseX, mouseY, clicked
    clicked = True

def mouseRelease(event):
    global mouseX, mouseY, clicked
    clicked = False

root.after(1000, runGame)

screen.bind("<Motion>", mouseMove)
screen.bind("<MouseWheel>", scrollWheel)
screen.bind("<Button-1>", mouseClick)
screen.bind("<ButtonRelease-1>", mouseRelease)

screen.pack()
screen.focus_set()

root.mainloop()