
import tkinter
from tkinter import ttk

root = tkinter.Tk()
label = tkinter.Label(root, text="test")
label.pack(side=tkinter.LEFT)

# Entry version
#entry = tkinter.Entry(master=root, bd=5)
#entry.pack(side=tkinter.RIGHT)

# Combobox version
cb = ttk.Combobox(master = root)
cb.pack(side=tkinter.RIGHT)
cb['state'] = 'readonly' # disallow custom input
cb['values'] = ['alpha', 'beta', 'gamma']

def on_modification(event: tkinter.Event):
    text = event.widget.get()

    print(f"Set value to {text}")
cb.bind("<<ComboboxSelected>>", on_modification)

root.mainloop()