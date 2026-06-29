import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq
from datetime import datetime, date
import time
import os
import json
import base64
from dateutil import parser
import re

st.set_page_config(page_title="Devi Social", page_icon="🔮", layout="wide", initial_sidebar_state="collapsed")

# ========================================
# WHATSAPP DARK + FACEBOOK THEME CSS
# ========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&display=swap');

* {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [data-testid="stAppViewContainer"] {
    background: #0B141A !important;
    color: #E5E5EA !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

/* TOP HEADER BAR */
.top-header {
    background: #0B141A;
    border-bottom: 1px solid #1F2C34;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.header-logo {
    font-size: 1.8rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}

.header-icons {
    display: flex;
    gap: 16px;
    align-items: center;
}

.header-icon-btn {
    background: none;
    border: none;
    color: #E5E5EA;
    font-size: 1.3rem;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: all 0.2s;
}

.header-icon-btn:hover {
    background: #1F2C34;
    color: #22C35E;
}

/* SEARCH BAR */
.search-container {
    background: #0B141A;
    padding: 12px 16px;
    border-bottom: 1px solid #1F2C34;
}

.search-bar {
    background: #1F2C34;
    border: 1px solid #2A3F4B;
    border-radius: 24px;
    padding: 10px 16px;
    color: #E5E5EA;
    width: 100%;
    font-size: 0.95rem;
}

.search-bar::placeholder {
    color: #8A9BA8;
}

/* FILTER CHIPS */
.filter-chips {
    background: #0B141A;
    padding: 12px 16px;
    border-bottom: 1px solid #1F2C34;
    display: flex;
    gap: 8px;
    overflow-x: auto;
}

.chip {
    background: #1F2C34;
    color: #8A9BA8;
    border: 1px solid #2A3F4B;
    border-radius: 20px;
    padding: 8px 14px;
    font-size: 0.85rem;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
}

.chip:hover {
    background: #2A3F4B;
}

.chip.active {
    background: #22C35E;
    color: #0B141A;
    border-color: #22C35E;
    font-weight: 600;
}

/* MAIN CONTENT */
.main-content {
    background: #0B141A;
    padding-bottom: 80px;
}

/* STORY TRAY */
.story-tray {
    background: #0B141A;
    padding: 12px 16px;
    border-bottom: 1px solid #1F2C34;
    display: flex;
    gap: 8px;
    overflow-x: auto;
}

.story-card {
    background: linear-gradient(135deg, #1F2C34 0%, #2A3F4B 100%);
    border-radius: 12px;
    width: 100px;
    height: 160px;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}

.story-card:hover {
    border-color: #22C35E;
}

.story-create {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: #22C35E;
    font-weight: 700;
}

.story-user-name {
    position: absolute;
    bottom: 8px;
    left: 8px;
    right: 8px;
    color: #FFFFFF;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* POST PUBLISHER */
.publisher-card {
    background: #1F2C34;
    border: 1px solid #2A3F4B;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 16px;
}

.publisher-header {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #2A3F4B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    position: relative;
}

.avatar.online::after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    background: #22C35E;
    border-radius: 50%;
    border: 2px solid #1F2C34;
}

.publisher-input {
    background: #2A3F4B;
    border: 1px solid #3A4F5B;
    border-radius: 20px;
    padding: 10px 16px;
    color: #E5E5EA;
    width: 100%;
    margin-bottom: 12px;
    font-size: 0.95rem;
}

.publisher-input::placeholder {
    color: #8A9BA8;
}

.publisher-actions {
    display: flex;
    gap: 8px;
    justify-content: space-around;
}

.action-btn {
    background: transparent;
    border: none;
    color: #8A9BA8;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: all 0.2s;
    flex: 1;
    text-align: center;
}

.action-btn:hover {
    background: #2A3F4B;
    color: #22C35E;
}

/* POST CARD */
.post-card {
    background: #1F2C34;
    border: 1px solid #2A3F4B;
    border-radius: 12px;
    margin: 12px 16px;
    overflow: hidden;
}

.post-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #2A3F4B;
}

.post-author {
    display: flex;
    gap: 12px;
    align-items: center;
    flex: 1;
}

.post-author-info {
    flex: 1;
}

.post-author-name {
    color: #FFFFFF;
    font-weight: 600;
    font-size: 0.95rem;
}

.post-meta {
    color: #8A9BA8;
    font-size: 0.8rem;
    margin-top: 2px;
}

.post-follow-badge {
    background: transparent;
    border: 1px solid #22C35E;
    color: #22C35E;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
}

.post-menu {
    background: none;
    border: none;
    color: #8A9BA8;
    cursor: pointer;
    font-size: 1.2rem;
}

.post-content {
    padding: 12px 16px;
    color: #E5E5EA;
    line-height: 1.5;
}

.post-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
}

.post-footer {
    padding: 12px 16px;
    border-top: 1px solid #2A3F4B;
}

.post-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 0.85rem;
    color: #8A9BA8;
}

