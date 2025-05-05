import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("hospital_data.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    symptoms TEXT,
    diagnosis TEXT,
    drug TEXT,
    doctor TEXT,
    visit_date TEXT
)
''')
conn.commit()

# --------------- DIAGNOSIS LOGIC ----------------
def diagnose_and_prescribe(symptoms):
    s = symptoms.lower()
    if "fever" in s and "headache" in s and "body pain" in s:
        return "Malaria", "Lonart"
    elif "cough" in s and "sore throat" in s:
        return "Common Cold", "Vitamin C + Antibiotics"
    elif "frequent urination" in s and "pain" in s:
        return "Urinary Tract Infection", "Ciprofloxacin"
    elif "chest pain" in s or "breathing difficulty" in s:
        return "Respiratory Issue", "Ventolin Inhaler"
    else:
        return "Unknown - Needs doctor diagnosis", "None"

def assign_doctor(diagnosis):
    mapping = {
        "Malaria": "Dr. Jane (GP)",
        "Common Cold": "Dr. Alex (ENT)",
        "Urinary Tract Infection": "Dr. Grace (Urologist)",
        "Respiratory Issue": "Dr. Ken (Pulmonologist)",
        "Unknown - Needs doctor diagnosis": "Dr. Michael (Consultant)"
    }
    return mapping.get(diagnosis, "Dr. Michael (Consultant)")

# ---------------- GUI LOGIC ----------------

# Main Dashboard
def launch_dashboard(doctor_name):
    login_win.destroy()

    def save_patient():
        name = name_entry.get()
        age = age_entry.get()
        symptoms = symptoms_entry.get()

        if not name or not age or not symptoms:
            messagebox.showwarning("Missing Info", "All fields are required.")
            return

        diagnosis, drug = diagnose_and_prescribe(symptoms)
        doctor = assign_doctor(diagnosis)
        visit_date = datetime.today().strftime('%Y-%m-%d')

        cursor.execute('''
        INSERT INTO patients (name, age, symptoms, diagnosis, drug, doctor, visit_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, symptoms, diagnosis, drug, doctor, visit_date))
        conn.commit()

        result_var.set(f"Diagnosis: {diagnosis}\nDrug: {drug}\nDoctor: {doctor}")
        messagebox.showinfo("Success", "Patient saved successfully.")

        name_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        symptoms_entry.delete(0, tk.END)

    def search_patients():
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + search_entry.get() + '%',))
        for row in cursor.fetchall():
            tree.insert('', tk.END, values=row)

    def export_to_excel():
        df = pd.read_sql_query("SELECT * FROM patients", conn)
        df.to_excel("patients_export.xlsx", index=False)
        messagebox.showinfo("Exported", "Data exported to patients_export.xlsx")

    # Dashboard Window
    root = tk.Tk()
    root.title("🏥 Hospital AI Dashboard")
    root.geometry("800x600")
    root.configure(bg="#e6f2ff")

    tk.Label(root, text=f"Welcome, {doctor_name}", font=("Helvetica", 14), bg="#e6f2ff", fg="#007acc").pack(pady=5)

    # -------- PATIENT REGISTRATION --------
    frame = tk.Frame(root, bg="#e6f2ff")
    frame.pack(pady=10)

    tk.Label(frame, text="Patient Name:", bg="#e6f2ff").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(frame, width=30)
    name_entry.grid(row=0, column=1)

    tk.Label(frame, text="Age:", bg="#e6f2ff").grid(row=1, column=0, sticky="w")
    age_entry = tk.Entry(frame, width=30)
    age_entry.grid(row=1, column=1)

    tk.Label(frame, text="Symptoms:", bg="#e6f2ff").grid(row=2, column=0, sticky="w")
    symptoms_entry = tk.Entry(frame, width=30)
    symptoms_entry.grid(row=2, column=1)

    tk.Button(root, text="Register Patient", command=save_patient, bg="#007acc", fg="white", width=20).pack(pady=5)

    result_var = tk.StringVar()
    tk.Label(root, textvariable=result_var, bg="#e6f2ff", fg="#28a745", font=("Helvetica", 12)).pack(pady=5)

    # -------- PATIENT HISTORY --------
    history_frame = tk.LabelFrame(root, text="🔍 Patient History", bg="#e6f2ff", fg="#333")
    history_frame.pack(pady=10, fill="both", expand=True)

    search_entry = tk.Entry(history_frame, width=30)
    search_entry.pack(pady=5)

    tk.Button(history_frame, text="Search", command=search_patients, bg="#007acc", fg="white").pack()

    cols = ['ID', 'Name', 'Age', 'Symptoms', 'Diagnosis', 'Drug', 'Doctor', 'Date']
    tree = ttk.Treeview(history_frame, columns=cols, show='headings', height=8)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10)

    # -------- EXPORT BUTTON --------
    tk.Button(root, text="Export to Excel", command=export_to_excel, bg="#28a745", fg="white", width=20).pack(pady=10)

    root.mainloop()


# ---------------- LOGIN SCREEN ----------------
def check_login():
    doctor_name = username_entry.get()
    password = password_entry.get()
    if doctor_name and password == "admin123":
        launch_dashboard(doctor_name)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

login_win = tk.Tk()
login_win.title("Doctor Login - Hospital AI")
login_win.geometry("350x250")
login_win.configure(bg="#e6f2ff")

tk.Label(login_win, text="Doctor Login", font=("Helvetica", 16), bg="#e6f2ff", fg="#007acc").pack(pady=10)

tk.Label(login_win, text="Username", bg="#e6f2ff").pack()
username_entry = tk.Entry(login_win)
username_entry.pack(pady=5)

tk.Label(login_win, text="Password", bg="#e6f2ff").pack()
password_entry = tk.Entry(login_win, show="*")
password_entry.pack(pady=5)

tk.Button(login_win, text="Login", command=check_login, bg="#007acc", fg="white", width=20).pack(pady=10)

login_win.mainloop()
