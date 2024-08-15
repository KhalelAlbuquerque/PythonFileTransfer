import Pyro4
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import base64

@Pyro4.expose
class FileClient:
    def notify(self, file_name):
        messagebox.showinfo("Notification", f"The file {file_name} is now available!")

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Client")
        self.server = None
        self.client = None
        self.selected_file_path = None
        self.is_connected = False

        self.setup_gui()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        server_frame = tk.LabelFrame(main_frame, text="Server Management", padx=10, pady=10)
        server_frame.pack(fill="x", pady=10)

        self.connect_button = tk.Button(server_frame, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack(fill="x", pady=5)

        file_frame = tk.LabelFrame(main_frame, text="Upload File", padx=10, pady=10)
        file_frame.pack(fill="x", pady=10)

        tk.Label(file_frame, text="Reference Name:").pack(side="left")
        self.ref_name_entry = tk.Entry(file_frame, width=30)
        self.ref_name_entry.pack(side="left", padx=5)
        self.ref_name_entry.bind("<KeyRelease>", self.update_upload_button_state)

        self.select_file_button = tk.Button(file_frame, text="Select File", command=self.select_file)
        self.select_file_button.pack(side="left", padx=5)

        self.selected_file_label = tk.Label(file_frame, text="", fg="blue")
        self.selected_file_label.pack(side="left", padx=5)

        self.remove_file_button = tk.Button(file_frame, text="Remove File", command=self.remove_selected_file, state="disabled")
        self.remove_file_button.pack(side="left", padx=5)

        self.upload_button = tk.Button(file_frame, text="Upload File", command=self.upload_file, state="disabled")
        self.upload_button.pack(fill="x", pady=5)

        download_frame = tk.LabelFrame(main_frame, text="Download File", padx=10, pady=10)
        download_frame.pack(fill="x", pady=10)

        tk.Label(download_frame, text="Reference Name:").pack(side="left")
        self.download_ref_name_entry = tk.Entry(download_frame, width=30)
        self.download_ref_name_entry.pack(side="left", padx=5)

        self.download_button = tk.Button(download_frame, text="Download File", command=self.download_file)
        self.download_button.pack(fill="x", pady=5)

        delete_frame = tk.LabelFrame(main_frame, text="Delete File", padx=10, pady=10)
        delete_frame.pack(fill="x", pady=10)

        tk.Label(delete_frame, text="Reference Name:").pack(side="left")
        self.delete_ref_name_entry = tk.Entry(delete_frame, width=30)
        self.delete_ref_name_entry.pack(side="left", padx=5)

        self.delete_file_button = tk.Button(delete_frame, text="Delete File", command=self.delete_file)
        self.delete_file_button.pack(fill="x", pady=5)

        interest_frame = tk.LabelFrame(main_frame, text="File Interests", padx=10, pady=10)
        interest_frame.pack(fill="x", pady=10)

        tk.Label(interest_frame, text="Reference Name:").pack(side="left")
        self.interest_ref_name_entry = tk.Entry(interest_frame, width=30)
        self.interest_ref_name_entry.pack(side="left", padx=5)

        self.register_button = tk.Button(interest_frame, text="Register Interest", command=self.register_interest)
        self.register_button.pack(fill="x", pady=5)

        self.cancel_interest_button = tk.Button(interest_frame, text="Cancel Interest", command=self.cancel_interest)
        self.cancel_interest_button.pack(fill="x", pady=5)

        list_frame = tk.LabelFrame(main_frame, text="List Files and Interests", padx=10, pady=10)
        list_frame.pack(fill="x", pady=10)

        self.list_button = tk.Button(list_frame, text="List Files", command=self.list_files)
        self.list_button.pack(fill="x", pady=5)

        self.list_interests_button = tk.Button(list_frame, text="List Interests", command=self.list_interests)
        self.list_interests_button.pack(fill="x", pady=5)


    def update_upload_button_state(self, event=None):

        ref_name = self.ref_name_entry.get()
        if ref_name and self.selected_file_path:
            self.upload_button.config(state="normal")
        else:
            self.upload_button.config(state="disabled")

    def connect_to_server(self):
        try:
            ns = Pyro4.locateNS(host="localhost", port=9090)
            uri = ns.lookup("example.fileserver")
            self.server = Pyro4.Proxy(uri)

            daemon = Pyro4.Daemon()
            self.client = FileClient()
            client_uri = daemon.register(self.client)
            self.client_proxy = Pyro4.Proxy(client_uri)

            daemon_thread = threading.Thread(target=daemon.requestLoop)
            daemon_thread.daemon = True
            daemon_thread.start()

            self.is_connected = True
            self.connect_button.config(state="disabled")
            self.connect_button.config(text="Server is connected")

            messagebox.showinfo("Connection", "Connected to the server successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {e}")

    def select_file(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        self.selected_file_path = filedialog.askopenfilename()
        if self.selected_file_path:
            self.selected_file_label.config(text=self.selected_file_path.split("/")[-1])
            self.remove_file_button.config(state="normal")
        self.update_upload_button_state()

    def remove_selected_file(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        self.selected_file_path = None
        self.selected_file_label.config(text="")
        self.remove_file_button.config(state="disabled")
        self.update_upload_button_state()

    def upload_file(self):
        if not self.is_connected:
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return

        # Esta função será executada em uma thread separada
        def do_upload():
            if self.selected_file_path:
                ref_name = self.ref_name_entry.get()
                if not ref_name:
                    messagebox.showerror("Upload Error", "Reference name cannot be empty.")
                    return

                existing_files = self.server.list_files()
                if ref_name in existing_files:
                    messagebox.showerror("Upload Error", "A file with this reference name already exists.")
                    return

                file_name = self.selected_file_path.split("/")[-1]
                with open(self.selected_file_path, "rb") as f:
                    file_data = f.read()

                if len(file_data) > 1 * 1024 * 1024:
                    messagebox.showerror("Upload Error", "File size exceeds 1MB limit.")
                    return

                response = self.server.upload_file(ref_name, file_name, file_data)
                messagebox.showinfo("Upload", response)

                self.ref_name_entry.delete(0, tk.END)
                self.remove_selected_file()

        # nova thread para executar `do_upload`
        upload_thread = threading.Thread(target=do_upload)
        upload_thread.start()

        # código original
        # if self.selected_file_path:
        #     ref_name = self.ref_name_entry.get()
        #     if not ref_name:
        #         messagebox.showerror("Upload Error", "Reference name cannot be empty.")
        #         return
        #
        #     existing_files = self.server.list_files()
        #     if ref_name in existing_files:
        #         messagebox.showerror("Upload Error", "A file with this reference name already exists.")
        #         return
        #
        #     file_name = self.selected_file_path.split("/")[-1]
        #     with open(self.selected_file_path, "rb") as f:
        #         file_data = f.read()
        #
        #     if len(file_data) > 1 * 1024 * 1024:
        #         messagebox.showerror("Upload Error", "File size exceeds 1MB limit.")
        #         return
        #
        #     response = self.server.upload_file(ref_name, file_name, file_data)
        #     messagebox.showinfo("Upload", response)
        #
        #     self.ref_name_entry.delete(0, tk.END)
        #     self.remove_selected_file()


    def delete_file(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        ref_name = self.delete_ref_name_entry.get()
        if not ref_name:
            messagebox.showerror("Delete Error", "Reference name cannot be empty.")
            return

        response = self.server.delete_file(ref_name)
        messagebox.showinfo("Delete File", response)

        self.delete_ref_name_entry.delete(0, tk.END)

    def register_interest(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        ref_name = self.interest_ref_name_entry.get()
        if self.server and ref_name:
            response = self.server.register_interest(ref_name, self.client_proxy, duration=3600)
            messagebox.showinfo("Interest", response)
        self.interest_ref_name_entry.delete(0, tk.END)

    def cancel_interest(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        ref_name = self.interest_ref_name_entry.get()
        if self.server and ref_name:
            response = self.server.cancel_interest(ref_name, self.client_proxy)
            messagebox.showinfo("Cancel Interest", response)
        self.interest_ref_name_entry.delete(0, tk.END)

    def list_files(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        if self.server:
            files = self.server.list_files()
            formatted_files = "\n".join([f"Reference Name: {ref}, File Name: {name}" for ref, name in files.items()])
            messagebox.showinfo("Files", f"Available files:\n{formatted_files}")

    def list_interests(self):
        if (not self.is_connected):
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return
        if self.server:
            interests = self.server.list_interests()
            formatted_interests = "\n".join([f"Reference Name: {ref}, Interested Clients: {len(clients)}" for ref, clients in interests.items()])
            messagebox.showinfo("Interests", f"Current interests:\n{formatted_interests}")

    def download_file(self):
        if not self.is_connected:
            messagebox.showerror("Connection error", "Please connect to server before using the system")
            return

        ref_name = self.download_ref_name_entry.get()
        if not ref_name:
            messagebox.showerror("Download Error", "Reference name cannot be empty.")
            return

        try:
            file_content = self.server.download_file(ref_name)
            print(f"Received content type: {type(file_content)}")  # Linha de depuração
            if isinstance(file_content, str) and file_content == "File not found.":
                messagebox.showerror("Download Error", file_content)
            elif isinstance(file_content, bytes):
                with open(ref_name, "wb") as f:
                    f.write(file_content)
                messagebox.showinfo("Download", f"{ref_name} downloaded successfully.")
            else:
                messagebox.showerror("Download Error", "Unexpected data type received.")
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {e}")


def run_interface():
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_interface()
