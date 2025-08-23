import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import shutil

TASK_FILE = "tasks.csv"
BACKUP_COUNT = 2  # Keep last 2 backups

st.set_page_config(page_title="Daily Planner", page_icon="📝", layout="centered")
st.title("Daily Planner & Task Logger")

if "edit_idx" not in st.session_state:
    st.session_state["edit_idx"] = None

def create_backup():
    if os.path.exists(TASK_FILE):
        backups = sorted([f for f in os.listdir() if f.startswith("tasks_backup_")])
        if len(backups) >= BACKUP_COUNT:
            os.remove(backups[0])
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(TASK_FILE, f"tasks_backup_{timestamp}.csv")

# ---------- Task Form ----------
st.markdown("### Add a New Task")
with st.form("task_form"):
    task = st.text_input("Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date", value=date.today())
    note = st.text_area("Notes")
    submitted = st.form_submit_button("Add Task", use_container_width=True)

if submitted:
    if not task.strip():
        st.error("Task name cannot be empty.")
    else:
        new_task = {
            "Task": task,
            "Priority": priority,
            "Due Date": due_date.strftime("%Y-%m-%d"),
            "Note": note.replace("\n", " ").strip(),
            "Status": "Pending",
            "Created": date.today().strftime("%Y-%m-%d"),
            "Completed_TS": ""
        }
        if not os.path.exists(TASK_FILE):
            df = pd.DataFrame([new_task])
        else:
            df = pd.read_csv(TASK_FILE)
            if "Completed_TS" not in df.columns:
                df["Completed_TS"] = ""
            df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
        create_backup()
        df.to_csv(TASK_FILE, index=False)
        st.success("Task added!")

# ---------- Task Viewer ----------
st.markdown("---")
st.subheader("Your Tasks")

def calculate_streak(df):
    if "Completed_TS" not in df.columns:
        df["Completed_TS"] = ""
    streak = 0
    today = pd.Timestamp(date.today())
    df_completed = df[df['Status'] == 'Completed'].copy()
    if df_completed.empty:
        return 0
    df_completed['Completed_Date'] = pd.to_datetime(df_completed['Completed_TS'], errors='coerce')
    df_completed = df_completed.dropna(subset=['Completed_Date'])
    df_completed = df_completed.sort_values('Completed_Date', ascending=False)
    for comp_date in df_completed['Completed_Date']:
        if (today - comp_date.normalize()).days == streak:
            streak += 1
        else:
            break
    return streak

def last_month_summary(df):
    if "Completed_TS" not in df.columns:
        df["Completed_TS"] = ""
    today = pd.Timestamp(date.today())
    month_ago = today - pd.Timedelta(days=30)

    df_completed = df[df['Status'] == 'Completed'].copy()
    df_completed['Completed_Date'] = pd.to_datetime(df_completed['Completed_TS'], errors='coerce')
    df_completed = df_completed.dropna(subset=['Completed_Date'])
    tasks_done = df_completed[(df_completed['Completed_Date'] >= month_ago) & (df_completed['Completed_Date'] <= today)].shape[0]

    df_pending = df[df['Status'] == 'Pending'].copy()
    df_pending['Due_Date'] = pd.to_datetime(df_pending['Due Date'], errors='coerce')
    tasks_missed = df_pending[(df_pending['Due_Date'] >= month_ago) & (df_pending['Due_Date'] <= today)].shape[0]

    return tasks_done, tasks_missed

try:
    tasks_df = pd.read_csv(TASK_FILE)
    if "Completed_TS" not in tasks_df.columns:
        tasks_df["Completed_TS"] = ""
        tasks_df.to_csv(TASK_FILE, index=False)

    st.subheader(f"Current Streak: {calculate_streak(tasks_df)} days")
    done_30, missed_30 = last_month_summary(tasks_df)
    st.subheader(f"Last 30 Days: {done_30} tasks done, {missed_30} tasks missed")

    # Filters
    with st.expander("Filter Tasks", expanded=True):
        status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "Completed"])
        priority_filter = st.multiselect("Filter by Priority", options=["Low","Medium","High"], default=["Low","Medium","High"])

    filtered_df = tasks_df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    if priority_filter:
        filtered_df = filtered_df[filtered_df["Priority"].isin(priority_filter)]

    if not filtered_df.empty:
        st.markdown("Filtered Tasks")
        for idx, row in filtered_df.iterrows():
            col1, col2, col3, col4 = st.columns([6,2,2,2])
            due_date_obj = pd.to_datetime(row['Due Date'])
            today = pd.Timestamp(date.today())
            with col1:
                if due_date_obj < today and row['Status'] == 'Pending':
                    st.markdown(f"<p style='color:red; font-weight:bold;'>{row['Task']} — Overdue!</p>", unsafe_allow_html=True)
                else:
                    st.write(f"{row['Task']} — {row['Priority']} | Due: {row['Due Date']}")
                st.caption(f"{row['Note']}")
                st.caption(f"Created: {row['Created']} | Status: {row['Status']}")

            with col2:
                if row['Status'] == "Pending" and st.button("Complete", key=f"done_{idx}", use_container_width=True):
                    tasks_df.at[idx, 'Status'] = 'Completed'
                    tasks_df.at[idx, 'Completed_TS'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    create_backup()
                    tasks_df.to_csv(TASK_FILE, index=False)
                    st.experimental_rerun = None  # Remove experimental rerun entirely

            with col3:
                if st.button("Edit", key=f"edit_{idx}", use_container_width=True):
                    st.session_state["edit_idx"] = idx

            with col4:
                if st.button("Delete", key=f"delete_{idx}", use_container_width=True):
                    create_backup()
                    tasks_df = tasks_df.drop(index=idx).reset_index(drop=True)
                    tasks_df.to_csv(TASK_FILE, index=False)
                    st.session_state["edit_idx"] = None

            # Edit form
            if st.session_state.get("edit_idx") == idx:
                st.markdown("---")
                st.markdown(f"Editing Task: {row['Task']}")
                with st.form(f"edit_form_{idx}"):
                    new_task = st.text_input("Task", row["Task"])
                    new_priority = st.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(row["Priority"]))
                    new_due_date = st.date_input("Due Date", pd.to_datetime(row["Due Date"]))
                    new_note = st.text_area("Notes", row["Note"], height=150)
                    save_edit = st.form_submit_button("Save Changes")
                    if save_edit:
                        tasks_df.at[idx, "Task"] = new_task
                        tasks_df.at[idx, "Priority"] = new_priority
                        tasks_df.at[idx, "Due Date"] = new_due_date.strftime("%Y-%m-%d")
                        tasks_df.at[idx, "Note"] = new_note.replace("\n"," ").strip()
                        create_backup()
                        tasks_df.to_csv(TASK_FILE, index=False)
                        st.session_state["edit_idx"] = None

    # Bulk delete completed tasks
    st.markdown("Bulk Actions")
    if not tasks_df[tasks_df["Status"]=="Completed"].empty:
        if st.button("Delete All Completed Tasks", use_container_width=True):
            create_backup()
            tasks_df = tasks_df[tasks_df["Status"]!="Completed"]
            tasks_df.to_csv(TASK_FILE, index=False)
            st.session_state["edit_idx"]=None

except FileNotFoundError:
    st.info("No tasks found. Add your first task above!")