import sqlite3
import customtkinter as ctk
from tkinter import messagebox
import threading
import time

# -------------------------------
# Database
# -------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )""")
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('esraa', '1234')")
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# login functions
# -------------------------------
def vulnerable_login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    log_query(query)
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result is not None

def secure_login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username=? AND password=?"
    log_query(f"[SECURE QUERY] {query} with params ({username}, {password})")
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# -------------------------------
# GUI Functions
# -------------------------------
def log_query(query_text):
    log_panel.configure(state="normal")
    log_panel.insert("end", query_text + "\n")
    log_panel.see("end")
    log_panel.configure(state="disabled")

def attempt_login():
    user = entry_user.get()
    pwd = entry_pass.get()

    threading.Thread(target=process_login, args=(user, pwd)).start()

def process_login(user, pwd):
    show_loader(True)
    time.sleep(1.5)  

    if mode_var.get() == "Vulnerable":
        success = vulnerable_login(user, pwd)
    else:
        success = secure_login(user, pwd)

    show_loader(False)

    if success:
        messagebox.showinfo("Login", "Logged in successfully!")
    else:
        messagebox.showerror("Login", "Invalid credentials!")

def show_loader(state):
    if state:
        loader_label.place(relx=0.5, rely=0.9, anchor="center")
    else:
        loader_label.place_forget()

# -------------------------------
# GUI - CustomTkinter
# -------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SQL Injection Demo")
root.geometry("500x500")
root.resizable(False, False)

title_label = ctk.CTkLabel(root, text="SQL Injection Demo", font=("Arial", 22, "bold"))
title_label.pack(pady=15)

entry_user = ctk.CTkEntry(root, placeholder_text="Username", width=300)
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(root, placeholder_text="Password", show="*", width=300)
entry_pass.pack(pady=10)

mode_var = ctk.StringVar(value="Vulnerable")
radio_vuln = ctk.CTkRadioButton(root, text="Vulnerable Mode", variable=mode_var, value="Vulnerable")
radio_safe = ctk.CTkRadioButton(root, text="Secure Mode", variable=mode_var, value="Secure")
radio_vuln.pack(pady=5)
radio_safe.pack(pady=5)

login_btn = ctk.CTkButton(root, text="Login", command=attempt_login, width=200, height=40, corner_radius=15)
login_btn.pack(pady=15)

loader_label = ctk.CTkLabel(root, text="Processing...", font=("Arial", 14))

log_label = ctk.CTkLabel(root, text="SQL Queries Log", font=("Arial", 14, "bold"))
log_label.pack(pady=5)

log_panel = ctk.CTkTextbox(root, width=450, height=200, state="disabled")
log_panel.pack(pady=5)

root.mainloop()
