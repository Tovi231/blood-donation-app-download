# Blood Donation App

A KivyMD-based application for managing blood donations.

## Features

- User registration and login
- Password reset functionality
- Donation management
- Donation history tracking
- Profile management

## Setup

1. Install Python 3.7 or higher
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the App

1. Make sure you have all the required files:
   - main.py
   - blooddonation.kv
   - IMG-20250506-WA0001.jpg (app icon)
   - requirements.txt

2. Run the application:
   ```
   python main.py
   ```

## Database

The app uses SQLite for data storage. The database file (blood_donation.db) will be created automatically when you first run the application.

## Note

This is a demo application. In a production environment, you would need to:
- Implement proper password hashing
- Add email verification
- Implement secure payment processing
- Add proper error handling
- Add data validation
- Implement proper session management 