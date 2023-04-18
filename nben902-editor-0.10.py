import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
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

    with open(file_path, 'w') as f:
        for _, row in df.iterrows():
            for col, (column_name, width) in enumerate(zip(df.columns, col_widths)):
                value = str(row[column_name])
                if column_name == "Name":
                    value = value.upper()
                if column_name == "Deduction Amount":
                    value = value.zfill(width)
                value = value[:width]
                f.write(value)
            f.write('\n')

def sftp_file(file_path, hostname, port, username, password, remote_dir):
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    remote_path = remote_dir + '/' + file_path.split('/')[-1]
    sftp.put(file_path, remote_path)
    sftp.close()
    transport.close()

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        global current_file_path
        current_file_path = file_path
        df = parse_fixed_width_file(file_path)
        table.load_data(df)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".input", initialfile="paysrp.nben902.sccea.input")
    if file_path:
        data = table.get_data()
        df = pd.DataFrame(data, columns=[column_name for column_name, _ in table.columns])
        save_data(df, file_path)
        messagebox.showinfo("Success", "File saved successfully!")

def sftp_file_button():
    file_path = filedialog.askopenfilename()
    if file_path:
        hostname = sftp_hostname_entry.get()
        port = int(sftp_port_entry.get())
        username = sftp_username_entry.get()
        password = sftp_password_entry.get()
        remote_dir = remote_directory_entry.get()
        sftp_file(file_path, hostname, port, username, password, remote_dir)
        messagebox.showinfo("Success", "File transferred successfully!")

def main():
    global root
    root = tk.Tk()
    root.title("902 Editor")
    root.geometry("800x600")

    global table
    table = EditableTable(root, [("Agency Code", 10), ("Name", 50), ("Employee ID", 9), ("Deduction Code", 6), ("Effective Date", 10), ("Deduction End Date", 10), ("Deduction Amount", 8)])
    table.pack(side="top", fill="both", expand=True)

    open_button = tk.Button(root, text="Open", command=open_file)
    open_button.pack(side="left", padx=10)

    save_button = tk.Button(root, text="Save", command=save_file)
    save_button.pack(side="left", padx=10)

    new_row_button = tk.Button(root, text="New Row", command=table.add_row)
    new_row_button.pack(side="left", padx=10)

    sftp_frame = tk.Frame(root)
    sftp_frame.pack(side="top", fill="x", pady=10)

    sftp_hostname_label = tk.Label(sftp_frame, text="SFTP Hostname")
    sftp_hostname_label.pack(side="left", padx=10)

    sftp_hostname_entry = tk.Entry(sftp_frame)
    sftp_hostname_entry.pack(side="left", padx=10)

    sftp_port_label = tk.Label(sftp_frame, text="SFTP Port")
    sftp_port_label.pack(side="left", padx=10)

    sftp_port_entry = tk.Entry(sftp_frame)
    sftp_port_entry.pack(side="left", padx=10)

    sftp_username_label = tk.Label(sftp_frame, text="SFTP Username")
    sftp_username_label.pack(side="left", padx=10)

    sftp_username_entry = tk.Entry(sftp_frame)
    sftp_username_entry.pack(side="left", padx=10)

    sftp_password_label = tk.Label(sftp_frame, text="SFTP Password")
    sftp_password_label.pack(side="left", padx=10)

    sftp_password_entry = tk.Entry(sftp_frame, show="*")
    sftp_password_entry.pack(side="left", padx=10)

    remote_directory_label = tk.Label(sftp_frame, text="Remote Directory")
    remote_directory_label.pack(side="left", padx=10)

    remote_directory_entry = tk.Entry(sftp_frame)
    remote_directory_entry.pack(side="left", padx=10)

    sftp_button = tk.Button(sftp_frame, text="SFTP File", command=sftp_file_button)
    sftp_button.pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
