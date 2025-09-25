#ADMIN ACCESS ONLY
import streamlit as st
import sys, os
from datetime import datetime, date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "admin":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("🏢 Placement Drive Management")

db = MongoDB()
drives = db.get_all_drives()

with st.sidebar:
    st.markdown("#### <span style='font-size: 2em'>👤</span> " +
                st.session_state.get("user_email", "User"),
                unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")

st.subheader("Add New Placement Drive")
with st.form("add_drive_form"):
    job_title = st.text_input("Job Title *")
    company_name = st.text_input("Company Name *")
    job_desc = st.text_area("Job Description *")
    deadline = st.date_input("Deadline *", min_value=date.today())
    location = st.text_input("Location *")
    salary = st.number_input("Salary *", min_value=0.0, step=1000.0)
    cutoff = st.number_input("CGPA Cutoff *", min_value=0.0, max_value=10.0, step=0.01)
    company_website = st.text_input("Company Website (optional)")
    submit = st.form_submit_button("Add Drive")
    if submit:
        if not all([job_title, company_name, job_desc, deadline, location]):
            st.error("Fill all required fields.")
        else:
            drive_data = {
                "job_title": job_title,
                "company_name": company_name,
                "job_description": job_desc,
                "deadline": datetime.combine(deadline, datetime.min.time()),
                "location": location,
                "salary": salary,
                "cutoff": cutoff,
                "company_website": company_website,
            }
            res = db.create_drive(drive_data)
            if res.get("success"):
                st.success("Drive added successfully!")
                st.rerun()
            else:
                st.error(res.get("message", "Drive creation failed."))

st.markdown("---")
st.subheader("All Placement Drives")

if "edit_id" not in st.session_state:
    st.session_state["edit_id"] = None

if drives and len(drives) > 0:
    for drive in drives:
        with st.expander(f"{drive.get('company_name','')} - {drive.get('job_title','')} [ID: {drive.get('company_id', '')}]"):
            st.write(f"**Job Title:** {drive.get('job_title')}")
            st.write(f"**Company:** {drive.get('company_name')}")
            st.write(f"**Description:** {drive.get('job_description')}")
            st.write(f"**Deadline:** {drive.get('deadline')}")
            st.write(f"**Location:** {drive.get('location')}")
            st.write(f"**Salary:** {drive.get('salary')}")
            st.write(f"**CGPA Cutoff:** {drive.get('cutoff')}")
            st.write(f"**Website:** {drive.get('company_website','')}")
            st.write("---")
            col1, col2 = st.columns([1,1])

            with col1:
                if st.button(f"Delete", key=f"del_{drive['company_id']}"):
                    db.delete_drive(drive['company_id'])
                    st.success("Drive deleted!")
                    st.rerun()
            with col2:
                if st.button(f"Edit", key=f"edit_{drive['company_id']}"):
                    st.session_state["edit_id"] = drive['company_id']

            # Display edit form only if this drive is being edited
            if st.session_state["edit_id"] == drive['company_id']:
                with st.form(f"form_edit_{drive['company_id']}"):
                    new_job_title = st.text_input("Job Title", value=drive.get('job_title',''))
                    new_company_name = st.text_input("Company Name", value=drive.get('company_name',''))
                    new_job_desc = st.text_area("Job Description", value=drive.get('job_description',''))
                    new_deadline = st.date_input("Deadline", value=drive.get('deadline', date.today()))
                    new_location = st.text_input("Location", value=drive.get('location',''))
                    # Ensure salary is always a float (fix for your error)
                    salary_val = drive.get('salary', 0.0)
                    try: salary_val = float(str(salary_val).replace("L","").strip())
                    except Exception: salary_val = 0.0
                    new_salary = st.number_input("Salary", value=salary_val)
                    new_cutoff = st.number_input("CGPA Cutoff", min_value=0.0, max_value=10.0, step=0.01, value=float(drive.get('cutoff',0.0)))
                    new_company_website = st.text_input("Website", value=drive.get('company_website',''))
                    save = st.form_submit_button("Update Drive")
                    cancel = st.form_submit_button("Cancel Edit")
                    if save:
                        update_data = {
                            "job_title": new_job_title,
                            "company_name": new_company_name,
                            "job_description": new_job_desc,
                            "deadline": datetime.combine(new_deadline, datetime.min.time()),
                            "location": new_location,
                            "salary": new_salary,
                            "cutoff": new_cutoff,
                            "company_website": new_company_website
                        }
                        # DEBUG: Print what you're updating
                        st.write(f"Updating drive {drive['company_id']} with data:")
                        st.write(update_data)
                        
                        result = db.update_drive(drive['company_id'], update_data)
                        st.write(f"Update result: {result}")  # Debug the result
                        
                        if result.get("success"):
                            st.success("Drive updated!")
                            st.session_state["edit_id"] = None
                            st.rerun()
                        else:
                            st.error(f"Update failed: {result.get('message')}")
                        db.update_drive(drive['company_id'], update_data)
                        st.success("Drive updated!")
                        st.session_state["edit_id"] = None
                        st.rerun()
                    if cancel:
                        st.session_state["edit_id"] = None
else:
    st.info("No placement drives in the system.")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")

