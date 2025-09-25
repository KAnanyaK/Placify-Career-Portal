#STUDENT ACCESS ONLY
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__) + '/../components')
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "student":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("📝 Apply to Drives")
db = MongoDB()
email = st.session_state.get("user_email")
student = db.get_student_by_email(email) if email else None
student_id = student.get("student_id") if student else None

if not student:
    st.warning("Update your profile before applying to drives.")
    st.stop()

student_cgpa = student.get("cgpa", 0)
applied = set(app["company_id"] for app in db.get_student_applications(student_id))

eligible_drives = db.get_eligible_drives(student_cgpa)
if not eligible_drives:
    st.info("No drives currently eligible for your CGPA.")
else:
    for drive in eligible_drives:
        if drive.get("company_id") in applied:
            st.success(f"Already applied to: {drive['company_name']} - {drive['job_title']}")
            continue
        with st.expander(f"{drive['company_name']} - {drive['job_title']} (Deadline: {drive.get('deadline')})"):
            st.write(f"**Location:** {drive.get('location','')}")
            st.write(f"**Salary:** {drive.get('salary','')}")
            st.write(f"**CGPA Cutoff:** {drive.get('cutoff','')}")
            st.write(f"**Job Description:** {drive.get('job_description','')}")
            if st.button(f"Apply for {drive['company_name']} - {drive['job_title']}", key=f"apply_{drive['company_id']}"):
                app_data = {
                    "student_id": student_id,
                    "company_id": drive["company_id"]
                }
                result = db.create_application(app_data)
                if result and result.get("success"):
                    st.success("Application submitted!")
                else:
                    st.error("Application failed: " + str(result.get("message")))
                st.rerun()

if st.button("Back to Drives"):
    st.switch_page("view_drives.py")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
