"""Wrappers around base tkinter classes to add my expanded functionality"""

import tkinter
from tkinter import ttk

import TkinterPlus.Functions as _import_Functions
import TkinterPlus.Values as _import_Values

class Tk(tkinter.Tk): pass
_import_Functions.add_functions(Tk)

def _init_toplevel(self, x_stretch, y_stretch, title):
    """Used to initialize Root and TopLevel windows"""
    res = [int(16*_import_Values.scale*x_stretch), int(9*_import_Values.scale*y_stretch)] # Default to 16:9
    self.geometry(f"{res[0]}x{res[1]}")
    self.title(title)
            
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

class Root(Tk, _import_Functions.FuncDeclare):
    """A root window with useful settings"""
    def __init__(self, x_stretch=1, y_stretch=1, title='Budget Buckets'):
        super().__init__()
        _init_toplevel(self, x_stretch=x_stretch, y_stretch=y_stretch, title=title)
_import_Functions.add_functions(Root)

class Toplevel(tkinter.Toplevel, _import_Functions.FuncDeclare):
    """A TopLevel window with the same useful settings as Root"""
    def __init__(self, parent, x_stretch=1, y_stretch=1, title='Sub-window'):
        super().__init__(master=parent)
        _init_toplevel(self, x_stretch=x_stretch, y_stretch=y_stretch, title=title)
_import_Functions.add_functions(Root)

class Button(tkinter.Button, _import_Functions.FuncDeclare):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('relief', 'ridge')
        if 'borderwidth' not in kwargs and 'bd' not in kwargs:
            kwargs['borderwidth'] = 1*_import_Values.scale
        # FIXME - using the big font makes all the buttons weird sizes
        #kwargs.setdefault('font', font)

        super().__init__(*args, **kwargs)
_import_Functions.add_functions(Button)

class Canvas(tkinter.Canvas, _import_Functions.FuncDeclare): pass
_import_Functions.add_functions(Canvas)

class Combobox(ttk.Combobox, _import_Functions.FuncDeclare):
    def __init__(self, master, values=[], initial=None, **kwargs):
        super().__init__(master, **kwargs)
        self.values = values

        if initial is not None:
            self.set(initial)

    def bind(self, sequence="<<ComboboxSelected>>", func=None, add=None):
        assert sequence is None or isinstance(sequence, str)
        super().bind(sequence, func, add)

    #%% State
    @property
    def state(self):
        return self['state']
    @state.setter
    def state(self, state):
        """Sets the state:
        normal - text field is directly editable
        readonly - user can only select from the dropdown
        disabled - no interaction is possible
        """
        assert state in ("normal", "readonly", "disabled")
        self['state'] = state
    def set_state_normal(self):   self.state = "normal"
    def set_state_readonly(self): self.state = "readonly"
    def set_state_disabled(self): self.state = "disabled"

    #%% Values
    @property
    def values(self):
        return self['values']
    @values.setter
    def values(self, values):
        if not isinstance(values, list):
            # I know Set doesn't work, so just always make it a list
            values = list(values)
        self['values'] = values

    #%%
_import_Functions.add_functions(Combobox)

class Entry(tkinter.Entry, _import_Functions.FuncDeclare):
    # Like a Text widget, but single-line
    def __init__(self, master = None, textvariable: tkinter.Variable = ..., *args, **kwargs):
        super().__init__(master, textvariable=textvariable, *args, **kwargs)
_import_Functions.add_functions(Entry)

class Frame(tkinter.Frame, _import_Functions.FuncDeclare):
    def __init__(self, master = None, cnf = {}, **kwargs):
        kwargs.setdefault('relief', 'ridge')
        if 'borderwidth' not in kwargs and 'bd' not in kwargs:
            kwargs['borderwidth'] = 1*_import_Values.scale
        # FIXME - using the big font makes all the buttons weird sizes
        #kwargs.setdefault('font', font)

        super().__init__(master, cnf, **kwargs)
_import_Functions.add_functions(Frame)

class ScrollableFrame(Frame, _import_Functions.FuncDeclare):
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
_import_Functions.add_functions(ScrollableFrame)

class Text(tkinter.Text, _import_Functions.FuncDeclare):
    # Like an Entry widget, but multi-line
    def __init__(self, master = None, cnf = {}, text = '', **kwargs):
        super().__init__(master, cnf, **kwargs)
        assert isinstance(text, str)
        self.insert('1.0', text)
_import_Functions.add_functions(Text)

class WatchedText(Text, _import_Functions.FuncDeclare):
    """A text widget that generates an event when the contents are modified"""
    # Based on https://stackoverflow.com/a/40618152/14501840
    def __init__(self, master = None, cnf = {}, text = '', **kwargs):
        super().__init__(master, cnf, text, **kwargs)

        # Create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        # Pass the command through to the underlying widget
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        # Generate the event
        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result
    
    def watch(self, func):
        self.bind("<<TextModified>>", func)
_import_Functions.add_functions(WatchedText)
