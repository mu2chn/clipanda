import clipanda
import sys, tkinter
from tkinter import filedialog

DEFAULT_HEIGHT = 40

class EntryBox:
    def __init__(self, label="", x=0, y=0, textwidth=80, entrywidth=20, hidechar=False):
        self.__label = tkinter.Label(text=label)
        self.__label.place(x=x, y=y)
        
        optional = {}
        if hidechar:
            optional["show"] = "*"
        self.__entry = tkinter.Entry(width=entrywidth, **optional)
        self.__entry.place(x=x+textwidth, y=y)
    
    def getText(self):
        return self.__entry.get()

    def clearText(self):
        self.__entry.delete(0)

    def setText(self, text):
        self.clearText()
        self.__entry.insert(tkinter.END, text)

class Button:
    def __init__(self, text="", x=0, y=0, width=10):
        self.__button = tkinter.Button(text=text, width=width)
        self.__button.place(x=x, y=y)

    def onLeftClick(self, func):
        self.__button.bind('<Button-1>', func=lambda arg: func())

def dbgShow(arg):
    print(arg)
    pass

def selectFolder():
    return tkinter.filedialog.askdirectory(initialdir="~/")

def render():
    root = tkinter.Tk()

    root.title(u"PandAfetcher")
    root.geometry("500x400")

    loginX = 10
    loginY = 30
    username = EntryBox(label="username", x=loginX, y=loginY)
    password = EntryBox(label="password", x=loginX, y=loginY+DEFAULT_HEIGHT, hidechar=True)

    button = Button(text="ログイン", x=loginX+330, y=loginY+DEFAULT_HEIGHT-8)
    button.onLeftClick(lambda : print(username.getText(), password.getText()))

    refDir = EntryBox(label="path", x=10, y=160, entrywidth=40, textwidth=40)
    button = Button(text="参照", x=380, y=155)
    button.onLeftClick(lambda : refDir.setText(filedialog.askdirectory(initialdir="~/Documents")))
    root.mainloop()


if __name__ == "__main__":
    render()
    