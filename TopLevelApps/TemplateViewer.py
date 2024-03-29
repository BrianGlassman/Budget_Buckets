from functools import partial

from Handlers import Categorize
import TkinterPlus as gui

nest_templates = Categorize.get_all_templates()
# Get the longest name so the buttons can be sized appropriately
width = max(len(t.name) for t in nest_templates.flattened())
# Adjust to account for indenting
# width += 16

bd = 10

bold = ('', 0, 'bold')
italic = ('', 0, 'italic')

class TemplateViewer(gui.Root):
    detail_frame: gui.Frame
    trunk_map: dict[str, Categorize.TemplateSuperGroup]
    branch_map: dict[str, Categorize.TemplateGroup]
    leaf_map: dict[str, Categorize.Template]
    def __init__(self):
        super().__init__(20, 15, "Templates")

        # Create everything first
        outer_frame = gui.Frame(self, name='outer_frame',
            bg='black', bd=bd, relief='ridge',)
        self.tree = gui.TreeviewScrollable(outer_frame, show='tree', vscroll='left', hscroll='bottom')
        self.detail_frame = gui.Frame(self, name='detail_frame',
            bg='yellow', bd=bd, relief='ridge')

        self.trunk_map = {}
        self.branch_map = {}
        self.leaf_map = {}
        # Fill the tree (nested version)
        for templateFile in nest_templates.files:
            for trunk_name, trunk in templateFile.items():
                self.make_trunk(trunk_name, trunk, '')
        
        # Make non-leaves bold
        self.tree.tag_configure('trunk', font=bold)
        self.tree.tag_configure('branch', font=bold)

        # Make auto-leaves italic
        self.tree.tag_configure('auto_leaf', font=italic)

        # Tree callback
        def on_select(_):
            selection = self.tree.selection()

            # Ignore multi-selection for now
            if len(selection) != 1: return self.placeholder_detail()

            id, = selection
            tree_item = self.tree.item(id)
            tags = tree_item['tags']
            if 'trunk' in tags:
                return self.trunk_gui(id=id)
            elif 'branch' in tags:
                return self.branch_gui(id=id)
            elif 'leaf' in tags:
                return self.leaf_gui(id=id)
            else:
                raise RuntimeError()

        self.tree.bind('<<TreeviewSelect>>', on_select)

        # Pack everything
        outer_frame.pack(side='left', fill='y', expand=False)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.column('#0', stretch=False)
        self.detail_frame.pack(side='left', fill='both', expand=True)

        # Initialize detail frame
        self.placeholder_detail()

        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.mainloop()

    
    def make_trunk(self, trunk_name: str, trunk: Categorize.TemplateSuperGroup, parent_id: str):
        trunk_id = self.tree.insert(parent=parent_id, index='end', text=trunk_name, tags='trunk', open=True)
        self.trunk_map[trunk_id] = trunk
        for branch_name, branch in trunk.items():
            self.make_branch(branch_name, branch, trunk_id)
    def make_branch(self, name: str, item: Categorize.TemplateGroup, parent_id: str):
        branch_id = self.tree.insert(parent=parent_id, index='end', text=name, tags='branch', open=True)
        self.branch_map[branch_id] = item
        for leaf in item:
            self.make_leaf(leaf, branch_id)
    def make_leaf(self, leaf: Categorize.Template, parent_id: str):
        assert isinstance(leaf, Categorize.Template)
        if leaf.name:
            name = leaf.name
            tags = 'leaf'
        else:
            name = leaf.pattern['desc']
            tags = ['leaf', 'auto_leaf']
        leaf_id = self.tree.insert(parent=parent_id, index='end', text=name, tags=tags, open=True)
        self.leaf_map[leaf_id] = leaf

    def placeholder_detail(self):
        frame = self.detail_frame
        frame.clear()
        label = gui.tkinter.Label(frame, text='Select a Template to view', font=bold)
        label.pack(side='top', anchor='center', fill='both', expand=True)
    def trunk_gui(self, id: str):
        trunk = self.trunk_map[id]
        return self.placeholder_detail()

    def branch_gui(self, id: str):
        frame = self.detail_frame
        branch = self.branch_map[id]
        def add_template_cb():
            template = Categorize.Template(name='Newly Created', pattern=dict(), new=dict())
            branch.append(template)
            self.make_leaf(template, parent_id=id)
        frame = frame
        frame.clear()
        button = gui.Button(frame, text='Add new template', command=add_template_cb)
        button.place(relx=0.5, rely=0.5, anchor='center')

    def leaf_gui(self, id: str, edit=False):
        t = self.leaf_map[id]
        t: Categorize.Template
        frame = self.detail_frame
        frame.clear()

        def edit_cb():
            self.leaf_gui(id=id, edit=True)
        def lock_cb():
            self.leaf_gui(id=id, edit=False)

        # The header bar with the Template name and Edit/Lock button
        top_frame = gui.Frame(master=frame)
        top_frame.pack(side='top', anchor='n', fill='x', expand=False)
        # The Edit/Lock button
        if edit:
            button = gui.Button(top_frame, text='Lock', command=lock_cb)
        else:
            button = gui.Button(top_frame, text='Edit', command=edit_cb)
        button.pack(side='left', fill='none', expand=False)
        # The Template name
        if edit:
            var = gui.tkinter.StringVar(value = t.name)
            name = gui.Entry(top_frame, textvariable=var, font=bold, anchor='center')
            def cb(*_, t: Categorize.Template):
                t.name = var.get()
            var.trace_add('write', partial(cb, t=t))
        else:
            name = gui.tkinter.Label(top_frame, text=t.name, font=bold, anchor='center')
        name.pack(side='left', anchor='center', fill='x', expand=True)

        def make_locked_sub(title: str, pattern: Categorize.BasePattern, parent: gui.Frame | None = frame):
            """Makes the sub-window for one of the items"""
            frame = gui.Frame(parent)
            label = gui.tkinter.Label(frame, text=title, font=bold, anchor='center', relief='groove')
            label.pack(side='top', anchor='n', fill='x', expand=False)
            # Use as_dict to get only the filled items
            for k,v in pattern.as_dict().items():
                label = gui.tkinter.Label(frame, text=k.capitalize(), anchor='w', font=bold)
                label.pack(side='top', anchor='w')
                value = gui.tkinter.Label(frame, text=str(v), anchor='w')
                value.pack(side='top', anchor='w', fill='x', expand=False)
            frame.pack(side='left', fill='both', expand=True)
            return frame
        
        def make_edit_sub(title: str, pattern: Categorize.BasePattern, parent: gui.Frame | None = frame):
            """Makes the sub-window for editing one of the items"""
            frame = gui.Frame(parent)
            label = gui.tkinter.Label(frame, text=title, font=bold, anchor='center', relief='groove')
            label.pack(side='top', anchor='n', fill='x', expand=False)
            # Use field_dict to get all items, even the unfilled ones
            for k in pattern.field_dict().keys():
                label = gui.tkinter.Label(frame, text=k.capitalize(), anchor='w', font=bold)
                label.pack(side='top', anchor='w')
                
                def do_stuff(frame, pattern: Categorize.BasePattern, k):
                    """Use a function because otherwise Tkinter messes up the callbacks"""
                    filled_val = pattern.get(k, '')
                    var = gui.tkinter.StringVar(value=filled_val)
                    entry = gui.Entry(frame, textvariable=var, anchor='w')
                    entry.pack(side='top', anchor='w', fill='x', expand=False)

                    def cb(*_, key: str):
                        val = var.get()
                        valid = True
                        if val == '':
                            pattern.clear(key)
                        else:
                            valid = pattern.try_set(key, value=val)
                        entry['bg'] = '#ffffff' if valid else '#ffc8c8'
                    var.trace_add('write', partial(cb, key=k))
                do_stuff(frame=frame, pattern=pattern, k=k)
            frame.pack(side='left', fill='both', expand=True)
            return frame
        
        def make_sub(title: str, pattern: Categorize.BasePattern, parent: gui.Frame | None = frame):
            if edit:
                return make_edit_sub(title=title, pattern=pattern, parent=parent)
            else:
                return make_locked_sub(title=title, pattern=pattern, parent=parent)

        # Pattern
        pattern_frame = make_sub('Pattern', t.pattern)

        # New
        new_frame = make_sub('New', t.new)

        # Create
        create_frame = None
        if t.create or edit:
            create_frame = gui.Frame(frame)
            create_frame.pack(side='left', fill='y', expand=False)
        for i,c in enumerate(t.create):
            make_sub(f'Create {i}', c, parent=create_frame)
        if edit:
            def create_cb():
                t.create.append(Categorize.Create())
                make_sub(f'Create {len(t.create)-1}', t.create[-1], parent=create_frame)
            create_button = gui.Button(create_frame, text='+', command=create_cb)
            create_button.pack(side='right', fill='y', expand=False)
    
    def on_close(self):
        Categorize.save_all_templates()
        self.destroy()

if __name__ == '__main__':
    TemplateViewer()