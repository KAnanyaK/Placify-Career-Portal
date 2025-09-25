#STUDENT ACCESS ONLY
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB


if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "student":
    st.warning("You are not authorized to view this page.")
    st.stop()

db = MongoDB()

def show_student_profile():
    st.header("👤 Student Profile")

    # Retrieve email from session
    email = st.session_state.get("user_email", "")
    if not email:
        st.warning("Please log in from main page to edit your profile.")
        st.stop()

    current_student = db.get_student_by_email(email)

    with st.form("student_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Name *", value=current_student.get("student_name", "") if current_student else "")
            roll_number = st.text_input("Roll Number *", value=current_student.get("roll_number", "") if current_student else "")
            campus = st.text_input("Campus *", value=current_student.get("campus", "") if current_student else "")
            department = st.text_input("Department *", value=current_student.get("department", "") if current_student else "")

        with col2:
            phone_number = st.text_input("Phone *", value=current_student.get("phone_number", "") if current_student else "")
            cgpa = st.number_input("CGPA *", min_value=0.0, max_value=10.0, step=0.01, value=float(current_student.get("cgpa", 0.0)) if current_student else 0.0)
            email_id = st.text_input("Email", value=email, disabled=True)
            resume = st.text_input("Resume Link", value=current_student.get("resume", "") if current_student else "")

        submitted = st.form_submit_button("Update" if current_student else "Create")
        if submitted:
            if not all([student_name, roll_number, campus, department, phone_number, cgpa > 0]):
                st.error("Please fill all required fields.")
            else:
                student_data = {
                    "student_name": student_name,
                    "roll_number": roll_number,
                    "campus": campus,
                    "department": department,
                    "phone_number": phone_number,
                    "email_id": email,
                    "cgpa": cgpa,
                    "resume": resume,
                    "user_role": "student"
                }
                if current_student:
                    result = db.update_student(current_student["student_id"], student_data)
                    st.success("Profile updated!" if result.get("success") else f"Error: {result.get('message')}")
                else:
                    result = db.create_student(student_data)
                    st.success("Profile created!" if result.get("success") else f"Error: {result.get('message')}")
                st.rerun()


show_student_profile()

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
