import tkinter as tk
from tkinter import messagebox
import pandas as pd
import re
from utils import ToolTip

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
            return value == "" or re.match(r'^\d{2}-\d{2}-\d{4}$', value)
        elif column_name == "Deduction End Date":
            return value == "" or re.match(r'^\d{2}-\d{2}-\d{4}$', value)
        elif column_name == "Deduction Amount":
            return value.replace(".", "", 1).isdigit() and float(value) > 0
        else:
            return False
