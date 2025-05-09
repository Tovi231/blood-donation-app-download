from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.utils import platform
import re
from datetime import datetime
import random
import string
import requests

# Set window size for Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
else:
    Window.size = (360, 640)  # Common mobile screen size for testing

class LoginScreen(Screen):
    pass

class RegistrationScreen(Screen):
    pass

class TermsScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class DonationHistoryScreen(Screen):
    pass

class ForgotPasswordScreen(Screen):
    pass

class ResetPasswordScreen(Screen):
    pass

class BloodDonationApp(MDApp):
    donation_history = []
    current_user = None
    API_URL = "http://localhost:5000"  # Backend API URL
    
    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegistrationScreen(name='registration'))
        sm.add_widget(TermsScreen(name='terms'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(DonationHistoryScreen(name='donation_history'))
        sm.add_widget(ForgotPasswordScreen(name='forgot_password'))
        sm.add_widget(ResetPasswordScreen(name='reset_password'))
        
        return sm
    
    def toggle_password_visibility(self, textfield):
        """Toggle password visibility"""
        textfield.password = not textfield.password
        textfield.icon_right = "eye" if not textfield.password else "eye-off"
    
    def register(self):
        """Handle user registration"""
        reg_screen = self.root.get_screen('registration')
        full_name = reg_screen.ids.reg_full_name.text
        phone = reg_screen.ids.reg_phone.text
        dob = reg_screen.ids.reg_dob.text
        username = reg_screen.ids.reg_username.text
        password = reg_screen.ids.reg_password.text
        
        # Validate inputs
        if not all([full_name, phone, dob, username, password]):
            self.show_alert_dialog("Please fill in all fields.")
            return
            
        try:
            # Send registration request to backend
            response = requests.post(
                f"{self.API_URL}/register",
                json={
                    "full_name": full_name,
                    "phone": phone,
                    "dob": dob,
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 201:
                self.show_alert_dialog("Registration successful! Please login.")
                self.root.current = 'login'
            else:
                self.show_alert_dialog(response.json().get('error', 'Registration failed'))
        except requests.exceptions.RequestException:
            self.show_alert_dialog("Could not connect to server. Please try again later.")
    
    def login(self):
        """Handle user login"""
        login_screen = self.root.get_screen('login')
        username = login_screen.ids.username.text
        password = login_screen.ids.password.text
        
        if not username or not password:
            self.show_alert_dialog("Please enter both username and password")
            return
            
        try:
            # Send login request to backend
            response = requests.post(
                f"{self.API_URL}/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_user = data.get('user')
                self.root.current = 'profile'
            else:
                self.show_alert_dialog("Invalid username or password")
        except requests.exceptions.RequestException:
            self.show_alert_dialog("Could not connect to server. Please try again later.")
    
    def confirm_donation(self):
        """Handle donation confirmation"""
        if not self.current_user:
            self.show_alert_dialog("Please login first")
            return
            
        profile_screen = self.root.get_screen('profile')
        charge_amount = profile_screen.ids.charge_amount.text
        
        if not charge_amount or not charge_amount.isdigit():
            self.show_alert_dialog("Please enter a valid amount")
            return
            
        charge_amount = int(charge_amount)
        if not (0 < charge_amount <= 2000):
            self.show_alert_dialog("Amount must be between 1 and 2000 INR")
            return
            
        service_fee = charge_amount * 0.1
        earnings = charge_amount - service_fee
        
        self.donation_history.append(f"Earned: {earnings} INR | Service Fee: {service_fee} INR")
        self.show_alert_dialog(f"Donation successful! You earned {earnings} INR after service fee deduction.")
        self.load_donation_history()
    
    def show_alert_dialog(self, message):
        dialog = MDDialog(
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()
    
    def load_donation_history(self):
        history_screen = self.root.get_screen('donation_history')
        history_list = history_screen.ids.history_list
        history_list.clear_widgets()
        
        for record in self.donation_history:
            history_list.add_widget(MDLabel(text=record, size_hint_y=None, height=40))

if __name__ == '__main__':
    BloodDonationApp().run()
