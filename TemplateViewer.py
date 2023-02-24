import Categorize
import TkinterPlus as gui

nest_templates = Categorize._nested_templates
# Get the longest name so the buttons can be sized appropriately
width = max(len(t.name) for t in nest_templates.flattened())
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

    trunk_map = {} ; trunk_map: dict[str, Categorize.TemplateSuperGroup]
    branch_map = {} ; branch_map: dict[str, Categorize.TemplateGroup]
    leaf_map = {} ; leaf_map: dict[str, Categorize.Template]
    # Fill the tree (nested version)
    def make_trunk(trunk_name: str, trunk: Categorize.TemplateSuperGroup, parent_id: str):
        trunk_id = tree.insert(parent=parent_id, index='end', text=trunk_name, tags='trunk', open=True)
        trunk_map[trunk_id] = trunk
        for branch_name, branch in trunk.items():
            make_branch(branch_name, branch, trunk_id)
    def make_branch(name: str, item: Categorize.TemplateGroup, parent_id: str):
        branch_id = tree.insert(parent=parent_id, index='end', text=name, tags='branch', open=True)
        branch_map[branch_id] = item
        for leaf in item:
            make_leaf(leaf, branch_id)
    def make_leaf(leaf: Categorize.Template, parent_id: str):
        assert isinstance(leaf, Categorize.Template)
        if leaf.name:
            name = leaf.name
            tags = 'leaf'
        else:
            name = leaf.pattern['desc']
            tags = ['leaf', 'auto_leaf']
        leaf_id = tree.insert(parent=parent_id, index='end', text=name, tags=tags, open=True)
        leaf_map[leaf_id] = leaf
    for trunk_name, trunk in nest_templates.items():
        make_trunk(trunk_name, trunk, '')
    
    # Make non-leaves bold
    tree.tag_configure('trunk', font=bold)
    tree.tag_configure('branch', font=bold)

    # Make auto-leaves italic
    tree.tag_configure('auto_leaf', font=italic)

    # Tree callback
    def on_select(_):
        selection = tree.selection()

        # Ignore multi-selection for now
        if len(selection) != 1: return placeholder_detail()

        id, = selection
        tree_item = tree.item(id)
        tags = tree_item['tags']
        if 'trunk' in tags:
            return trunk_gui(id)
        elif 'branch' in tags:
            return branch_gui(id)
        elif 'leaf' in tags:
            return leaf_gui(id)
        else:
            raise RuntimeError()

    tree.bind('<<TreeviewSelect>>', on_select)

    # Detail pane
    def placeholder_detail():
        frame = detail_frame
        frame.clear()
        label = gui.tkinter.Label(frame, text='Select a Template to view', font=bold)
        label.pack(side='top', anchor='center', fill='both', expand=True)
    def trunk_gui(id: str):
        trunk = trunk_map[id]
        return placeholder_detail()
    def branch_gui(id: str):
        branch = branch_map[id]
        def add_template_cb():
            make_leaf(Categorize.Template(name='Newly Created', pattern=dict(), new=dict()), parent_id=id)
        frame = detail_frame
        frame.clear()
        button = gui.Button(frame, text='Add new template', command=add_template_cb)
        button.place(relx=0.5, rely=0.5, anchor='center')
    def leaf_gui(id: str):
        t = leaf_map[id]
        t: Categorize.Template
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