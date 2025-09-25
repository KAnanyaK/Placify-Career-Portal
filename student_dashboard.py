import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "student":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("🎓 Student Dashboard")

db = MongoDB()
email = st.session_state.get("user_email")
student = db.get_student_by_email(email) if email else None
student_id = student.get("student_id") if student else None

if student:
    st.markdown(f"### 👋 Welcome **{student.get('student_name', 'Student')}**!")

total_drives = len(db.get_all_drives())
eligible_drives = len(db.get_eligible_drives(student.get("cgpa", 0.0)) if student else [])
applied_drives = len(db.get_student_applications(student_id) if student_id else [])

# Stat boxes (metric charts)
col1, col2, col3 = st.columns(3)
col1.metric("Total Drives", total_drives)
col2.metric("Eligible Drives", eligible_drives)
col3.metric("Drives Applied", applied_drives)

st.markdown("---")

# Add main navigation buttons
btn_col1, btn_col2, btn_col3 = st.columns(3)
with btn_col1:
    if st.button("👤 Profile"):
        st.switch_page("pages/student_profile.py")
with btn_col2:
    if st.button("📄 Applications"):
        st.switch_page("pages/view_applications.py")
with btn_col3:
    if st.button("📢 Placement Drives"):
        st.switch_page("pages/view_drives.py")

st.markdown("---")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
