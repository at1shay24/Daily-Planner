import streamlit as st
import pandas as pd
from datetime import date
import os

TASK_FILE = "tasks.csv"

st.title("📝 Daily Planner & Task Logger")


with st.form("task_form"):
    task = st.text_input("Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", value=date.today())
    note = st.text_area("Notes")
    submitted = st.form_submit_button("Add Task")

if submitted:
    # Input validation
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


    

st.markdown("---")
st.subheader("📋 Your Tasks")

try:
    tasks_df = pd.read_csv(TASK_FILE)

    if not tasks_df.empty:
        for idx, row in tasks_df.iterrows():
            col1, col2 = st.columns([8, 2])
            with col1:
                st.write(f"**{row['Task']}** — {row['Priority']} priority | Due: {row['Due Date']}")
                st.write(f"📝 {row['Note']}")
                st.write(f"📅 Created: {row['Created']} | 🏁 Status: {row['Status']}")
            with col2:
                if row['Status'] != "Completed":
                    if st.button(f"✅ Done", key=f"done_{idx}"):
                        tasks_df.at[idx, 'Status'] = 'Completed'
                        tasks_df.to_csv(TASK_FILE, index=False)
                        st.success(f"Task '{row['Task']}' marked as Completed!")
                        st.rerun()
    else:
        st.info("No tasks found. Add your first task above!")

except FileNotFoundError:
    st.info("No tasks found. Add your first task above!")

