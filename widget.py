import clipanda
import sys, tkinter

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

class Button:
    def __init__(self, text="", x=0, y=0, width=10):
        self.__button = tkinter.Button(text=text, width=width)
        self.__button.place(x=x, y=y)

    def onLeftClick(self, func):
        self.__button.bind('<Button-1>', func=func)

def render():
    root = tkinter.Tk()

    root.title(u"PandAfetcher")
    root.geometry("400x300")

    Static1 = tkinter.Label(text=u'test', foreground="#ff0000", background="#ffaacc")
    Static1.place(x=150, y=228)

    username = EntryBox(label="username", x=20, y=10)
    password = EntryBox(label="password", x=20, y=50, hidechar=True)

    button = Button(text="ログイン", x=20, y=90)
    button.onLeftClick(lambda arg: print(username.getText()))

    root.mainloop()


if __name__ == "__main__":
    render()
    