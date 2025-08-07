import streamlit as st
import pandas as pd
from datetime import date
import os

TASK_FILE = "tasks.csv"

st.title("📝 Daily Planner & Task Logger")

# ---------- Task Form ----------
with st.form("task_form"):
    task = st.text_input("Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", value=date.today())
    note = st.text_area("Notes")
    submitted = st.form_submit_button("Add Task")

if submitted:
    if not task.strip():
        st.error("❌ Task name cannot be empty.")
    else:
        new_task = {
            "Task": task,
            "Priority": priority,
            "Due Date": due_date.strftime("%Y-%m-%d"),
            "Note": note.replace("\n", " ").strip(),
            "Status": "Pending",
            "Created": date.today().strftime("%Y-%m-%d")
        }

        if not os.path.exists(TASK_FILE):
            df = pd.DataFrame([new_task])
        else:
            df = pd.read_csv(TASK_FILE)
            df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)

        df.to_csv(TASK_FILE, index=False)
        st.success("✅ Task added!")

# ---------- Task Viewer ----------
st.markdown("---")
st.subheader("📋 Your Tasks")

try:
    tasks_df = pd.read_csv(TASK_FILE)

    # 🔍 Filters
    st.markdown("### 🔍 Filter Tasks")
    status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "Completed"])
    priority_filter = st.multiselect("Filter by Priority", options=["Low", "Medium", "High"], default=["Low", "Medium", "High"])

    filtered_df = tasks_df.copy()

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    if priority_filter:
        filtered_df = filtered_df[filtered_df["Priority"].isin(priority_filter)]

    if not filtered_df.empty:
        st.markdown("### 📄 Filtered Tasks")
        for idx, row in filtered_df.iterrows():
            col1, col2 = st.columns([8, 2])
            with col1:
                st.write(f"**{row['Task']}** — {row['Priority']} priority | Due: {row['Due Date']}")
                st.write(f"📝 {row['Note']}")
                st.write(f"📅 Created: {row['Created']} | 🏁 Status: {row['Status']}")
            with col2:
                if row['Status'] == "Pending":
                    if st.button(f"✅ Done", key=f"done_{idx}"):
                        tasks_df.at[idx, 'Status'] = 'Completed'
                        tasks_df.to_csv(TASK_FILE, index=False)
                        st.success(f"Task '{row['Task']}' marked as Completed!")
                        st.rerun()
    else:
        st.info("No tasks match the selected filters.")

except FileNotFoundError:
    st.info("No tasks found. Add your first task above!")