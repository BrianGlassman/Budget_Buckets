import Categorize
import TkinterPlus as gui

nest_templates = Categorize._nested_templates
flat_templates = Categorize._templates
# Get the longest name so the buttons can be sized appropriately
width = max(len(t.name) for t in flat_templates)
# Adjust to account for indenting
# width += 16

bd = 10

bold = ('', 0, 'bold')
italic = ('', 0, 'italic')

def run():
    root = gui.Root(20, 15, "Templates")

    # Create everything first
    outer_frame = gui.Frame(root, name='outer_frame',
        bg='black', bd=bd, relief='ridge',)
    tree = gui.TreeviewScrollable(outer_frame, show='tree', vscroll='left', hscroll='bottom')
    detail_frame = gui.Frame(root, name='detail_frame',
        bg='yellow', bd=bd, relief='ridge')

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
        tree.insert(parent='', index='end', text=trunk_name, tags='trunk')
        for branch_name, branch in trunk.items():
            tree.insert(parent='', index='end', text=' '+branch_name, tags='branch')
            for leaf in branch:
                assert isinstance(leaf, Categorize.Template)
                if leaf.name:
                    leaf_name = leaf.name
                    tags = 'leaf'
                else:
                    leaf_name = leaf.pattern['desc']
                    tags = ['leaf', 'auto_leaf']
                leaf_id = tree.insert(parent='', index='end', text='   '+leaf_name, tags=tags)
                leaf_map[leaf_id] = leaf
    # Make non-leaves bold
    tree.tag_configure('trunk', font=bold)
    tree.tag_configure('branch', font=bold)

    # Make auto-leaves italic
    tree.tag_configure('auto_leaf', font=italic)

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
        name = gui.tkinter.Label(frame, text=t.name, font=bold, anchor='center')
        name.pack(side='top', anchor='n', fill='x', expand=False)

        def make_sub(title: str, dct: dict):
            frame = gui.Frame(detail_frame)
            label = gui.tkinter.Label(frame, text=title, font=bold, anchor='center', relief='groove')
            label.pack(side='top', anchor='n', fill='x', expand=False)
            for k,v in dct.items():
                label = gui.tkinter.Label(frame, text=k.capitalize(), anchor='w', font=bold)
                label.pack(side='top', anchor='w')
                value = gui.tkinter.Label(frame, text=str(v), anchor='w')
                value.pack(side='top', anchor='w', fill='x', expand=False)
            frame.pack(side='left', fill='both', expand=True)

        make_sub('Pattern', t.pattern)
        make_sub('New', t.new)
        for i,c in enumerate(t.create):
            make_sub(f'Create {i}', c)

    # Pack everything
    outer_frame.pack(side='left', fill='y', expand=False)
    tree.pack(side='left', fill='both', expand=True)
    tree.column('#0', stretch=False)
    detail_frame.pack(side='left', fill='both', expand=True)

    # Initialize detail frame
    placeholder_detail()

    root.mainloop()

if __name__ == '__main__':
    run()