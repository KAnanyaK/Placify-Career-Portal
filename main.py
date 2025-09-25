import streamlit as st
import sys, os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'components'))
from database import MongoDB
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Placify : Career Portal", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_db():
    return MongoDB()

def main():
    db = get_db()
    st.title("🎓 Placify : Career Portal")

    # Show toggle buttons at the top
    if "show_login" not in st.session_state:
        st.session_state.show_login = True  # Default view

    cols = st.columns([2, 2])
    with cols[0]:
        if st.button("Login", type="primary"):
            st.session_state.show_login = True
    with cols[1]:
        if st.button("Register"):
            st.session_state.show_login = False

    st.markdown("---")

    if st.session_state.show_login:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if not all([email, password]):
                    st.error("Enter both email and password.")
                else:
                    if email == "admin@gmail.com" and password == "admin123":
                        st.session_state.user_logged_in = True
                        st.session_state.user_role = "admin"
                        st.session_state.user_email = email
                        st.success("Admin login successful.")
                        st.switch_page("pages/admin_dashboard.py")
                    else:
                        student = db.get_student_by_email(email)
                        if student and "password" in student and student["password"] == password:
                            st.session_state.user_logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.user_email = email
                            st.session_state.student_id = student["student_id"]
                            st.success("Student login successful.")
                            st.switch_page("pages/student_dashboard.py")
                        else:
                            st.error("Invalid login or not registered.")
        st.info("New student? Click 'Register' above to create an account.")

    else:
        st.subheader("New Student Registration")
        with st.form("signup_form"):
            name = st.text_input("Full Name *")
            roll_number = st.text_input("Roll Number *")
            campus = st.text_input("Campus *")
            department = st.text_input("Department *")
            phone = st.text_input("Phone *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            submit = st.form_submit_button("Register")
            if submit:
                # Phone validation
                if not phone.isdigit() or len(phone) != 10:
                    st.error("Phone number must be exactly 10 digits.")
                # Email validation
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
                    st.error("Please enter a valid email address.")
                # Password validation (at least 8 chars, with one digit, one uppercase, one lowercase)
                elif not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', password):
                    st.error("Password must be at least 8 characters long, contain a digit, uppercase and lowercase letter.")
                elif not all([name, roll_number, campus, department, phone, email, password, confirm]):
                    st.error("All fields required!")
                elif password != confirm:
                    st.error("Passwords do not match!")
                elif db.get_student_by_email(email):
                    st.error("Email already registered. Please log in.")
                elif email == "admin@gmail.com":
                    st.error("That email is reserved for admin.")
                else:
                    result = db.create_student({
                        "student_name": name,
                        "roll_number": roll_number,
                        "campus": campus,
                        "department": department,
                        "phone_number": phone,
                        "email_id": email,
                        "user_role": "student",
                        "cgpa": 0,
                        "resume": "",
                        "password": password
                    })
                    if result.get("success"):
                        st.success("Registered! Please click Login to sign in.")
                        st.session_state.show_login = True
                    else:
                        st.error(result.get("message", "Error in registration."))

if __name__ == "__main__":
    main()
