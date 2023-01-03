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