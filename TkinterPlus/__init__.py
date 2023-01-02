"""Wrappers around base tkinter classes to add my expanded functionality"""

import tkinter

import TkinterPlus.Functions as _import_Functions
import TkinterPlus.Values as _import_Values

class Tk(tkinter.Tk):
    gridconfigure = _import_Functions.gridconfigure
    grid = _import_Functions.grid

class Root(Tk):
    """A root window with useful settings"""

    def __init__(self, x_stretch=1, y_stretch=1):
        super().__init__()
        res = [int(16*_import_Values.scale*x_stretch), int(9*_import_Values.scale*y_stretch)] # Default to 16:9
        self.geometry(f"{res[0]}x{res[1]}")
        self.title('Budget Buckets')
                
        # Always open in screen center
        # https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
        # get screen width and height
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (res[0]/2)
        y = (hs/2) - (res[1]/2)
        
        # set the dimensions of the screen 
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (res[0], res[1], x, y))
        
        self.gridconfigure()

class Button(tkinter.Button):
    gridconfigure = _import_Functions.gridconfigure
    grid = _import_Functions.grid

    def __init__(self, *args, **kwargs):
        # kwargs.update(relief='ridge', borderwidth=1*scale, font=font)
        # FIXME - using the big font makes all the buttons weird sizes
        kwargs.update(relief='ridge', borderwidth=1*Values.scale)

        super().__init__(*args, **kwargs)

class Canvas(tkinter.Canvas):
    gridconfigure = _import_Functions.gridconfigure
    grid = _import_Functions.grid

class Frame(tkinter.Frame):
    gridconfigure = _import_Functions.gridconfigure
    grid = _import_Functions.grid

    def __init__(self, *args, **kwargs):
        # kwargs.update(relief='ridge', borderwidth=1*scale, font=font)
        # FIXME - using the big font makes all the buttons weird sizes
        kwargs.update(relief='ridge', borderwidth=1*Values.scale)

        super().__init__(*args, **kwargs)

class ScrollableFrame(Frame):
    """A frame with vertical and horizontal scrolling
    Adapted from: https://stackoverflow.com/a/3092341/14501840
    """

    # FIXME the table contents overlap the frame border and scrollbars

    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = Canvas(master = self) # Need a canvas to scroll
        self.frame = Frame(master = self) # The frame inside the canvas

        self.vScroll = tkinter.Scrollbar(master = self, orient = "vertical", command = self.canvas.yview)
        self.hScroll = tkinter.Scrollbar(master = self, orient = "horizontal", command = self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vScroll.set)
        self.canvas.configure(xscrollcommand=self.hScroll.set)
        self.vScroll.pack(side = "right", fill = "y")
        self.hScroll.pack(side = "bottom", fill = "x")

        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
