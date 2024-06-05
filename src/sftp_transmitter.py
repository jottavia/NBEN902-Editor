import paramiko
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class SFTPTransmitter(tk.Toplevel):
    def __init__(self, parent, file_path, save_function):
        super().__init__(parent)
        self.file_path = file_path
        self.save_function = save_function

        self.title("SFTP Transmission")
        self.geometry("500x450")

        tk.Label(self, text="Destination Address:").pack(pady=5)
        self.host_entry = tk.Entry(self, width=50)
        self.host_entry.pack(pady=5)
        self.host_entry.insert(0, "sft.osc.state.ny.us")

        tk.Label(self, text="Destination Folder:").pack(pady=5)
        self.remote_path_entry = tk.Entry(self, width=50)
        self.remote_path_entry.pack(pady=5)
        self.remote_path_entry.insert(0, "/inbound/")

        tk.Label(self, text="Current File Path:").pack(pady=5)
        self.local_path_frame = tk.Frame(self)
        self.local_path_frame.pack(pady=5)
        self.local_path_entry = tk.Entry(self.local_path_frame, width=40)
        self.local_path_entry.pack(side="left", pady=5)
        self.local_path_entry.insert(0, file_path)
        self.browse_button = tk.Button(self.local_path_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side="left", padx=5)

        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=50)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "sccea_paysr")

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", width=50)
        self.password_entry.pack(pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.transmit_button = tk.Button(self, text="Send", command=self.transmit_file)
        self.transmit_button.pack(pady=20)

        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".input", filetypes=[("Input files", "*.input"), ("All files", "*.*")])
        if file_path:
            self.local_path_entry.delete(0, tk.END)
            self.local_path_entry.insert(0, file_path)

    def transmit_file(self):
        host = self.host_entry.get()
        remote_path = self.remote_path_entry.get()
        local_path = self.local_path_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not password:
            messagebox.showerror("Error", "Password is required for SFTP transmission.")
            return

        try:
            transport = paramiko.Transport((host, 22))
            transport.connect(username=username, password=password)

            sftp = paramiko.SFTPClient.from_transport(transport)
            file_size = os.path.getsize(local_path)

            self.progress["maximum"] = file_size
            self.progress["value"] = 0

            def progress_callback(transferred, total):
                self.progress["value"] = transferred
                self.update_idletasks()

            remote_file_path = os.path.join(remote_path, "paysrp.nben902.sccea.input")
            sftp.put(local_path, remote_file_path, callback=progress_callback)

            sftp.close()
            transport.close()

            self.status_label.config(text="File transmitted successfully.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Failed to transmit file: {e}", fg="red")

def save_before_transmit(file_path, save_function):
    if not file_path:
        file_path = filedialog.asksaveasfilename(defaultextension=".input", filetypes=[("Input files", "*.input"), ("All files", "*.*")])
        if not file_path:
            return None

    save_function(file_path)
    return file_path
