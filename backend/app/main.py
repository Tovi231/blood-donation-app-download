from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .models import database, user, donation
from .models.database import engine, get_db
from .utils import auth
import random
import string

# Create database tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(password)
    db_user = user.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user or not auth.verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset code
    reset_code = ''.join(random.choices(string.digits, k=6))
    db_user.reset_code = reset_code
    db.commit()
    
    # In production, send email with reset code
    return {"message": "Reset code sent to email", "reset_code": reset_code}

@app.post("/reset-password")
async def reset_password(email: str, reset_code: str, new_password: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user or db_user.reset_code != reset_code:
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    db_user.hashed_password = auth.get_password_hash(new_password)
    db_user.reset_code = None
    db.commit()
    return {"message": "Password reset successful"}

@app.post("/donate")
async def create_donation(
    email: str,
    amount: float,
    db: Session = Depends(get_db)
):
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if amount <= 0 or amount > 2000:
        raise HTTPException(status_code=400, detail="Amount must be between 1 and 2000 INR")
    
    service_fee = amount * 0.1
    earnings = amount - service_fee
    
    db_donation = donation.Donation(
        user_id=db_user.id,
        amount=amount,
        service_fee=service_fee,
        earnings=earnings
    )
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    
    return {
        "message": "Donation successful",
        "earnings": earnings,
        "service_fee": service_fee
    }

@app.get("/donation-history/{email}")
async def get_donation_history(email: str, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    donations = db.query(donation.Donation).filter(donation.Donation.user_id == db_user.id).all()
    return donations 