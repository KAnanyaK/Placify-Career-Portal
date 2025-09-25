import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class FirebaseAuth:
    def __init__(self):
        # Demo mode for now - Firebase setup comes later
        self.demo_mode = True
        print("✅ Auth initialized in demo mode")
    
    def register_user(self, email, password):
        return {
            "success": True,
            "message": "Account created successfully (Demo mode)",
            "user_id": f"demo_user_{hash(email) % 10000}"
        }
    
    def login_user(self, email, password):
        if "@" in email and "." in email:
            return {
                "success": True,
                "message": "Login successful (Demo mode)",
                "user_id": f"demo_user_{hash(email) % 10000}"
            }
        else:
            return {"success": False, "message": "Invalid email format"}
