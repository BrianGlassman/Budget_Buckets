import Categorize
import TkinterPlus as gui

nest_templates = Categorize._nested_templates
flat_templates = Categorize._templates
# Get the longest name so the buttons can be sized appropriately
width = max(len(t.name) for t in flat_templates)
# Adjust to account for indenting
# width += 16

root = gui.Root(10, 10, "Templates")

bd = 10

# Create everything first
outer_frame = gui.Frame(root, name='outer_frame',
    bg='black', bd=bd, relief='ridge',)
tree = gui.ttk.Treeview(outer_frame, show='tree')
vscroll = gui.tkinter.Scrollbar(outer_frame, orient='vertical', command=tree.yview)
hscroll = gui.tkinter.Scrollbar(outer_frame, orient='horizontal', command=tree.xview)
detail_frame = gui.Frame(root, name='detail_frame',
    bg='yellow', bd=bd, relief='ridge')

# Connect the scrollbar to things
tree.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)

# Fill the tree
for trunk_name, trunk in nest_templates.items():
    trunk_id = tree.insert(parent='', index='end', text=trunk_name, tags='trunk')
    for branch_name, branch in trunk.items():
        branch_id = tree.insert(parent=trunk_id, index='end', text=branch_name, tags='branch')
        for leaf in branch:
            assert isinstance(leaf, Categorize.Template)
            tree.insert(parent=branch_id, index='end', text=leaf.name, tags='leaf')
tree.tag_configure('trunk', font=('', 0, 'bold'))
tree.tag_configure('branch', font=('', 0, 'bold'))

# Pack everything
outer_frame.pack(side='left', fill='y', expand=False)
vscroll.pack(side='left', fill='y', expand=False)
hscroll.pack(side='bottom', fill='x', expand=False)
tree.pack(side='left', fill='both', expand=True)
tree.column('#0', stretch=False)
detail_frame.pack(side='left', fill='both', expand=True)

root.mainloop()