.post-actions {
    display: flex;
    gap: 8px;
}

.post-action {
    background: #2A3F4B;
    border: none;
    color: #8A9BA8;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    flex: 1;
    font-size: 0.9rem;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

.post-action:hover {
    background: #3A4F5B;
    color: #22C35E;
}

/* CHAT INTERFACE */
.chat-container {
    display: flex;
    height: calc(100vh - 180px);
    background: #0B141A;
}

.chat-list {
    width: 30%;
    border-right: 1px solid #1F2C34;
    overflow-y: auto;
}

.chat-window {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-header {
    background: #1F2C34;
    border-bottom: 1px solid #2A3F4B;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    background: #0B141A;
}

.message {
    display: flex;
    margin-bottom: 12px;
    align-items: flex-end;
    gap: 8px;
}

.message.own {
    justify-content: flex-end;
}

.message-bubble {
    max-width: 60%;
    padding: 10px 14px;
    border-radius: 12px;
    word-wrap: break-word;
}

.message-bubble.own {
    background: #22C35E;
    color: #0B141A;
    border-radius: 12px 2px 12px 12px;
}

.message-bubble.other {
    background: #2A3F4B;
    color: #E5E5EA;
    border-radius: 2px 12px 12px 12px;
}

.message-time {
    font-size: 0.7rem;
    color: #8A9BA8;
    margin-top: 4px;
}

.chat-input-area {
    background: #1F2C34;
    border-top: 1px solid #2A3F4B;
    padding: 12px 16px;
    display: flex;
    gap: 8px;
    align-items: flex-end;
}

.chat-input {
    background: #2A3F4B;
    border: 1px solid #3A4F5B;
    border-radius: 20px;
    padding: 10px 16px;
    color: #E5E5EA;
    flex: 1;
    font-size: 0.95rem;
}

.chat-input::placeholder {
    color: #8A9BA8;
}

.send-btn {
    background: #22C35E;
    border: none;
    color: #0B141A;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.send-btn:hover {
    background: #1AA84A;
}

.chat-row {
    padding: 12px 16px;
    border-bottom: 1px solid #1F2C34;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    gap: 12px;
    align-items: center;
}

.chat-row:hover {
    background: #1F2C34;
}

.chat-row-info {
    flex: 1;
}

.chat-row-name {
    color: #FFFFFF;
    font-weight: 600;
    font-size: 0.95rem;
}

.chat-row-preview {
    color: #8A9BA8;
    font-size: 0.85rem;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.unread-badge {
    background: #22C35E;
    color: #0B141A;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
}

/* CALLING SCREEN */
.call-screen {
    background: linear-gradient(135deg, #1F2C34 0%, #0B141A 100%);
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #FFFFFF;
}

.call-avatar {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: #2A3F4B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
    margin-bottom: 30px;
    border: 4px solid #22C35E;
}

.call-user-name {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.call-status {
    color: #8A9BA8;
    font-size: 1.1rem;
    margin-bottom: 40px;
}

.call-actions {
    display: flex;
    gap: 30px;
}

.call-btn {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.call-accept {
    background: #22C35E;
    color: #0B141A;
}

.call-accept:hover {
    background: #1AA84A;
    transform: scale(1.1);
}

.call-reject {
    background: #E74C3C;
    color: #FFFFFF;
}

.call-reject:hover {
    background: #C0392B;
    transform: scale(1.1);
}

/* BOTTOM NAVIGATION */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1F2C34;
    border-top: 1px solid #2A3F4B;
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 60px;
    z-index: 999;
}

.nav-item {
    background: none;
    border: none;
    color: #8A9BA8;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    flex: 1;
}

.nav-item:hover {
    color: #22C35E;
}

.nav-item.active {
    background: #22C35E;
    color: #0B141A;
    font-weight: 600;
}

.nav-badge {
    background: #E74C3C;
    color: #FFFFFF;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0B141A;
}

::-webkit-scrollbar-thumb {
    background: #2A3F4B;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #3A4F5B;
}

</style>
""", unsafe_allow_html=True)

# ========================================
# SESSION STATE
# ========================================
def init_session_state():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if "user" not in st.session_state: st.session_state.user = None
    if "page" not in st.session_state: st.session_state.page = "home"
    if "chat_user" not in st.session_state: st.session_state.chat_user = None
    if "calling" not in st.session_state: st.session_state.calling = False
    if "call_user" not in st.session_state: st.session_state.call_user = None
    if "view_user" not in st.session_state: st.session_state.view_user = None
    if "filter_active" not in st.session_state: st.session_state.filter_active = "All"

init_session_state()

# ========================================
# FIREBASE
# ========================================
@st.cache_resource
def get_db():
    try:
        if not firebase_admin._apps:
            fbase = dict(st.secrets.get("fbase", {}))
            if fbase:
                cred = credentials.Certificate(fbase)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            if os.path.exists("serviceAccountKey.json"):
                with open("serviceAccountKey.json") as f:
                    cred = credentials.Certificate(json.load(f))
                firebase_admin.initialize_app(cred)
                return firestore.client()
        return None
    except Exception as e:
        st.error(f"Firebase Error: {e}")
        return None

db = get_db()
FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")

# ========================================
# HELPER FUNCTIONS
# ========================================
def file_to_base64(file):
    if file is None: return None
    try:
        bytes_data = file.getvalue()
        b64 = base64.b64encode(bytes_data).decode()
        return f"data:{file.type};base64,{b64}"
    except: return None

def firebase_auth(endpoint, email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={FIREBASE_API_KEY}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        d = r.json()
        return {"ok": r.status_code == 200, "uid": d.get("localId"), "token": d.get("idToken"), "err": d.get("error", {}).get("message", "Error")}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def get_profile(uid):
    if not db: return None
    try:
        d = db.collection("users").document(uid).get()
        return d.to_dict() if d.exists else None
    except: return None

def save_profile(uid, data):
    if not db: return False
    try:
        db.collection("users").document(uid).set(data)
        return True
    except: return False

def get_friend_status(me_id, other_id):
    if not db or me_id == other_id: return "self"
    try:
        fid = f"{min(me_id, other_id)}_{max(me_id, other_id)}"
        if db.collection("friends").document(fid).get().exists: return "friends"
        for r in db.collection("friend_requests").where("receiver_id", "==", me_id).where("sender_id", "==", other_id).limit(1).stream():
            if r.to_dict().get("status") == "pending": return "pending_in"
        for r in db.collection("friend_requests").where("sender_id", "==", me_id).where("receiver_id", "==", other_id).limit(1).stream():
            if r.to_dict().get("status") == "pending": return "pending_out"
        return "none"
    except: return "none"

def send_friend_req(sender, receiver):
    if not db: return
    try:
        db.collection("friend_requests").add({"sender_id": sender, "receiver_id": receiver, "status": "pending", "time": datetime.now().isoformat()})
    except: pass

def accept_friend_req(rid):
    if not db: return
    try:
        r = db.collection("friend_requests").document(rid).get().to_dict()
        db.collection("friend_requests").document(rid).update({"status": "accepted"})
        fid = f"{min(r['sender_id'], r['receiver_id'])}_{max(r['sender_id'], r['receiver_id'])}"
        db.collection("friends").document(fid).set({"users": [r["sender_id"], r["receiver_id"]], "time": datetime.now().isoformat()})
    except: pass

def get_my_friends(uid):
    if not db: return []
    try:
        result = []
        for d in db.collection("friends").where("users", "array_contains", uid).stream():
            data = d.to_dict()
            other = data["users"][0] if data["users"][1] == uid else data["users"][1]
            p = get_profile(other)
            if p: result.append(p)
        return result
    except: return []

def get_incoming_reqs(uid):
    if not db: return []
    try:
        return [{**r.to_dict(), "id": r.id} for r in db.collection("friend_requests").where("receiver_id", "==", uid).stream() if r.to_dict().get("status") == "pending"]
    except: return []

def get_notifications(uid):
    if not db: return []
    try:
        notifs = []
        for n in db.collection("notifications").where("user_id", "==", uid).limit(50).stream():
            notifs.append({**n.to_dict(), "id": n.id})
        notifs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return notifs[:20]
    except: return []

def add_notification(user_id, text, type_="general"):
    if not db: return
    try:
        db.collection("notifications").add({"user_id": user_id, "text": text, "type": type_, "read": False, "timestamp": datetime.now().isoformat()})
    except: pass

# ========================================
# AUTH SCREEN
# ========================================
if not st.session_state.authenticated:
    st.markdown("<div style='background: #0B141A; min-height: 100vh; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; font-size:3rem; color:#22C35E; margin-bottom:10px;'>🔮 Devi Social</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#8A9BA8; font-size:1.1rem; margin-bottom:30px;'>Connect. Share. Grow.</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login"):
                em = st.text_input("Email", placeholder="your@email.com")
                pw = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Login", use_container_width=True):
                    if not em or not pw:
                        st.error("Please fill in all fields")
                    else:
                        res = firebase_auth("signInWithPassword", em, pw)
                        if res["ok"]:
                            prof = get_profile(res["uid"])
                            if prof:
                                st.session_state.authenticated = True
                                st.session_state.user = prof
                                st.rerun()
                            else: st.error("Profile not found")
                        else: st.error(f"Login failed: {res['err']}")
        
        with tab2:
            with st.form("signup"):
                fn = st.text_input("Full Name", placeholder="John Doe")
                un = st.text_input("Username", placeholder="johndoe")
                em = st.text_input("Email", placeholder="john@example.com")
                pw = st.text_input("Password", type="password", placeholder="Min 6 characters")
                bd = st.date_input("Birthday", value=date(2000,1,1), max_value=date.today())
                ct = st.text_input("City", placeholder="New York")
                bio = st.text_area("Bio", placeholder="Tell us about yourself", height=60)
                cpw = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                dp = st.file_uploader("Profile Picture", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([fn, un, em, pw, ct, bio]):
                        st.error("All fields are required")
                    elif pw != cpw:
                        st.error("Passwords don't match")
                    elif len(pw) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        username_exists = False
                        if db:
                            try:
                                existing = list(db.collection("users").where("username", "==", un).limit(1).stream())
                                username_exists = len(existing) > 0
                            except: pass
                        
                        if username_exists:
                            st.error("❌ Username already taken. Try another one!")
                        else:
                            res = firebase_auth("signUp", em, pw)
                            if res["ok"]:
                                dp_data = file_to_base64(dp)
                                data = {
                                    "user_id": res["uid"], "email": em, "username": un, "full_name": fn,
                                    "birthday": bd.isoformat(), "city": ct, "bio": bio, "profile_pic": dp_data or "",
                                    "cover_pic": "", "created_at": datetime.now().isoformat()
                                }
                                if save_profile(res["uid"], data):
                                    st.session_state.authenticated = True
                                    st.session_state.user = data
                                    st.success("✅ Account created successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to save profile")
                            else:
                                st.error(f"Signup failed: {res['err']}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ========================================
# MAIN APP
# ========================================
me = st.session_state.user
page = st.session_state.page

# ========================================
# CALLING SCREEN (Full Screen)
# ========================================
if st.session_state.calling and st.session_state.call_user:
    call_user = st.session_state.call_user
    st.markdown("<div class='call-screen'>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='call-avatar'>📱</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='call-user-name'>@{call_user['username']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='call-status'>Calling...</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        c1, c2 = st.columns(2)
        if c1.button("✅ Accept", use_container_width=True):
            st.success(f"Call connected with @{call_user['username']}!")
            time.sleep(2)
            st.session_state.calling = False
            st.rerun()
        if c2.button("❌ Reject", use_container_width=True):
            st.session_state.calling = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ========================================
# TOP HEADER
# ========================================
st.markdown("<div class='top-header'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown("<div class='header-logo'>🔮 Devi</div>", unsafe_allow_html=True)
with col2:
    search_query = st.text_input("", placeholder="Search posts, videos, or chats...", label_visibility="collapsed", key="search")
with col3:
    c1, c2, c3 = st.columns(3)
    if c1.button("📷", key="camera"):
        pass
    if c2.button("🔍", key="search_btn"):
        pass
    if c3.button("⋮", key="menu"):
        pass
st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# FILTER CHIPS
# ========================================
st.markdown("<div class='filter-chips'>", unsafe_allow_html=True)
chips = ["All", "Chats", "Feeds", "Videos/Reels", "+"]
for chip in chips:
    is_active = chip == st.session_state.filter_active
    cls = "chip active" if is_active else "chip"
    if st.button(chip, key=f"chip_{chip}", help=f"Filter by {chip}"):
        st.session_state.filter_active = chip
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# HOME PAGE
# ========================================
if page == "home":
    # Story Tray
    st.markdown("<div class='story-tray'>", unsafe_allow_html=True)
    st.markdown("<div class='story-card story-create'>+</div>", unsafe_allow_html=True)
    for i in range(5):
        st.markdown(f"<div class='story-card'><div class='story-user-name'>User {i+1}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Publisher
    st.markdown("<div class='publisher-card'>", unsafe_allow_html=True)
    st.markdown("<div class='publisher-header'>", unsafe_allow_html=True)
    st.markdown("<div class='avatar online'>👤</div>", unsafe_allow_html=True)
    post_text = st.text_input("", placeholder="What's on your mind? Share a post, text, or video...", label_visibility="collapsed", key="post_input")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='publisher-actions'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.button("📷 Photo/Video", use_container_width=True)
    col2.button("🎥 Go Live", use_container_width=True)
    col3.button("📝 Text Status", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Posts Feed
    if db:
        try:
            all_posts = list(db.collection("posts").limit(50).stream())
            all_posts.sort(key=lambda x: x.to_dict().get("timestamp", ""), reverse=True)
            
            for post in all_posts:
                p = post.to_dict()
                pid = post.id
                
                st.markdown("<div class='post-card'>", unsafe_allow_html=True)
                
                # Header
                st.markdown("<div class='post-header'>", unsafe_allow_html=True)
                st.markdown("<div class='post-author'>", unsafe_allow_html=True)
                st.markdown("<div class='avatar'>👤</div>", unsafe_allow_html=True)
                st.markdown("<div class='post-author-info'>", unsafe_allow_html=True)
                st.markdown(f"<div class='post-author-name'>{p.get('author_name', 'User')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='post-meta'>@{p.get('author_username', 'user')} • {p.get('author_city', '')} • {p.get('timestamp', '')[:10]}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<button class='post-follow-badge'>• Follow</button>", unsafe_allow_html=True)
                st.markdown("<button class='post-menu'>⋮</button>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Content
                st.markdown(f"<div class='post-content'>{p.get('content', '')}</div>", unsafe_allow_html=True)
                if p.get("image"):
                    st.markdown(f"<img src='{p['image']}' class='post-image'>", unsafe_allow_html=True)
                
                # Footer
                st.markdown("<div class='post-footer'>", unsafe_allow_html=True)
                st.markdown(f"<div class='post-stats'><span>❤️ {p.get('likes', 0)} Likes</span> <span>💬 0 Comments</span> <span>🔗 Share</span></div>", unsafe_allow_html=True)
                st.markdown("<div class='post-actions'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                col1.button("👍 Like", use_container_width=True, key=f"like_{pid}")
                col2.button("💬 Comment", use_container_width=True, key=f"comment_{pid}")
                col3.button("🔗 Share", use_container_width=True, key=f"share_{pid}")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading posts: {str(e)}")

# ========================================
# CHATS PAGE
# ========================================
elif page == "chats":
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Chat List
    st.markdown("<div class='chat-list'>", unsafe_allow_html=True)
    friends = get_my_friends(me["user_id"])
    for f in friends:
        if not f: continue
        st.markdown("<div class='chat-row'>", unsafe_allow_html=True)
        st.markdown("<div class='avatar online'>👤</div>", unsafe_allow_html=True)
        st.markdown("<div class='chat-row-info'>", unsafe_allow_html=True)
        if st.button(f"@{f['username']}", key=f"chat_{f['user_id']}", use_container_width=True):
            st.session_state.chat_user = f
            st.session_state.page = "chats"
            st.rerun()
        st.markdown(f"<div class='chat-row-preview'>Last message preview...</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='unread-badge'>2</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat Window
    if st.session_state.chat_user:
        other = st.session_state.chat_user
        st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
        
        # Chat Header
        st.markdown("<div class='chat-header'>", unsafe_allow_html=True)
        st.markdown(f"<div><strong>@{other['username']}</strong><br><small style='color:#8A9BA8;'>Online</small></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("📞", key=f"call_{other['user_id']}"):
            st.session_state.calling = True
            st.session_state.call_user = other
            st.rerun()
        if c2.button("🎥", key=f"video_{other['user_id']}"):
            pass
        if c3.button("⋮", key=f"menu_{other['user_id']}"):
            pass
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Messages
        st.markdown("<div class='chat-messages'>", unsafe_allow_html=True)
        if db:
            try:
                m1 = [{**m.to_dict(), "me": True} for m in db.collection("messages").where("sender_id","==",me["user_id"]).where("receiver_id","==",other["user_id"]).stream()]
                m2 = [{**m.to_dict(), "me": False} for m in db.collection("messages").where("sender_id","==",other["user_id"]).where("receiver_id","==",me["user_id"]).stream()]
                msgs = sorted(m1 + m2, key=lambda x: x.get("timestamp",""))
                
                for m in msgs:
                    is_me = m.get("me", False)
                    cls = "message own" if is_me else "message"
                    bubble_cls = "message-bubble own" if is_me else "message-bubble other"
                    st.markdown(f"<div class='{cls}'><div class='{bubble_cls}'>{m['message_body']}</div></div>", unsafe_allow_html=True)
            except: pass
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Input
        st.markdown("<div class='chat-input-area'>", unsafe_allow_html=True)
        msg = st.text_input("", placeholder="Type a message...", label_visibility="collapsed", key="msg_input")
        if st.button("📤", key="send_msg"):
            if msg.strip() and db:
                db.collection("messages").add({
                    "sender_id": me["user_id"], "receiver_id": other["user_id"],
                    "message_body": msg.strip(), "timestamp": datetime.now().isoformat()
                })
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:#8A9BA8; padding:40px;'>Select a chat to start messaging</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# BOTTOM NAVIGATION
# ========================================
st.markdown("<div class='bottom-nav'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    notifs = get_notifications(me["user_id"]) if db else []
    unread = len([n for n in notifs if not n.get("read", False)])
    badge = f"<span class='nav-badge'>{unread}</span>" if unread > 0 else ""
    if st.button(f"💬 Chats{badge}", use_container_width=True):
        st.session_state.page = "chats"
        st.rerun()

with col2:
    if st.button("📰 Feeds", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

with col3:
    if st.button("🎥 Watch", use_container_width=True):
        st.session_state.page = "watch"
        st.rerun()

with col4:
    if st.button("👥 Calls", use_container_width=True):
        st.session_state.page = "calls"
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
