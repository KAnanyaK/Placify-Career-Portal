import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../components'))
from database import MongoDB

if "user_logged_in" not in st.session_state or st.session_state.get("user_role") != "admin":
    st.warning("You are not authorized to view this page.")
    st.stop()

st.title("👨‍💼 Admin Dashboard")

db = MongoDB()
applications = db.get_all_applications()
students = list(db.students.find()) if db.connected else []
drives = list(db.drives.find()) if db.connected else []

with st.sidebar:
    st.markdown("#### <span style='font-size: 2em'>👤</span> " +
                st.session_state.get("user_email", "User"),
                unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")

# --- Data join: only placed applications ---
data_rows = []
for app in applications:
    if app.get("status","") == "Placed":
        student = db.students.find_one({"student_id": app["student_id"]})
        drive = db.drives.find_one({"company_id": app["company_id"]})
        data_rows.append({
            "Department": student.get("department","N/A") if student else "N/A",
            "Campus": student.get("campus","N/A") if student else "N/A",
            "Company": drive.get("company_name", "N/A") if drive else "N/A",
            "Student Name": student.get("student_name","N/A") if student else "N/A",
            "Branch": student.get("department","N/A") if student else "N/A"
        })

placement_df = pd.DataFrame(data_rows)

st.subheader("📊 Placement Analytics")

# Overall placements metric
st.metric("Total Students Placed", len(placement_df))

if not placement_df.empty:
    # Example color palette
    palette = ["#EF553B","#D1EF3B","#636EFA", "#00CC96", "#AB63FA", "#FFA15A"]
    # Dept-wise placements
    dept_counts = placement_df["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Placed"]
    fig1 = px.pie(
        dept_counts,
        names="Department",
        values="Placed",
        title="Placements Per Department",
        hole=0.4,
        color_discrete_sequence=palette
    )
    fig1.update_layout(width=600, height=400)
    st.plotly_chart(fig1, use_container_width=False)

    st.subheader("Company hires by Branch")

    # Prepare the data
    hires = placement_df.groupby(["Company","Branch"]).size().reset_index(name="Placed")

    # Create a grouped bar chart
    fig = px.bar(
        hires,
        x="Company",
        y="Placed",
        color="Branch",            # dept/branch as color
        barmode="group",           # or "stack" if you prefer stacked bars
        title="Company hires by Branch",
        color_discrete_sequence=palette
    )
    fig.update_layout(width=800, height=450)
    st.plotly_chart(fig, use_container_width=False)


    # Campus-wise placements
    # Campus-wise placements with distinct colors per bar
    campus_counts = placement_df["Campus"].value_counts().reset_index()
    campus_counts.columns = ["Campus", "Placed"]
    fig2 = px.bar(
        campus_counts,
        x="Campus",
        y="Placed",
        color="Campus",                        # one color per campus
        color_discrete_sequence=palette,       # your custom palette
        title="Campus-wise Placements"
    )
    fig2.update_layout(width=800, height=400)
    st.plotly_chart(fig2, use_container_width=False)
    
else:
    st.info("No students have been marked as 'Placed' yet.")
st.markdown("---")

btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("🏢 Placement Drive Management"):
        st.switch_page("pages/manage_drives.py")
with btn_col2:
    if st.button("📝 Student Applications"):
        st.switch_page("pages/manage_applications.py")

if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("main.py")
