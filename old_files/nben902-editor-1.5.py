import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
import subprocess
import os

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x = y = 0
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, justify='left', background='#ffffe0', relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class EditableTable(tk.Frame):
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.columns = columns
        self.grid(sticky='nsew')
        self.create_widgets()
        self.effective_date = ""

    def create_widgets(self):
        self.entries = []
        self.labels = []
        self.delete_buttons = []
        self.duplicate_buttons = []

        tooltips = {
            "Agency Code": "Agency Code for Suffolk County is 05527\nAgency Code for the Academy is 05007",
            "Deduction Code": "456 for union dues\n407 for the PAC fund",
            "Effective Date": "The Thursday after the last payday",
            "Deduction End Date": "Can be the Thursday after the last payday"
        }

        for col, (column_name, width) in enumerate(self.columns):
            label = tk.Label(self, text=column_name, relief='ridge')
            label.grid(row=0, column=col + 1)  # Updated column to add space for Duplicate button
            self.labels.append(label)

            if column_name in tooltips:
                ToolTip(label, tooltips[column_name])

    def load_data(self, df):
        self.clear_table()
        for row, record in df.iterrows():
            self.add_row(record)

    def add_row(self, record=None, row_idx=None):
        if row_idx is None:
            row_idx = len(self.entries)

        duplicate_button = tk.Button(self, text="Duplicate", command=lambda row=row_idx: self.duplicate_row(row))
        duplicate_button.grid(row=row_idx + 1, column=0)  # Moved duplicate button to the left of the row
        self.duplicate_buttons.insert(row_idx, duplicate_button)

        entries_row = []
        for col, (column_name, width) in enumerate(self.columns):
            if record is None:
                if column_name == "Employee ID":
                    value = "N"
                elif column_name == "Effective Date":
                    value = self.effective_date
                else:
                    value = ""
            elif pd.isna(record[column_name]) and column_name == "Deduction End Date":
                value = ""
            else:
                value = record[column_name]
                if column_name == "Name":
                    value = value.upper()
            entry = tk.Entry(self, width=width)
            entry.insert(0, value)
            entry.grid(row=row_idx + 1, column=col + 1)  # Updated column to add space for Duplicate button

            if column_name == "Effective Date":
                entry.bind("<FocusOut>", lambda event, row=row_idx, col=col: self.update_effective_date(row, col))

            entries_row.append(entry)
        self.entries.insert(row_idx, entries_row)

        delete_button = tk.Button(self, text="Delete", command=lambda row=row_idx: self.delete_row(row))
        delete_button.grid(row=row_idx + 1, column=len(self.columns) + 1)
        self.delete_buttons.insert(row_idx, delete_button)

        # Update the positions of the subsequent rows
        for i in range(row_idx + 1, len(self.entries)):
            for col, entry in enumerate(self.entries[i]):
                entry.grid(row=i + 1, column=col + 1)  # Updated column to add space for Duplicate button
            self.delete_buttons[i].grid(row=i + 1, column=len(self.columns) + 1)
            self.delete_buttons[i].config(command=lambda row=i: self.delete_row(row))

            self.duplicate_buttons[i].grid(row=i + 1, column=0)  # Moved duplicate button to the left of the row
            self.duplicate_buttons[i].config(command=lambda row=i: self.duplicate_row(row))

    def update_effective_date(self, row, col):
        effective_date = self.entries[row][col].get()
        if re.match(r'^\d{2}-\d{2}-\d{4}$', effective_date):
            self.effective_date = effective_date
            for r in range(len(self.entries)):
                self.entries[r][col].delete(0, tk.END)
                self.entries[r][col].insert(0, effective_date)

    def delete_row(self, row):
        for entry in self.entries[row]:
            entry.destroy()
        self.entries.pop(row)

        self.delete_buttons[row].destroy()
        self.delete_buttons.pop(row)

        self.duplicate_buttons[row].destroy()
        self.duplicate_buttons.pop(row)

        for i in range(row, len(self.entries)):
            for col, entry in enumerate(self.entries[i]):
                entry.grid(row=i + 1, column=col + 1)  # Updated column to add space for Duplicate button
            self.delete_buttons[i].grid(row=i + 1, column=len(self.columns) + 1)
            self.delete_buttons[i].config(command=lambda row=i: self.delete_row(row))

            self.duplicate_buttons[i].grid(row=i + 1, column=0)  # Moved duplicate button to the left of the row
            self.duplicate_buttons[i].config(command=lambda row=i: self.duplicate_row(row))

    def duplicate_row(self, row):
        record_values = [entry.get() for entry in self.entries[row]]
        record = pd.Series(record_values, index=[col[0] for col in self.columns])

        # Update specific values for the duplicated row
        record["Deduction Code"] = "407"
        record["Deduction Amount"] = "100"

        self.add_row(record, row + 1)

    def clear_table(self):
        for row in self.entries:
            for entry in row:
                entry.destroy()
        self.entries = []

        for button in self.delete_buttons:
            button.destroy()
        self.delete_buttons = []

        for button in self.duplicate_buttons:
            button.destroy()
        self.duplicate_buttons = []

    def get_data(self):
        data = []
        for row_idx, row in enumerate(self.entries):
            record = []
            for col, (column_name, width) in enumerate(self.columns):
                value = row[col].get()

                if not self.validate_value(column_name, value):
                    messagebox.showerror("Input Validation Error", f"Invalid value for {column_name} at row {row_idx + 1}.")
                    return None

                if column_name == "Name":
                    value = value.upper()
                record.append(value)
            data.append(record)
        return data

    @staticmethod
    def validate_value(column_name, value):
        if column_name == "Agency Code":
            return bool(value)
        elif column_name == "Name":
            return bool(value)
        elif column_name == "Employee ID":
            return re.match(r'^N\d{8}$', value)
        elif column_name == "Deduction Code":
            return bool(value)
        elif column_name == "Effective Date":
            return re.match(r'^\d{2}-\d{2}-\d{4}$', value)
        elif column_name == "Deduction End Date":
            return value == "" or re.match(r'^\d{2}-\d{2}-\d{4}$', value)
        elif column_name == "Deduction Amount":
            return value.replace(".", "", 1).isdigit() and float(value) > 0
        else:
            return False

