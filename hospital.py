"""
🏥 HOSPITAL MANAGEMENT SYSTEM - READY TO RUN
✅ Copy this ENTIRE code ✅ Save as hospital.py ✅ Run with: python hospital.py
"""

# ============================================================================
# STEP 1: COPY THIS ENTIRE CODE AND SAVE AS hospital.py
# STEP 2: OPEN TERMINAL/CMD AND TYPE: python hospital.py
# ============================================================================

import sqlite3
import datetime
import json
import os
import sys

# ============================================================================
# SIMPLE DATABASE SETUP
# ============================================================================

class SimpleHospitalDB:
    def __init__(self):
        self.conn = sqlite3.connect('hospital_simple.db')
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        # Patients table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE,
                name TEXT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                address TEXT,
                reg_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Doctors table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id TEXT UNIQUE,
                name TEXT,
                specialization TEXT,
                fee REAL,
                phone TEXT,
                available INTEGER DEFAULT 1
            )
        ''')
        
        # Appointments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id TEXT UNIQUE,
                patient_id TEXT,
                doctor_id TEXT,
                date DATE,
                time TEXT,
                status TEXT DEFAULT 'Scheduled'
            )
        ''')
        
        # Medicines table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity INTEGER,
                price REAL,
                expiry DATE
            )
        ''')
        
        # Bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_no TEXT UNIQUE,
                patient_id TEXT,
                amount REAL,
                paid REAL,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        
        # Insert sample data
        self.insert_sample_data()
        self.conn.commit()
    
    def insert_sample_data(self):
        # Sample doctors
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        if self.cursor.fetchone()[0] == 0:
            doctors = [
                ('DOC001', 'Dr. Rajesh Kumar', 'Cardiology', 800, '9876543210'),
                ('DOC002', 'Dr. Priya Sharma', 'Pediatrics', 600, '9876543211'),
                ('DOC003', 'Dr. Anil Verma', 'Orthopedics', 700, '9876543212')
            ]
            self.cursor.executemany(
                "INSERT INTO doctors (doctor_id, name, specialization, fee, phone) VALUES (?, ?, ?, ?, ?)",
                doctors
            )
        
        # Sample medicines
        self.cursor.execute("SELECT COUNT(*) FROM medicines")
        if self.cursor.fetchone()[0] == 0:
            medicines = [
                ('Paracetamol', 100, 5.0, '2025-12-31'),
                ('Amoxicillin', 50, 15.0, '2024-08-30'),
                ('Insulin', 30, 200.0, '2024-10-31')
            ]
            self.cursor.executemany(
                "INSERT INTO medicines (name, quantity, price, expiry) VALUES (?, ?, ?, ?)",
                medicines
            )
    
    def close(self):
        self.conn.close()

# ============================================================================
# SIMPLE HOSPITAL SYSTEM
# ============================================================================

class SimpleHospitalSystem:
    def __init__(self):
        self.db = SimpleHospitalDB()
        print("✅ Database initialized successfully!")
    
    def generate_id(self, prefix, table):
        self.db.cursor.execute(f"SELECT MAX(id) FROM {table}")
        max_id = self.db.cursor.fetchone()[0] or 0
        return f"{prefix}{max_id + 1:03d}"
    
    # Patient Management
    def add_patient(self):
        print("\n" + "="*50)
        print("ADD NEW PATIENT")
        print("="*50)
        
        patient_id = self.generate_id('P', 'patients')
        name = input("Patient Name: ")
        age = input("Age: ")
        gender = input("Gender (M/F): ").upper()
        phone = input("Phone: ")
        address = input("Address: ")
        
        try:
            self.db.cursor.execute('''
                INSERT INTO patients (patient_id, name, age, gender, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, name, age, gender, phone, address))
            self.db.conn.commit()
            
            print(f"\n✅ Patient registered successfully!")
            print(f"Patient ID: {patient_id}")
            return patient_id
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return None
    
    def view_patients(self):
        print("\n" + "="*50)
        print("PATIENT LIST")
        print("="*50)
        
        self.db.cursor.execute("SELECT * FROM patients ORDER BY reg_date DESC")
        patients = self.db.cursor.fetchall()
        
        if patients:
            print(f"\nTotal Patients: {len(patients)}")
            print("-"*80)
            for patient in patients:
                print(f"ID: {patient[1]:6} | Name: {patient[2]:20} | Age: {patient[3]:3} | Phone: {patient[5]:12}")
            print("-"*80)
        else:
            print("\n📭 No patients found.")
    
    # Doctor Management
    def view_doctors(self):
        print("\n" + "="*50)
        print("DOCTOR LIST")
        print("="*50)
        
        self.db.cursor.execute("SELECT * FROM doctors WHERE available = 1")
        doctors = self.db.cursor.fetchall()
        
        if doctors:
            print(f"\nAvailable Doctors: {len(doctors)}")
            print("-"*80)
            for doctor in doctors:
                print(f"ID: {doctor[1]:6} | Dr. {doctor[2]:20} | Specialization: {doctor[3]:15} | Fee: ₹{doctor[4]}")
            print("-"*80)
            return doctors
        else:
            print("\n📭 No doctors available.")
            return []
    
    # Appointment Management
    def book_appointment(self):
        print("\n" + "="*50)
        print("BOOK APPOINTMENT")
        print("="*50)
        
        # Show patients
        self.view_patients()
        patient_id = input("\nEnter Patient ID: ")
        
        # Check patient exists
        self.db.cursor.execute("SELECT name FROM patients WHERE patient_id = ?", (patient_id,))
        if not self.db.cursor.fetchone():
            print("\n❌ Patient not found!")
            return
        
        # Show doctors
        doctors = self.view_doctors()
        if not doctors:
            return
        
        doctor_id = input("\nEnter Doctor ID: ")
        
        # Check doctor exists
        self.db.cursor.execute("SELECT name FROM doctors WHERE doctor_id = ? AND available = 1", (doctor_id,))
        doctor = self.db.cursor.fetchone()
        if not doctor:
            print("\n❌ Doctor not found or not available!")
            return
        
        date = input("Date (YYYY-MM-DD): ")
        time = input("Time (HH:MM): ")
        
        appointment_id = self.generate_id('APT', 'appointments')
        
        try:
            self.db.cursor.execute('''
                INSERT INTO appointments (appointment_id, patient_id, doctor_id, date, time)
                VALUES (?, ?, ?, ?, ?)
            ''', (appointment_id, patient_id, doctor_id, date, time))
            self.db.conn.commit()
            
            print(f"\n✅ Appointment booked successfully!")
            print(f"Appointment ID: {appointment_id}")
            print(f"Doctor: Dr. {doctor[0]}")
            return appointment_id
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return None
    
    def view_today_appointments(self):
        print("\n" + "="*50)
        print("TODAY'S APPOINTMENTS")
        print("="*50)
        
        today = datetime.date.today().isoformat()
        self.db.cursor.execute('''
            SELECT a.*, p.name as patient_name, d.name as doctor_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.date = ?
            ORDER BY a.time
        ''', (today,))
        
        appointments = self.db.cursor.fetchall()
        
        if appointments:
            print(f"\nToday's Appointments: {len(appointments)}")
            print("-"*100)
            for apt in appointments:
                print(f"ID: {apt[1]:8} | Patient: {apt[7]:20} | Doctor: {apt[8]:20}")
                print(f"    Time: {apt[6]} | Status: {apt[7]}")
                print("-"*100)
        else:
            print("\n📭 No appointments for today.")
    
    # Medicine Management
    def view_medicines(self):
        print("\n" + "="*50)
        print("MEDICINE STOCK")
        print("="*50)
        
        self.db.cursor.execute("SELECT * FROM medicines ORDER BY name")
        medicines = self.db.cursor.fetchall()
        
        if medicines:
            print(f"\nMedicine Stock: {len(medicines)} items")
            print("-"*60)
            for med in medicines:
                print(f"{med[1]:20} | Qty: {med[2]:4} | Price: ₹{med[3]:6.2f} | Expiry: {med[4]}")
            print("-"*60)
        else:
            print("\n📭 No medicines in stock.")
    
    def add_medicine(self):
        print("\n" + "="*50)
        print("ADD MEDICINE")
        print("="*50)
        
        name = input("Medicine Name: ")
        quantity = int(input("Quantity: ") or 0)
        price = float(input("Price: ") or 0)
        expiry = input("Expiry Date (YYYY-MM-DD): ")
        
        try:
            self.db.cursor.execute('''
                INSERT INTO medicines (name, quantity, price, expiry)
                VALUES (?, ?, ?, ?)
            ''', (name, quantity, price, expiry))
            self.db.conn.commit()
            
            print(f"\n✅ Medicine added successfully!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Billing System
    def generate_bill(self):
        print("\n" + "="*50)
        print("GENERATE BILL")
        print("="*50)
        
        self.view_patients()
        patient_id = input("\nEnter Patient ID: ")
        
        # Check patient
        self.db.cursor.execute("SELECT name FROM patients WHERE patient_id = ?", (patient_id,))
        patient = self.db.cursor.fetchone()
        if not patient:
            print("\n❌ Patient not found!")
            return
        
        amount = float(input("Total Amount: ₹") or 0)
        paid = float(input("Amount Paid: ₹") or 0)
        
        bill_no = self.generate_id('BILL', 'bills')
        status = "Paid" if paid >= amount else "Partial" if paid > 0 else "Pending"
        
        try:
            self.db.cursor.execute('''
                INSERT INTO bills (bill_no, patient_id, amount, paid, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (bill_no, patient_id, amount, paid, status))
            self.db.conn.commit()
            
            print(f"\n✅ Bill generated successfully!")
            print(f"Bill No: {bill_no}")
            print(f"Patient: {patient[0]}")
            print(f"Total: ₹{amount:.2f}")
            print(f"Paid: ₹{paid:.2f}")
            print(f"Due: ₹{amount - paid:.2f}")
            print(f"Status: {status}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Reports
    def view_statistics(self):
        print("\n" + "="*50)
        print("SYSTEM STATISTICS")
        print("="*50)
        
        # Patient count
        self.db.cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = self.db.cursor.fetchone()[0]
        
        # Doctor count
        self.db.cursor.execute("SELECT COUNT(*) FROM doctors WHERE available = 1")
        doctor_count = self.db.cursor.fetchone()[0]
        
        # Today's appointments
        today = datetime.date.today().isoformat()
        self.db.cursor.execute("SELECT COUNT(*) FROM appointments WHERE date = ?", (today,))
        today_appointments = self.db.cursor.fetchone()[0]
        
        # Medicine stock
        self.db.cursor.execute("SELECT SUM(quantity) FROM medicines")
        total_medicines = self.db.cursor.fetchone()[0] or 0
        
        # Pending bills
        self.db.cursor.execute("SELECT COUNT(*) FROM bills WHERE status != 'Paid'")
        pending_bills = self.db.cursor.fetchone()[0]
        
        print(f"\n📊 SYSTEM OVERVIEW")
        print("-"*40)
        print(f"Total Patients: {patient_count}")
        print(f"Available Doctors: {doctor_count}")
        print(f"Today's Appointments: {today_appointments}")
        print(f"Total Medicines in Stock: {total_medicines}")
        print(f"Pending Bills: {pending_bills}")
        print("-"*40)
    
    def daily_report(self):
        print("\n" + "="*50)
        print("DAILY REPORT")
        print("="*50)
        
        today = datetime.date.today().isoformat()
        
        # New patients today
        self.db.cursor.execute("SELECT COUNT(*) FROM patients WHERE reg_date = ?", (today,))
        new_patients = self.db.cursor.fetchone()[0]
        
        # Appointments today
        self.db.cursor.execute("SELECT COUNT(*) FROM appointments WHERE date = ?", (today,))
        total_appointments = self.db.cursor.fetchone()[0]
        
        # Bills today
        self.db.cursor.execute("SELECT COUNT(*), SUM(amount), SUM(paid) FROM bills WHERE DATE('now') = DATE('now')")
        bill_data = self.db.cursor.fetchone()
        
        print(f"\n📅 REPORT FOR {today}")
        print("-"*50)
        print(f"New Patients: {new_patients}")
        print(f"Total Appointments: {total_appointments}")
        print(f"\n💰 Financial Summary:")
        print(f"  Total Bills: {bill_data[0] or 0}")
        print(f"  Total Amount: ₹{bill_data[1] or 0:.2f}")
        print(f"  Total Collected: ₹{bill_data[2] or 0:.2f}")
        print(f"  Pending: ₹{(bill_data[1] or 0) - (bill_data[2] or 0):.2f}")
        print("-"*50)

# ============================================================================
# MAIN MENU INTERFACE
# ============================================================================

def display_menu():
    """Display the main menu"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*60)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM")
    print("="*60)
    print("\nMAIN MENU:")
    print("1. 👤 Patient Management")
    print("2. 👨‍⚕️ Doctor Management") 
    print("3. 📅 Appointment Management")
    print("4. 💊 Medicine Management")
    print("5. 💰 Billing System")
    print("6. 📊 Reports & Statistics")
    print("7. 🚪 Exit")
    print("="*60)

def patient_menu(system):
    """Patient management menu"""
    while True:
        print("\n" + "="*50)
        print("PATIENT MANAGEMENT")
        print("="*50)
        print("1. Add New Patient")
        print("2. View All Patients")
        print("3. Back to Main Menu")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            system.add_patient()
            input("\nPress Enter to continue...")
        elif choice == "2":
            system.view_patients()
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice!")

def doctor_menu(system):
    """Doctor management menu"""
    while True:
        print("\n" + "="*50)
        print("DOCTOR MANAGEMENT")
        print("="*50)
        print("1. View Available Doctors")
        print("2. Back to Main Menu")
        
        choice = input("\nEnter choice (1-2): ")
        
        if choice == "1":
            system.view_doctors()
            input("\nPress Enter to continue...")
        elif choice == "2":
            break
        else:
            print("❌ Invalid choice!")

def appointment_menu(system):
    """Appointment management menu"""
    while True:
        print("\n" + "="*50)
        print("APPOINTMENT MANAGEMENT")
        print("="*50)
        print("1. Book Appointment")
        print("2. View Today's Appointments")
        print("3. Back to Main Menu")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            system.book_appointment()
            input("\nPress Enter to continue...")
        elif choice == "2":
            system.view_today_appointments()
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice!")

def medicine_menu(system):
    """Medicine management menu"""
    while True:
        print("\n" + "="*50)
        print("MEDICINE MANAGEMENT")
        print("="*50)
        print("1. View Medicine Stock")
        print("2. Add New Medicine")
        print("3. Back to Main Menu")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            system.view_medicines()
            input("\nPress Enter to continue...")
        elif choice == "2":
            system.add_medicine()
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice!")

def billing_menu(system):
    """Billing menu"""
    while True:
        print("\n" + "="*50)
        print("BILLING SYSTEM")
        print("="*50)
        print("1. Generate Bill")
        print("2. Back to Main Menu")
        
        choice = input("\nEnter choice (1-2): ")
        
        if choice == "1":
            system.generate_bill()
            input("\nPress Enter to continue...")
        elif choice == "2":
            break
        else:
            print("❌ Invalid choice!")

def reports_menu(system):
    """Reports menu"""
    while True:
        print("\n" + "="*50)
        print("REPORTS & STATISTICS")
        print("="*50)
        print("1. System Statistics")
        print("2. Daily Report")
        print("3. Back to Main Menu")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            system.view_statistics()
            input("\nPress Enter to continue...")
        elif choice == "2":
            system.daily_report()
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice!")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program"""
    print("\n" + "="*60)
    print("INITIALIZING HOSPITAL MANAGEMENT SYSTEM...")
    print("="*60)
    
    try:
        system = SimpleHospitalSystem()
        print("✅ System initialized successfully!")
        print("🚀 Ready to use!")
        
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                patient_menu(system)
            elif choice == "2":
                doctor_menu(system)
            elif choice == "3":
                appointment_menu(system)
            elif choice == "4":
                medicine_menu(system)
            elif choice == "5":
                billing_menu(system)
            elif choice == "6":
                reports_menu(system)
            elif choice == "7":
                print("\n" + "="*60)
                print("Thank you for using Hospital Management System!")
                print("Goodbye! 👋")
                print("="*60)
                system.db.close()
                break
            else:
                print("\n❌ Invalid choice! Please enter 1-7.")
                input("Press Enter to continue...")
                
    except Exception as e:
        print(f"\n❌ Error initializing system: {e}")
        print("Please check if Python is installed correctly.")
        input("Press Enter to exit...")

# ============================================================================
# RUN INSTRUCTIONS
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("HOW TO RUN THIS HOSPITAL SYSTEM:")
    print("="*70)
    print("\n📋 STEP 1: Copy this entire code")
    print("📋 STEP 2: Save as 'hospital.py'")
    print("📋 STEP 3: Open Terminal/Command Prompt")
    print("📋 STEP 4: Type: python hospital.py")
    print("📋 STEP 5: Press Enter")
    print("\n" + "="*70)
    print("Starting system in 3 seconds...")
    
    import time
    time.sleep(3)
    
    main()