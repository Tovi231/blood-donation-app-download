from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import sqlite3
import re
import random
import string
from datetime import datetime

# Set window size
Window.size = (400, 700)

class LoginScreen(MDScreen):
    pass

class RegistrationScreen(MDScreen):
    pass

class ProfileScreen(MDScreen):
    pass

class DonationHistoryScreen(MDScreen):
    pass

class ForgotPasswordScreen(MDScreen):
    pass

class ResetPasswordScreen(MDScreen):
    pass

class BloodDonationApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.setup_database()
        
    def setup_database(self):
        conn = sqlite3.connect('blood_donation.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                dob TEXT,
                password TEXT NOT NULL
            )
        ''')
        
        # Create donations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        return super().build()

    def toggle_password_visibility(self, textfield):
        textfield.password = not textfield.password
        textfield.icon_right = "eye" if textfield.password else "eye-off"

    def show_dialog(self, title, text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.title = title
        self.dialog.text = text
        self.dialog.open()

    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        return len(password) >= 8

    def login(self):
        username = self.root.get_screen('login').ids.username.text
        password = self.root.get_screen('login').ids.password.text

        if not username or not password:
            self.show_dialog("Error", "Please fill in all fields")
            return

        conn = sqlite3.connect('blood_donation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.root.current = 'profile'
        else:
            self.show_dialog("Error", "Invalid username or password")

    def register(self):
        full_name = self.root.get_screen('registration').ids.reg_full_name.text
        username = self.root.get_screen('registration').ids.reg_username.text
        email = self.root.get_screen('registration').ids.reg_email.text
        phone = self.root.get_screen('registration').ids.reg_phone.text
        dob = self.root.get_screen('registration').ids.reg_dob.text
        password = self.root.get_screen('registration').ids.reg_password.text
        confirm_password = self.root.get_screen('registration').ids.reg_confirm_password.text

        if not all([full_name, username, email, phone, dob, password, confirm_password]):
            self.show_dialog("Error", "Please fill in all fields")
            return

        if not self.validate_email(email):
            self.show_dialog("Error", "Invalid email format")
            return

        if not self.validate_password(password):
            self.show_dialog("Error", "Password must be at least 8 characters")
            return

        if password != confirm_password:
            self.show_dialog("Error", "Passwords do not match")
            return

        conn = sqlite3.connect('blood_donation.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (full_name, username, email, phone, dob, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (full_name, username, email, phone, dob, password))
            conn.commit()
            self.show_dialog("Success", "Registration successful!")
            self.root.current = 'login'
        except sqlite3.IntegrityError:
            self.show_dialog("Error", "Username or email already exists")
        finally:
            conn.close()

    def send_reset_link(self):
        email = self.root.get_screen('forgot_password').ids.email.text
        
        if not email:
            self.show_dialog("Error", "Please enter your email")
            return

        if not self.validate_email(email):
            self.show_dialog("Error", "Invalid email format")
            return

        conn = sqlite3.connect('blood_donation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # In a real app, you would send an email here
            reset_code = ''.join(random.choices(string.digits, k=6))
            self.show_dialog("Success", f"Reset code sent to {email}\nCode: {reset_code}")
            self.root.current = 'reset_password'
        else:
            self.show_dialog("Error", "Email not found")

    def reset_password(self):
        reset_code = self.root.get_screen('reset_password').ids.reset_code.text
        new_password = self.root.get_screen('reset_password').ids.new_password.text
        confirm_password = self.root.get_screen('reset_password').ids.confirm_password.text

        if not all([reset_code, new_password, confirm_password]):
            self.show_dialog("Error", "Please fill in all fields")
            return

        if not self.validate_password(new_password):
            self.show_dialog("Error", "Password must be at least 8 characters")
            return

        if new_password != confirm_password:
            self.show_dialog("Error", "Passwords do not match")
            return

        # In a real app, you would verify the reset code here
        self.show_dialog("Success", "Password reset successful!")
        self.root.current = 'login'

    def confirm_donation(self):
        amount = self.root.get_screen('profile').ids.charge_amount.text
        
        if not amount:
            self.show_dialog("Error", "Please enter donation amount")
            return

        try:
            amount = float(amount)
            if amount <= 0 or amount > 2000:
                self.show_dialog("Error", "Amount must be between 1 and 2000 INR")
                return
        except ValueError:
            self.show_dialog("Error", "Invalid amount")
            return

        # In a real app, you would process the payment here
        service_fee = amount * 0.1
        net_amount = amount - service_fee
        
        conn = sqlite3.connect('blood_donation.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donations (user_id, amount, date)
            VALUES (?, ?, ?)
        ''', (1, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

        self.show_dialog("Success", f"Donation confirmed!\nAmount: {amount} INR\nService Fee: {service_fee:.2f} INR\nNet Amount: {net_amount:.2f} INR")

if __name__ == '__main__':
    BloodDonationApp().run() 