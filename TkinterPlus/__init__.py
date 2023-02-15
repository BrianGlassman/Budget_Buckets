"""Wrappers around base tkinter classes to add my expanded functionality"""

import typing
import tkinter
from tkinter import ttk

import TkinterPlus.Functions as _import_Functions
import TkinterPlus.Values as _import_Values

class Root(tkinter.Tk, _import_Functions.FuncDeclare):
    """A Root or Toplevel window, as appropriate, with useful settings"""
    running: bool
    def __init__(self, x_stretch, y_stretch, title = 'Budget Buckets'):
        global root
        if root is None:
            # Create a Root window and save as root
            tkinter.Tk.__init__(self)
            root = self
        else:
            # Create a Toplevel window
            tkinter.Toplevel.__init__(self, master=root) # type: ignore
        
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
        
        # Set the dimensions of the screen and where it is placed
        self.geometry('%dx%d+%d+%d' % (res[0], res[1], x, y))
        
        self.gridconfigure()

        self.running = False
    
    def mainloop(self) -> None:
        """Gives a way to call mainloop safely"""
        if self.running:
            return
        else:
            self.running = True
            super().mainloop()
_import_Functions.add_functions(Root)
root: Root = None # type: ignore

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
    
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
_import_Functions.add_functions(Frame)

class ScrollableFrame(Frame, _import_Functions.FuncDeclare):
    """A frame with vertical and horizontal scrolling
    Adapted from: https://stackoverflow.com/a/3092341/14501840
    """

    # FIXME the table contents overlap the frame border and scrollbars

    def __init__(self, parent, vscroll=True, hscroll=True, **kwargs):
        kwargs.setdefault('bd', 0)
        super().__init__(parent, **kwargs)
        sub_kwargs = {}
        for key in ['bg',]:
            if key in kwargs: # Only add the key if it exists (so don't use kwargs.get)
                sub_kwargs[key] = kwargs[key]
        self.canvas = Canvas(master = self, bd=0, relief='flat', **sub_kwargs) # Need a canvas to scroll
        self.frame = Frame(master = self, bd=0, relief='flat', **sub_kwargs) # The frame inside the canvas

        if vscroll:
            self.vScroll = tkinter.Scrollbar(master = self, orient = "vertical", command = self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vScroll.set)
            self.vScroll.pack(side = "right", fill = "y")
        
        if hscroll:
            self.hScroll = tkinter.Scrollbar(master = self, orient = "horizontal", command = self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.hScroll.set)
            self.hScroll.pack(side = "bottom", fill = "x")

        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw", tags="self.frame")
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

class Treeview(ttk.Treeview, _import_Functions.FuncDeclare):
    pass
_import_Functions.add_functions(Treeview)

class TreeviewScrollable(Treeview):
    def __init__(self, parent, *args,
        vscroll: typing.Literal['', 'left', 'right'] = 'left',
        hscroll: typing.Literal['', 'bottom', 'top'] = 'bottom',
        **kwargs):
        self.outer_frame = Frame(parent)
        super().__init__(master=self.outer_frame, *args, **kwargs)
        
        if vscroll:
            self.vscroll = tkinter.Scrollbar(self.outer_frame, orient='vertical', command=self.yview)
            self.configure(yscrollcommand=self.vscroll.set)
            self.vscroll.pack(side=vscroll, fill='y', expand=False)
        
        if hscroll:
            self.hscroll = tkinter.Scrollbar(self.outer_frame, orient='horizontal', command=self.xview)
            self.configure(xscrollcommand=self.hscroll.set)
            self.hscroll.pack(side=hscroll, fill='x', expand=False)

        super().pack(fill='both', expand=True)
    
    def pack(self, *args, **kwargs):
        """Pass-through to the outer Frame"""
        return self.outer_frame.pack(*args, **kwargs)

