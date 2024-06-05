import tkinter as tk
from tkinter import messagebox, ttk

class MemberSelector(tk.Toplevel):
    def __init__(self, parent, members_df):
        super().__init__(parent)
        self.title("Select Members")
        self.geometry("300x400")
        self.members_df = members_df
        self.selected_members = []

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill='both')

        self.tree = ttk.Treeview(self.frame, columns=('Name',), show='headings', selectmode='none')
        self.tree.heading('Name', text='Name')
        self.tree.pack(side="left", expand=True, fill="both")

        self.scrollbar_y = tk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

        for index, row in self.members_df.iterrows():
            self.tree.insert('', tk.END, values=(row['Name'],), iid=index)

        self.tree.bind('<Button-1>', self.on_click)

        self.select_button = tk.Button(self, text="Select", command=self.select_members)
        self.select_button.pack(pady=5)

    def on_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if self.tree.selection() and item in self.tree.selection():
                self.tree.selection_remove(item)
            else:
                self.tree.selection_add(item)

    def select_members(self):
        selected_items = self.tree.selection()
        self.selected_members = [self.members_df.iloc[int(item)].to_dict() for item in selected_items]
        if not self.selected_members:
            messagebox.showwarning("No selection", "No members selected.")
            return
        self.destroy()

    def get_selected_members(self):
        return self.selected_members
