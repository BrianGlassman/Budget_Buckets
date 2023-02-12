import Categorize
import TkinterPlus as gui

templates = Categorize._templates
# Get the longest name so the buttons can be sized appropriately
width = max(len(t['name']) for t in templates)

root = gui.Root(10, 10, "Templates")

bd = 10

# Create everything first
outer_frame = gui.Frame(root, name='outer_frame',
    bg='black', bd=bd, relief='ridge')
canvas = gui.Canvas(outer_frame, name='canvas',
    bg='cyan', bd=0, relief='ridge')
scroll = gui.tkinter.Scrollbar(outer_frame, orient='vertical', command=canvas.yview)
inner_frame = gui.Frame(canvas, name='inner_frame',
    bg='green', bd=bd, relief='ridge')
window = canvas.create_window(0, 0, window=inner_frame, anchor='nw')
buttons = [gui.Button(inner_frame, text=t['name'], width=width) for t in templates if t['name']]
detail_frame = gui.Frame(root, name='detail_frame',
    bg='yellow', bd=bd, relief='ridge')

# Connect the scrollbar to things
canvas.configure(yscrollcommand=scroll.set)
inner_frame.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')), add=True)

# Make canvas match inner_frame size
inner_frame.bind('<Configure>', lambda e: canvas.configure(width=e.width, height=e.height), add=True)

# Pack everything
outer_frame.pack(side='left', fill='y', expand=False)
scroll.pack(side='left', fill='y', expand=False)
canvas.pack(side='left', fill='both', expand=True)
# inner_frame.pack(side='left', fill='none', expand=False)
for b in buttons: b.pack()
detail_frame.pack(side='left', fill='both', expand=True)

root.mainloop()