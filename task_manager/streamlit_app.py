import os
import requests
import streamlit as st

# --- CONFIG & STYLING ---
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="TaskFlow Pro", page_icon="TaskFlow Pro", layout="wide")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .app-title { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #2563eb, #14b8a6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; }
    
    /* Kanban Card Styling */
    .card { 
        padding: 1rem; 
        border-radius: 12px; 
        margin-bottom: 1rem; 
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 5px solid transparent;
    }
    .card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4); }
    
    .todo { background: #ffffff; border-left-color: #94a3b8; }
    .in-progress { background: #eff6ff; border-left-color: #3b82f6; }
    .done { background: #ecfdf5; border-left-color: #10b981; }
    
    .card-title { font-weight: 700; font-size: 1.05rem; color: #0f172a; margin-bottom: 0.4rem; }
    .card-meta { color: #475569; font-size: 0.8rem; line-height: 1.4; }
    .priority-badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; background: rgba(15,23,42,0.08); text-transform: uppercase; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)


def api_request(method, path, **kwargs):
    url = f"{st.session_state.get('api_url', API_BASE)}{path}"
    try:
        res = requests.request(method, url, timeout=5, **kwargs)
        return res
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None


def fetch_data(endpoint, params=None):
    res = api_request("GET", endpoint, params=params)
    return res.json() if res and res.ok else []


# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.session_state.api_url = st.text_input("API Base URL", API_BASE)
    st.divider()
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.rerun()

# --- MAIN UI ---
st.markdown('<div class="app-title">TaskFlow Pro</div>', unsafe_allow_html=True)
st.caption("Streamlined Task Management & Team Collaboration")

tab_board, tab_create, tab_users = st.tabs(
    ["Kanban Board", "New Task", "Team"]
)

# Initialize users for selectboxes
users = fetch_data("/users/")
user_map = {u.get("id"): u.get("name") for u in users}
user_options = ["Unassigned"] + [f"{u['id']} - {u['name']}" for u in users]

# --- KANBAN BOARD TAB ---
with tab_board:
    # Filter Row
    f1, f2, f3 = st.columns(3)
    with f1:
        f_status = st.selectbox("Status", ["All", "todo", "in_progress", "done"])
    with f2:
        f_priority = st.selectbox("Priority", ["All", "low", "medium", "high"])
    with f3:
        f_user = st.selectbox("Assignee", ["All"] + user_options)

    # Fetch tasks based on filters
    params = {}
    if f_status != "All":
        params["status"] = f_status
    if f_priority != "All":
        params["priority"] = f_priority
    if f_user != "All" and f_user != "Unassigned":
        params["assigned_user_id"] = f_user.split(" - ")[0]

    tasks = fetch_data("/tasks/", params=params)

    # Render Board
    col_todo, col_ip, col_done = st.columns(3)
    cols = {"todo": col_todo, "in_progress": col_ip, "done": col_done}
    names = {"todo": "TO DO", "in_progress": "IN PROGRESS", "done": "DONE"}

    for status, col in cols.items():
        with col:
            st.markdown(f"### {names[status]}")
            status_tasks = [t for t in tasks if t.get("status") == status]

            if not status_tasks:
                st.caption("Empty")

            for t in status_tasks:
                with st.container():
                    st.markdown(
                        f"""
                    <div class="card {status.replace('_', '-')}">
                        <div class="card-title">{t['name']} <span class="priority-badge">{t['priority']}</span></div>
                        <div class="card-meta"><b>Assignee:</b> {user_map.get(t['assigned_user_id'], 'Unassigned')}</div>
                        <div class="card-meta">{t.get('description') or 'No description provided.'}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # No action buttons

# --- CREATE TASK TAB ---
with tab_create:
    st.subheader("Create a New Task")
    with st.form("task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Task Name*")
        priority = c1.selectbox("Priority", ["low", "medium", "high"], index=1)
        assigned = c2.selectbox("Assign To", user_options)
        status = c2.selectbox("Initial Status", ["todo", "in_progress", "done"])
        desc = st.text_area("Detailed Description")

        if st.form_submit_button("Deploy Task"):
            if name:
                payload = {
                    "name": name,
                    "description": desc,
                    "priority": priority,
                    "status": status,
                    "assigned_user_id": int(assigned.split(" - ")[0])
                    if " - " in assigned
                    else None,
                }
                res = api_request("POST", "/tasks/", json=payload)
                if res and res.ok:
                    st.success("Task created!")
                    st.rerun()
            else:
                st.warning("Task name is required.")

# --- USERS TAB ---
with tab_users:
    u_list, u_create = st.columns([2, 1])

    with u_create:
        st.subheader("Add Team Member")
        with st.form("user_form"):
            u_name = st.text_input("Full Name")
            u_role = st.selectbox("Role", ["member", "manager", "admin"])
            if st.form_submit_button("Add Member"):
                api_request("POST", "/users/", json={"name": u_name, "role": u_role})
                st.rerun()

    with u_list:
        st.subheader("Active Directory")
        st.dataframe(users, width="stretch")
