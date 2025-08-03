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
    new_task = {
        "Task": task,
        "Priority": priority,
        "Due Date": due_date.strftime("%Y-%m-%d"),
        "Note": note,
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


if os.path.exists(TASK_FILE):
    st.markdown("---")
    st.subheader("📋 Your Tasks")
    df = pd.read_csv(TASK_FILE)
    st.dataframe(df)
