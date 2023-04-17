import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
import paramiko

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
                if column_name == "Employee ID":
                    value = "N"
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
                if column_name == "Name":
                    value = value.upper()
                record.append(value)
            data.append(record)
        return data

def parse_fixed_width_file(file_path):
    colspecs = [(0, 10), (10, 60), (60, 69), (69, 75), (75, 85), (85, 95), (95, 103)]
    column_names = ["Agency Code", "Name", "Employee ID", "Deduction Code", "Effective Date", "Deduction End Date", "Deduction Amount"]
    df = pd.read_fwf(file_path, colspecs=colspecs, header=None, names=column_names)
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

def sftp_file(file_path, host, username, password):
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(file_path, "/remote/directory/" + file_path.split("/")[-1])
    sftp.close()
    transport.close()

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
        nonlocal file_path, df
        save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="paysrp.nben902.sccea.input")
        if not save_file_path:
            return
        data = editable_table.get_data()
        df = pd.DataFrame(data, columns=[col[0] for col in columns])
        save_data(df, save_file_path)

    def sftp_file_dialog():
        nonlocal file_path
        sftp_host = sftp_host_entry.get()
        sftp_username = sftp_username_entry.get()
        sftp_password = sftp_password_entry.get()
        if not file_path:
            messagebox.showerror("Error", "No file to upload. Please open or save a file first.")
            return
        sftp_file(file_path, sftp_host, sftp_username, sftp_password)
        messagebox.showinfo("Success", "File uploaded successfully.")

    def add_new_row():
        editable_table.add_row()

    def close_app():
        data = editable_table.get_data()
        new_df = pd.DataFrame(data, columns=[col[0] for col in columns])

        if not new_df.equals(df):
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes before closing?")
            if response is None:
                return
            elif response:
                save_file()

        root.destroy()

    open_button = tk.Button(root, text="Open", command=open_file)
    open_button.pack(side="left", padx=10)

    save_button = tk.Button(root, text="Save", command=save_file)
    save_button.pack(side="left", padx=10)

    add_button = tk.Button(root, text="Add Row", command=add_new_row)
    add_button.pack(side="left", padx=10)

    sftp_host_label = tk.Label(root, text="SFTP Host")
    sftp_host_label.pack(side="left", padx=10)
    sftp_host_entry = tk.Entry(root)
    sftp_host_entry.pack(side="left", padx=10)

    sftp_username_label = tk.Label(root, text="Username")
    sftp_username_label.pack(side="left", padx=10)
    sftp_username_entry = tk.Entry(root)
    sftp_username_entry.pack(side="left", padx=10)

    sftp_password_label = tk.Label(root, text="Password")
    sftp_password_label.pack(side="left", padx=10)
    sftp_password_entry = tk.Entry(root, show="*")
    sftp_password_entry.pack(side="left", padx=10)

    sftp_button = tk.Button(root, text="Upload via SFTP", command=sftp_file_dialog)
    sftp_button.pack(side="left", padx=10)

    exit_button = tk.Button(root, text="Exit", command=close_app)
    exit_button.pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
