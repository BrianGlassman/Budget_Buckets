
import tkinter
from tkinter import ttk


root = None

class Root(tkinter.Tk, tkinter.Toplevel):
    def __init__(self, title):
        global root
        if root is None:
            tkinter.Tk.__init__(self)
            root = self
        else:
            tkinter.Toplevel.__init__(self, master=root)
        self.title(title)

Root('root')
Root('top')

root.mainloop()