def parse_fixed_width_file(file_path):
    colspecs = [(0, 10), (10, 60), (60, 69), (69, 75), (75, 85), (85, 95), (95, 103)]
    column_names = ["Agency Code", "Name", "Employee ID", "Deduction Code", "Effective Date", "Deduction End Date", "Deduction Amount"]
    df = pd.read_fwf(file_path, colspecs=colspecs, header=None, names=column_names, converters={'Agency Code': str})
    return df

def save_data(df, file_path):
    col_widths = [10, 50, 9, 6, 10, 10, 8]
    with open(file_path, "w") as file:
        for _, row in df.iterrows():
            row_str = ""
            for idx, value in enumerate(row):
                if idx == 4 or idx == 5:  # Effective Date and Deduction End Date columns
                    if value == "":
                        value = " " * col_widths[idx]
                if idx == 6:  # Deduction Amount field
                    formatted_value = str(value).rjust(col_widths[idx], '0')
                else:
                    formatted_value = str(value).ljust(col_widths[idx], ' ')
                row_str += formatted_value[:col_widths[idx]]
            file.write(row_str + "\n")

def main():
    root = tk.Tk()
    root.title("Fixed-Width File Editor")
    root.geometry("1000x600")

    file_path, df = None, pd.DataFrame()

    columns = [
        ("Agency Code", 10),
        ("Name", 50),
        ("Employee ID", 10),
        ("Deduction Code", 6),
        ("Effective Date", 10),
        ("Deduction End Date", 10),
        ("Deduction Amount", 8)
    ]

    def open_file():
        nonlocal file_path, df
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        df = parse_fixed_width_file(file_path)
        editable_table.load_data(df)

    def save_file():
        nonlocal file_path, df
        save_file_path = filedialog.asksaveasfilename(initialfile=os.path.basename(file_path))
        if not save_file_path:
            return
        data = editable_table.get_data()
        if data is None:
            return
        df = pd.DataFrame(data, columns=[col[0] for col in columns])
        save_data(df, save_file_path)

    def add_new_row():
        nonlocal editable_table
        editable_table.add_row()

    def convert_902():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            subprocess.run(["convert-902.exe"], check=True, cwd=current_directory)
        except Exception as e:
            messagebox.showerror("Error", f"Error running convert-902: {str(e)}")

    def transmit_902():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            subprocess.run(["902-sftp.exe"], check=True, cwd=current_directory)
        except Exception as e:
            messagebox.showerror("Error", f"Error running 902-sftp: {str(e)}")

    def close_app():
        data = editable_table.get_data()
        if data is None:
            return
        new_df = pd.DataFrame(data, columns=[col[0] for col in columns])

        if not new_df.equals(df):
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes before closing?")
            if response is None:
                return
            elif response:
                save_file()

        root.destroy()

    # Button Frame
    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=0, sticky="nw")

    open_button = tk.Button(button_frame, text="Open", command=open_file)
    open_button.pack(side="left", padx=(10, 5), pady=5)

    save_button = tk.Button(button_frame, text="Save", command=save_file)
    save_button.pack(side="left", padx=(0, 5), pady=5)

    add_row_button = tk.Button(button_frame, text="Add Row", command=add_new_row)
    add_row_button.pack(side="left", padx=(0, 5), pady=5)

    convert_902_button = tk.Button(button_frame, text="Convert-902", command=convert_902)
    convert_902_button.pack(side="left", padx=(0, 5), pady=5)

    transmit_902_button = tk.Button(button_frame, text="Transmit 902", command=transmit_902)
    transmit_902_button.pack(side="left", padx=(0, 5), pady=5)

    exit_button = tk.Button(button_frame, text="Exit", command=root.quit)
    exit_button.pack(side="left", padx=(0, 10), pady=5)

    # Table Frame
    table_frame = tk.Frame(root)
    table_frame.grid(row=1, column=0, sticky="nsew")

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(table_frame)
    canvas.grid(row=0, column=0, sticky="nsew")

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    editable_table = EditableTable(canvas, columns=columns)
    canvas.create_window((0, 0), window=editable_table, anchor="nw")

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    editable_table.bind("<Configure>", update_scrollregion)

    scrollbar_y = tk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollbar_x.grid(row=2, column=0, sticky="ew")
    canvas.configure(xscrollcommand=scrollbar_x.set)

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()

if __name__ == "__main__":
    main()
