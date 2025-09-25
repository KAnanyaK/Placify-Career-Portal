#ADMIN ACCESS ONLY
import streamlit as st
import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "admin":
    st.warning("You are not authorized to view this page.")
    st.stop()

with st.sidebar:
    st.markdown("#### <span style='font-size: 2em'>👤</span> " +
                st.session_state.get("user_email", "User"),
                unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")

db = MongoDB()
st.title("📝 Student Applications")

STATUS_OPTIONS = [
    "Rejected", "Shortlisted", "Placed"
]

# --- Load and join all data ---
applications = db.get_all_applications()
data_rows = []
if applications:
    for app in applications:
        drive = db.drives.find_one({"company_id": app["company_id"]})
        student = db.students.find_one({"student_id": app["student_id"]})
        data_rows.append({
            "App Id": app["app_id"],
            "Student Name": student.get("student_name", "N/A") if student else "N/A",
            "Email": student.get("email_id", "N/A") if student else "N/A",
            "Roll Number": student.get("roll_number", "N/A") if student else "N/A",
            "Department": student.get("department", "N/A") if student else "N/A",
            "Company": drive.get("company_name", "N/A") if drive else "N/A",
            "Job Title": drive.get("job_title", "N/A") if drive else "N/A",
            "Applied On": str(app.get("apply_date", "")),
            "Status": app.get("status", "Not Selected")
        })
    df = pd.DataFrame(data_rows)

    # --- Add filters for all key columns ---
    filter_cols = st.columns(5)
    # Company filter
    comp_choices = ["All"] + sorted(df["Company"].unique())
    company = filter_cols[0].selectbox("Company", comp_choices)
    if company != "All":
        df = df[df["Company"] == company]
    # Department filter
    dept_choices = ["All"] + sorted(df["Department"].unique())
    dept = filter_cols[1].selectbox("Department", dept_choices)
    if dept != "All":
        df = df[df["Department"] == dept]
    # Status filter
    status_choices = ["All"] + STATUS_OPTIONS
    status_filter = filter_cols[2].selectbox("Status", status_choices)
    if status_filter != "All":
        df = df[df["Status"] == status_filter]

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Update Application Status")
    # Loop only through filtered applications for status update
    for app_id in df["App Id"]:
        app = next(a for a in applications if a["app_id"] == app_id)
        drive = db.drives.find_one({"company_id": app["company_id"]})
        student = db.students.find_one({"student_id": app["student_id"]})
        st.write(f"**App ID:** {app['app_id']} | **Student:** {student.get('student_name','')} ({student.get('email_id','')}) | **Drive:** {drive.get('company_name','')} - {drive.get('job_title','')}")
        new_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(app.get("status", "Not Selected")) if app.get("status") in STATUS_OPTIONS else 0,
            key=f"status_{app['app_id']}"
        )
        if st.button("Update Status", key=f"update_{app['app_id']}"):
            res = db.update_application_status(app["app_id"], new_status)
            if res.get("success"):
                st.success("Status updated!")
            else:
                st.error(res.get("message"))
            st.rerun()
        st.markdown("---")
else:
    st.info("No student applications found.")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
