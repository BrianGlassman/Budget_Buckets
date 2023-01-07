def gridconfigure(self, rw=None, cw=None) -> None:
    """
    Convenience function to configure the grid for a TKinter object
    Parameters
    ----------
    self : TKinter object
        The object to configure
    rw : list, optional
        List of row weights. If None, make one row of weight 1
    cw : list, optional
        List of column weights. If None, make one column of weight 1
    """
    if rw is None:
        rw = [1]
    if cw is None:
        cw = [1]
    
    for i, weight in enumerate(rw):
        self.rowconfigure(i, weight=weight)
    for i, weight in enumerate(cw):
        self.columnconfigure(i, weight=weight)

def grid(obj, row=0, column=0, *args, **kwargs) -> None:
    """Sugar syntax for TKinter's grid function"""
    if 'sticky' not in kwargs:
        kwargs['sticky'] = 'NSEW'

    try:
        # Assume it's a TkinterPlus object
        obj._grid(*args, row=row, column=column, **kwargs)
    except AttributeError:
        obj.grid(*args, row=row, column=column, **kwargs)

class FuncDeclare():
    """Contains declarations for functions that get added
    The whole point is tell Pylance about these functions so that
    my monkey patching works
    Usage: when defining a new class, use 
        class some_new_class(tkinter.base_class, TKPlus):
            ..."""
    def gridconfigure(self, rw=None, cw=None) -> None: pass
    def grid(self, row=0, column=0, *args, **kwargs) -> None: pass

    # Implemented by tkinter itself, but Pylance doesn't know that
    _w: str

def add_functions(obj) -> None:
    # Use a flag to check if functionality has already been added
    if hasattr(obj, "_TkinterPlus"):
        return
    obj._TkinterPlus = True

    if hasattr(obj, "rowconfigure") and hasattr(obj, "columnconfigure"):
        obj.gridconfigure = gridconfigure
    if hasattr(obj, "grid"):
        obj._grid = obj.grid
        obj.grid = grid