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

bold = ('', 0, 'bold')

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

leaf_map = {}
# Fill the tree (nested version)
# for trunk_name, trunk in nest_templates.items():
#     trunk_id = tree.insert(parent='', index='end', text=trunk_name, tags='trunk')
#     for branch_name, branch in trunk.items():
#         branch_id = tree.insert(parent=trunk_id, index='end', text=branch_name, tags='branch')
#         for leaf in branch:
#             assert isinstance(leaf, Categorize.Template)
#             leaf_id = tree.insert(parent=branch_id, index='end', text=leaf.name, tags='leaf')
#             leaf_map[leaf_id] = leaf
# Fill the tree (flat version)
for trunk_name, trunk in nest_templates.items():
    trunk_id = tree.insert(parent='', index='end', text=trunk_name, tags='trunk')
    for branch_name, branch in trunk.items():
        branch_id = tree.insert(parent='', index='end', text=branch_name, tags='branch')
        for leaf in branch:
            assert isinstance(leaf, Categorize.Template)
            leaf_id = tree.insert(parent='', index='end', text=leaf.name, tags='leaf')
            leaf_map[leaf_id] = leaf
# Make non-leaves bold
tree.tag_configure('trunk', font=bold)
tree.tag_configure('branch', font=bold)

# Tree callback
def on_select(_):
    selection = tree.selection()

    # Only care about when single Templates (leaves) are selected
    if len(selection) != 1: return placeholder_detail()
    id, = selection
    tree_item = tree.item(id)
    if 'leaf' not in tree_item['tags']: return placeholder_detail()

    t = leaf_map[id]
    return make_detail(t)
tree.bind('<<TreeviewSelect>>', on_select)

# Detail pane
def placeholder_detail():
    frame = detail_frame
    frame.clear()
    label = gui.tkinter.Label(frame, text='Select a Template to view', font=bold)
    label.pack(side='top', anchor='center', fill='both', expand=True)
def make_detail(t: Categorize.Template):
    frame = detail_frame
    frame.clear()
    name = gui.tkinter.Label(frame, text=t.name, font=bold)
    name.pack(side='top', anchor='nw', fill='x', expand=False)
    for k,v in t.as_dict().items():
        if k == name: continue
        label = gui.tkinter.Label(frame, text=k.capitalize(), anchor='w', font=bold)
        label.pack(side='top', anchor='w')
        value = gui.tkinter.Label(frame, text=str(v), anchor='w')
        value.pack(side='top', anchor='w', fill='x', expand=False)

# Pack everything
outer_frame.pack(side='left', fill='y', expand=False)
vscroll.pack(side='left', fill='y', expand=False)
hscroll.pack(side='bottom', fill='x', expand=False)
tree.pack(side='left', fill='both', expand=True)
tree.column('#0', stretch=False)
detail_frame.pack(side='left', fill='both', expand=True)

# Initialize detail frame
placeholder_detail()

root.mainloop()