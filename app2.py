import tkinter as tk
from tkinter import ttk, filedialog, messagebox,Tk
from tkinter import Tk, Label, PhotoImage
from PIL import Image, ImageTk
from Crypto.Cipher import AES, DES, DES3, Blowfish
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class Encryptor:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def generate_key(self):
        if self.algorithm == 'AES':
            return get_random_bytes(32)  # 256-bit key
        elif self.algorithm == 'DES':
            return get_random_bytes(8)  # 64-bit key
        elif self.algorithm == '3DES':
            return get_random_bytes(24)  # 192-bit key
        elif self.algorithm == 'Blowfish':
            return get_random_bytes(16)  # 128-bit key
        elif self.algorithm == 'RSA':
            # Generate RSA key pair (private and public key)
            key = RSA.generate(2048)
            private_key = key.export_key()
            public_key = key.publickey().export_key()
            return private_key, public_key

    def file_encrypt(self, key, original_file):
        encrypted_file = original_file + ".enc"
        key_file = f"key_{os.path.basename(original_file)}.key"

        if self.algorithm == 'AES':
            cipher = AES.new(key, AES.MODE_EAX)
        elif self.algorithm == 'DES':
            cipher = DES.new(key, DES.MODE_EAX)
        elif self.algorithm == '3DES':
            cipher = DES3.new(key, DES3.MODE_EAX)
        elif self.algorithm == 'Blowfish':
            cipher = Blowfish.new(key, Blowfish.MODE_EAX)
        elif self.algorithm == 'RSA':
            public_key = RSA.import_key(key[1])  # Use the public key for encryption
            cipher = PKCS1_OAEP.new(public_key)

        with open(original_file, 'rb') as file:
            original = file.read()

        if self.algorithm in ['AES', 'DES', '3DES', 'Blowfish']:
            original = pad(original, cipher.block_size)
            ciphertext, tag = cipher.encrypt_and_digest(original)
            with open(encrypted_file, 'wb') as file:
                file.write(cipher.nonce)
                file.write(tag)
                file.write(ciphertext)

            # Save symmetric key to a file
            with open(key_file, 'wb') as key_out:
                key_out.write(key)

        elif self.algorithm == 'RSA':
            ciphertext = cipher.encrypt(original)
            with open(encrypted_file, 'wb') as file:
                file.write(ciphertext)

            # Save RSA keys to files
            with open(f"private_{key_file}", 'wb') as priv_file:
                priv_file.write(key[0])  # Save private key
            with open(f"public_{key_file}", 'wb') as pub_file:
                pub_file.write(key[1])  # Save public key

        return encrypted_file, key_file

    def file_decrypt(self, key, encrypted_file):
        decrypted_file = encrypted_file.replace(".enc", "_decrypted.txt")
        with open(encrypted_file, 'rb') as file:
            if self.algorithm == 'AES':
                nonce = file.read(16)
                tag = file.read(16)
                ciphertext = file.read()
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            elif self.algorithm == 'DES':
                nonce = file.read(16)
                tag = file.read(16)
                ciphertext = file.read()
                cipher = DES.new(key, DES.MODE_EAX, nonce=nonce)
            elif self.algorithm == '3DES':
                nonce = file.read(16)
                tag = file.read(16)
                ciphertext = file.read()
                cipher = DES3.new(key, DES3.MODE_EAX, nonce=nonce)
            elif self.algorithm == 'Blowfish':
                nonce = file.read(16)
                tag = file.read(16)
                ciphertext = file.read()
                cipher = Blowfish.new(key, Blowfish.MODE_EAX, nonce=nonce)
            elif self.algorithm == 'RSA':
                ciphertext = file.read()
                private_key = RSA.import_key(key)  # Use the private key for decryption
                cipher = PKCS1_OAEP.new(private_key)
                decrypted = cipher.decrypt(ciphertext)
                with open(decrypted_file, 'wb') as out_file:
                    out_file.write(decrypted)
                return decrypted_file

            try:
                decrypted = cipher.decrypt_and_verify(ciphertext, tag)
                decrypted = unpad(decrypted, cipher.block_size)
            except ValueError:
                messagebox.showerror("Error", "MAC check failed. The file may have been tampered with.")
                return None
        with open(decrypted_file, 'wb') as file:
            file.write(decrypted)
        return decrypted_file


