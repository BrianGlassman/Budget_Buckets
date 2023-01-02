#%% Parsing
import Parsing

parser = Parsing.USAAParser("USAA CC", "cc.csv")

#%% Display
import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side = "top", fill="both", expand=True)

# Populate the table
widths = [10, 10, 60, 8]
for r, row in enumerate(parser.transactions):
    for c, cell in enumerate(row.values()):
        if c == 0: continue # Skip the Account
        if c == 4: continue # Skip the source-specific data
        if c < len(widths):
            gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1, width=widths[c]).grid(row=r, column=c)
        else:
            gui.tkinter.Label(table.frame, text = str(cell), anchor = 'w', relief='solid', bd = 1).grid(row=r, column=c)

root.mainloop()
