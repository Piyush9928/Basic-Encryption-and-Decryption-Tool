import mysql.connector
from tkinter import *
from tkinter import messagebox, simpledialog
import base64

# MySQL Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="piyush",
    database="encryption_tool"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS encryption_tool")
cursor.execute("USE encryption_tool")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (user_id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) UNIQUE,password VARCHAR(255))")
cursor.execute("CREATE TABLE IF NOT EXISTS Messages (message_id INT AUTO_INCREMENT PRIMARY KEY,user_id INT,encrypted_message TEXT,FOREIGN KEY (user_id) REFERENCES Users(user_id))")

# --- Helper Functions ---

# Simple Caesar Cipher for Encryption/Decryption
def encrypt_text(plain_text, shift=3):
    encrypted = ''.join([chr((ord(char) + shift) % 256) for char in plain_text])
    return base64.urlsafe_b64encode(encrypted.encode()).decode()

def decrypt_text(encrypted_text, shift=3):
    encrypted = base64.urlsafe_b64decode(encrypted_text).decode()
    decrypted = ''.join([chr((ord(char) - shift) % 256) for char in encrypted])
    return decrypted

# Function to add a new user
def add_user(username, password):
    try:
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", f"User '{username}' created successfully!")
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

# Function to save encrypted message to the database
def save_message(user_id, message):
    cursor.execute("INSERT INTO Messages (user_id, encrypted_message) VALUES (%s, %s)", (user_id, message))
    conn.commit()
    messagebox.showinfo("Success", "Message saved successfully!")

# Function to fetch and display saved messages
def fetch_messages(user_id):
    cursor.execute("SELECT message_id, encrypted_message FROM Messages WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()

    message_list.delete(0, END)
    for row in rows:
        message_list.insert(END, f"ID: {row[0]} - Message: {row[1]}")

# --- GUI Components ---

# Function to open main menu after login
def open_main_menu(user_id):
    main_menu = Tk()
    main_menu.title("Encryption and Decryption Tool")
    main_menu.geometry("490x410")

    # Encrypt and Save Message Section
    Label(main_menu, text="Enter Message to Encrypt").pack()
    message_entry = Entry(main_menu)
    message_entry.pack()

    def encrypt_and_save():
        plain_text = message_entry.get()
        encrypted_text = encrypt_text(plain_text)
        save_message(user_id, encrypted_text)

    Button(main_menu, text="Encrypt & Save", command=encrypt_and_save).pack(pady=10)

    # View Messages Section
    Label(main_menu, text="Saved Messages").pack()
    global message_list
    message_list = Listbox(main_menu, width=50)
    message_list.pack(pady=10)
    
    Button(main_menu, text="Refresh Messages", command=lambda: fetch_messages(user_id)).pack(pady=5)

    # Decrypt Message Section
    Label(main_menu, text="Enter Message ID to Decrypt").pack()
    message_id_entry = Entry(main_menu)
    message_id_entry.pack()

    def decrypt_and_show():
        message_id = message_id_entry.get()
        cursor.execute("SELECT encrypted_message FROM Messages WHERE message_id = %s", (message_id,))
        result = cursor.fetchone()

        if result:
            decrypted_text = decrypt_text(result[0])
            messagebox.showinfo("Decrypted Message", decrypted_text)
        else:
            messagebox.showerror("Error", "Message ID not found.")

    Button(main_menu, text="Decrypt Message", command=decrypt_and_show).pack(pady=10)

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute("SELECT user_id FROM Users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()

    if result:
        open_main_menu(result[0])
        login_window.destroy()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# Function to handle signup
def signup():
    signup_window = Toplevel()
    signup_window.title("Signup")

    Label(signup_window, text="Username").pack()
    signup_username_entry = Entry(signup_window)
    signup_username_entry.pack()

    Label(signup_window, text="Password").pack()
    signup_password_entry = Entry(signup_window, show="*")
    signup_password_entry.pack()

    Button(signup_window, text="Signup", command=lambda: add_user(
        signup_username_entry.get(), signup_password_entry.get())).pack()

# --- Login Window ---

login_window = Tk()
login_window.title("Login")
login_window.geometry("300x200")

Label(login_window, text="Username").pack()
username_entry = Entry(login_window)
username_entry.pack()

Label(login_window, text="Password").pack()
password_entry = Entry(login_window, show="*")
password_entry.pack()

Button(login_window, text="Login", command=login).pack()
Button(login_window, text="Signup", command=signup).pack()
Button(login_window, text="Exit", command=login_window.destroy).pack()

# Start the GUI event loop
login_window.mainloop()

# Close the database connection
cursor.close()
conn.close()