class EncryptorApp:
    def __init__(self, master):
        self.master = master
        master.title("Secure File Encryptor/Decryptor")
        master.geometry("800x600")  # Set your desired initial window size
        master.minsize(800, 600)  # Minimum window size

        # Load and resize the background image
        self.bg_image = Image.open("D:\Ahmed\internship task\download.png")  # Load your image file
        self.bg_image = self.bg_image.resize((master.winfo_width(), master.winfo_height()))  # Resize it to window size
        self.bg_image = ImageTk.PhotoImage(self.bg_image)  # Convert to Tkinter format

        # Create a label for the background image
        self.bg_label = Label(master, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)  # Make the background fill the window

        self.key = None

        # Style configuration for widgets
        style = ttk.Style()
        style.configure("TLabel", background="white", foreground="black", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=8, relief="flat", background="#5498db", foreground="blue")
        style.map("TButton", background=[('active', '#2980b9')])  # Button hover effect
        style.configure("TCombobox", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)

        # Title
        self.title_label = ttk.Label(master, text="File Encryptor/Decryptor", font=("Helvetica", 18, "bold"), background="white", foreground="#2980b9")
        self.title_label.pack(pady=10)

        # Encryption Algorithm
        self.algorithm_label = ttk.Label(master, text="Algorithm:")
        self.algorithm_label.pack(pady=5)
        self.algorithm_var = tk.StringVar()
        self.algorithm_dropdown = ttk.Combobox(master, textvariable=self.algorithm_var, values=['AES', 'DES', '3DES', 'Blowfish', 'RSA'], state="readonly")
        self.algorithm_dropdown.current(0)
        self.algorithm_dropdown.pack(pady=10, padx=20, fill="x")

        # File Selection
        self.file_frame = ttk.Frame(master)
        self.file_frame.pack(pady=10, padx=20)

        self.file_label = ttk.Label(self.file_frame, text="Select File:")
        self.file_label.pack(pady=5)
        self.file_entry = ttk.Entry(self.file_frame, width=35)
        self.file_entry.pack(pady=5)
        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self.select_file)
        self.browse_button.pack(pady=5)

        # Action Buttons
        self.action_frame = ttk.Frame(master)
        self.action_frame.pack(pady=15, padx=20)

        self.encrypt_button = ttk.Button(self.action_frame, text="Encrypt", command=self.encrypt_file)
        self.encrypt_button.pack(fill="x", pady=5)

        self.decrypt_button = ttk.Button(self.action_frame, text="Decrypt", command=self.decrypt_file)
        self.decrypt_button.pack(fill="x", pady=5)

        # Output Box
        self.output_text = tk.Text(master, height=6, wrap="word", bg="#2980b9", fg="#2c3e50", font=("Helvetica", 12), borderwidth=2, relief="solid", bd=0)
        self.output_text.pack(fill="both", expand=True, padx=20, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def encrypt_file(self):
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to encrypt.")
            return

        algorithm = self.algorithm_var.get()
        encryptor = Encryptor(algorithm)
        key = encryptor.generate_key()

        try:
            encrypted_file, key_file = encryptor.file_encrypt(key, file_path)
            self.output_text.insert(tk.END, f"Encrypted File: {encrypted_file}\nKey File: {key_file}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")

    def decrypt_file(self):
        file_path = self.file_entry.get()
        if not file_path or not file_path.endswith(".enc"):
            messagebox.showerror("Error", "Please select a valid encrypted file.")
            return

        key_file_path = filedialog.askopenfilename(title="Select Key File")
        if not key_file_path:
            messagebox.showerror("Error", "Please select a valid key file.")
            return

        with open(key_file_path, 'rb') as key_file:
            key = key_file.read()

        algorithm = self.algorithm_var.get()
        encryptor = Encryptor(algorithm)

        try:
            decrypted_file = encryptor.file_decrypt(key, file_path)
            if decrypted_file:
                self.output_text.insert(tk.END, f"Decrypted File: {decrypted_file}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptorApp(root)
    root.mainloop()