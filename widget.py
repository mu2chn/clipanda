import clipanda
import sys, tkinter
from tkinter import filedialog
from tkinter import ttk

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

class DropDown:
    def __init__(self, root, list, x=0, y=0):
        frame = ttk.Frame(root, padding=10)
        frame.place(x=x, y=y)

        v = tkinter.StringVar()
        self.__cb = ttk.Combobox(
            frame,
            textvariable=v, 
            values=list, width=10)
        self.__cb.set(list[0])
        self.__cb.bind(
            '<<ComboboxSelected>>', 
            lambda e: print('v=%s' % v.get()))
        self.__cb.place(x=10, y=300)
        self.__cb.grid(row=0, column=0)

    def getVal(self):
        return self.__cb.get()

    def destroy(self):
        self.__cb.destroy()

pc = None

def init_pc(username, password):
    cookie = clipanda.PandaClient.createSession(username, password)
    pc = clipanda.PandaClient(cookie)

def render():
    root = tkinter.Tk()

    root.title(u"PandAfetcher")
    root.geometry("500x400")

    loginX = 10
    loginY = 30
    username = EntryBox(label="username", x=loginX, y=loginY)
    password = EntryBox(label="password", x=loginX, y=loginY+DEFAULT_HEIGHT, hidechar=True)

    button = Button(text="login", x=loginX+330, y=loginY+DEFAULT_HEIGHT-8)
    button.onLeftClick(lambda : init_pc(username.getText(), password.getText()))

    refDir = EntryBox(label="path", x=10, y=160, entrywidth=40, textwidth=40)
    button = Button(text="reference", x=380, y=155)
    button.onLeftClick(lambda : refDir.setText(filedialog.askdirectory(initialdir="~/Documents")))

    DropDown(root, ["A", "B", "C"], x=10, y=250)

    root.mainloop()


if __name__ == "__main__":
    render()
    