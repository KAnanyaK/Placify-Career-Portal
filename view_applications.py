#STUDENT ACCESS ONLY
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

# Authorization check
if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "student":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("📄 My Applications")

db = MongoDB()
student_id = st.session_state.get("student_id")
if not student_id:
    st.warning("Student ID not found. Please update your profile first.")
    st.stop()

applications = db.get_student_applications(student_id)

if applications:
    st.markdown(f"### You have applied to {len(applications)} drives:")
    for app in applications:
        drive_info = db.drives.find_one({"company_id": app["company_id"]}) if db.connected else None
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            company = drive_info.get('company_name') if drive_info else "Unknown Company"
            job_title = drive_info.get('job_title') if drive_info else "Unknown Title"
            st.write(f"**Company:** {company}")
            st.write(f"**Job Title:** {job_title}")
            st.write(f"**Applied On:** {app.get('apply_date','')}")
        with col2:
            status = app.get("status", "Pending")
            if status == "Rejected":
                color = "red"
            elif status == "Applied":
                color = "orange"
            elif status == "Shortlisted":
                color = "pink"
            elif status == "Placed":
                color = "green"
            else:
                color = "gray"
            st.markdown(
                f"**Status:** <span style='color:{color}; font-weight:bold'>{status}</span>",
                unsafe_allow_html=True
            )
else:
    st.info("You have not applied to any placement drives yet.")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
