#STUDENT ACCESS ONLY
import streamlit as st
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "student":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("📢 All Placement Drives")

db = MongoDB()
email = st.session_state.get("user_email")
student = db.get_student_by_email(email) if email else None
student_id = student.get("student_id") if student else None

if not student:
    st.warning("Please update your profile to see eligible drives.")
    st.stop()

student_cgpa = student.get("cgpa", 0)
applied = set(app["company_id"] for app in db.get_student_applications(student_id))

all_drives = db.get_all_drives()

# Display drives with Apply buttons
if all_drives:
    for drive in all_drives:
        eligible = (drive.get("cutoff", 0) <= student_cgpa)
        already_applied = drive.get("company_id") in applied
        
        with st.expander(f"{drive.get('company_name', '')} - {drive.get('job_title', '')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Location:** {drive.get('location', '')}")
                st.write(f"**Deadline:** {drive.get('deadline', '')}")
                st.write(f"**CGPA Cutoff:** {drive.get('cutoff', '')}")
                st.write(f"**Salary:** {drive.get('salary', '')}")
                st.write(f"**Description:** {drive.get('job_description', '')}")
                
                if already_applied:
                    st.success("✅ Already Applied")
                elif eligible:
                    st.info("✅ Eligible")
                else:
                    st.warning("❌ Not Eligible (CGPA below cutoff)")
            
            with col2:
                # Show Apply button only if eligible and not already applied
                if eligible and not already_applied:
                    if st.button("Apply", key=f"apply_{drive.get('company_id')}"):
                        # Create new application
                        application_data = {
                            "student_id": student_id,
                            "company_id": drive.get("company_id"),
                            "apply_date": datetime.now().strftime("%Y-%m-%d"),
                            "status": "Not Applied"  # Default status as per your requirement
                        }
                        
                        result = db.create_application(application_data)
                        if result.get("success"):
                            st.success("🎉 Successfully applied!")
                            st.rerun()
                        else:
                            st.error(f"Application failed: {result.get('message', 'Unknown error')}")
else:
    st.info("No placement drives found.")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
