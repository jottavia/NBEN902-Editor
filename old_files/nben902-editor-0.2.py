import tkinter as tk
from tkinter import filedialog
import pandas as pd

class EditableTable(tk.Frame):
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.columns = columns
        self.grid(sticky='nsew')
        self.create_widgets()

    def create_widgets(self):
        self.entries = []
        self.labels = []
        self.delete_buttons = []
        for col, (column_name, width) in enumerate(self.columns):
            label = tk.Label(self, text=column_name, relief='ridge')
            label.grid(row=0, column=col)
            self.labels.append(label)

    def load_data(self, df):
        self.clear_table()

        for row, record in df.iterrows():
            self.add_row(record)

    def add_row(self, record=None):
        entries_row = []
        for col, (column_name, width) in enumerate(self.columns):
            if record is None:
                value = ""
            elif pd.isna(record[column_name]) and column_name == "Deduction End Date":
                value = ""
            else:
                value = record[column_name]
            entry = tk.Entry(self, width=width)
            entry.insert(0, value)
            entry.grid(row=len(self.entries)+1, column=col)
            entries_row.append(entry)
        self.entries.append(entries_row)

        delete_button = tk.Button(self, text="Delete", command=lambda row=len(self.entries)-1: self.delete_row(row))
        delete_button.grid(row=len(self.entries), column=len(self.columns))
        self.delete_buttons.append(delete_button)

    def delete_row(self, row):
        for entry in self.entries[row]:
            entry.destroy()
        self.entries.pop(row)

        self.delete_buttons[row].destroy()
        self.delete_buttons.pop(row)

        for i in range(row, len(self.entries)):
            for col, entry in enumerate(self.entries[i]):
                entry.grid(row=i+1, column=col)
            self.delete_buttons[i].grid(row=i+1, column=len(self.columns))
            self.delete_buttons[i].config(command=lambda row=i: self.delete_row(row))

    def clear_table(self):
        for row in self.entries:
            for entry in row:
                entry.destroy()
        self.entries = []

        for button in self.delete_buttons:
            button.destroy()
        self.delete_buttons = []

    def get_data(self):
        data = []
        for row in self.entries:
            record = []
            for col, (column_name, width) in enumerate(self.columns):
                value = row[col].get()
                record.append(value)
            data.append(record)
        return data

def parse_fixed_width_file(file_path):
    colspecs = [(0, 10), (10, 60), (60, 69), (69, 75), (75, 85), (85, 95), (95, 103)]
    column_names = ["Agency Code", "Name", "Employee ID", "Deduction Code", "Effective Date", "Deduction End Date", "Deduction Amount"]
    df = pd.read_fwf(file_path, colspecs=colspecs, header=None, names=column_names)
    return df

def save_data(df, file_path):
    with open(file_path, "w") as file:
        for _, row in df.iterrows():
            row_str = ""
            for value in row:
                row_str += str(value)
            file.write(row_str + "\n")

def main():
    root = tk.Tk()
    root.title("Fixed-Width File Editor")

    file_path, df = None, pd.DataFrame()

    columns = [
        ("Agency Code", 10),
        ("Name", 50),
        ("Employee ID", 9),
        ("Deduction Code", 6),
        ("Effective Date", 10),
        ("Deduction End Date", 10),
        ("Deduction Amount", 8)
    ]
    editable_table = EditableTable(root, columns=columns)
    editable_table.pack(pady=20)

    def open_file():
        nonlocal file_path, df
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        df = parse_fixed_width_file(file_path)
        editable_table.load_data(df)

    def save_file():
        if not file_path or df.empty:
            return
        data = editable_table.get_data()
        df = pd.DataFrame(data, columns=[col[0] for col in columns])
        save_data(df, file_path)

    def add_new_row():
        editable_table.add_row()

    open_button = tk.Button(root, text="Open", command=open_file)
    open_button.pack(side="left", padx=10)

    save_button = tk.Button(root, text="Save", command=save_file)
    save_button.pack(side="left", padx=10)

    new_row_button = tk.Button(root, text="New Row", command=add_new_row)
    new_row_button.pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
