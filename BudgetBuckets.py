#%% Parsing
import Parsing

parser = Parsing.USAAParser("USAA Credit Card", "cc.csv")

#%% Display
import TkinterPlus as gui

root = gui.Root(10, 10)

table = gui.ScrollableFrame(root)
table.pack(side = "top", fill="both", expand=True)
table.populate()

root.mainloop()
