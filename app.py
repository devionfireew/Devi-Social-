import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date
import time
import os
import json
import base64
from dateutil import parser
import re
import uuid
import io

st.set_page_config(page_title="Devi Social", page_icon="🔮", layout="wide", initial_sidebar_state="collapsed")

# ========================================
# PROFESSIONAL FACEBOOK UI CSS
# ========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&display=swap');

* { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] { background: #F0F2F5 !important; }
[data-testid="stSidebar"] { display: none !important; }

/* TOP NAV */
.top-nav { background: #FFF; border-bottom: 1px solid #CED0D4; padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.logo { font-size: 2rem; font-weight: 700; color: #0A66C2; }
.nav-icons { display: flex; gap: 20px; }
.nav-btn { background: none; border: none; font-size: 1.3rem; cursor: pointer; color: #65676B; padding: 8px 12px; border-radius: 50%; }
.nav-btn:hover { background: #F0F2F5; color: #0A66C2; }

/* MAIN LAYOUT */
.main-container { display: flex; gap: 16px; padding: 16px; max-width: 1400px; margin: 0 auto; }
.feed-col { flex: 2; }
.sidebar-col { flex: 1; }

/* POST CARD */
.post-card { background: #FFF; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); overflow: hidden; }
.post-header { padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E5E7EB; }
.post-author { display: flex; gap: 12px; align-items: center; flex: 1; }
.avatar { width: 40px; height: 40px; border-radius: 50%; background: #E4E6EB; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; overflow: hidden; border: 2px solid #E4E6EB; }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.post-author-info { flex: 1; }
.post-author-name { font-weight: 600; color: #050505; font-size: 0.95rem; cursor: pointer; }
.post-author-name:hover { text-decoration: underline; }
.post-meta { color: #65676B; font-size: 0.85rem; margin-top: 2px; }
.post-menu { background: none; border: none; cursor: pointer; color: #65676B; font-size: 1.2rem; padding: 4px 8px; }
.post-menu:hover { color: #0A66C2; }
.post-content { padding: 12px 16px; color: #050505; line-height: 1.5; }
.post-image { width: 100%; max-height: 400px; object-fit: cover; }
.post-footer { padding: 8px 16px; border-top: 1px solid #E5E7EB; }
.post-stats { display: flex; justify-content: space-between; font-size: 0.85rem; color: #65676B; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #E5E7EB; }
.post-actions { display: flex; gap: 0; }
.post-action { background: none; border: none; color: #65676B; padding: 8px; flex: 1; cursor: pointer; font-size: 0.9rem; border-radius: 4px; transition: all 0.2s; }
.post-action:hover { background: #F0F2F5; color: #0A66C2; }

/* STORY */
.story-container { background: #FFF; border-radius: 8px; padding: 12px; margin-bottom: 16px; display: flex; gap: 8px; overflow-x: auto; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.story-card { background: linear-gradient(135deg, #E4E6EB 0%, #D0D2D7 100%); border-radius: 8px; width: 100px; height: 150px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 2rem; border: 2px solid transparent; position: relative; overflow: hidden; }
.story-card img { width: 100%; height: 100%; object-fit: cover; }
.story-card:hover { border-color: #0A66C2; }
.story-label { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7); color: #FFF; padding: 4px; font-size: 0.75rem; text-align: center; }

/* COMMENT */
.comment-box { background: #F0F2F5; border-radius: 8px; padding: 12px; margin-top: 12px; }
.comment-item { padding: 8px; margin-bottom: 8px; background: #FFF; border-radius: 8px; border-left: 3px solid #0A66C2; display: flex; gap: 8px; }
.comment-avatar { width: 32px; height: 32px; border-radius: 50%; background: #E4E6EB; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; overflow: hidden; }
.comment-avatar img { width: 100%; height: 100%; object-fit: cover; }
.comment-content { flex: 1; }
.comment-author { font-weight: 600; color: #050505; font-size: 0.9rem; }
.comment-text { color: #65676B; margin-top: 4px; font-size: 0.9rem; }

/* FRIEND LIST */
.friend-item { padding: 12px; border-bottom: 1px solid #E5E7EB; cursor: pointer; display: flex; gap: 12px; align-items: center; }
.friend-item:hover { background: #F0F2F5; }
.friend-info { flex: 1; }
.friend-name { font-weight: 600; color: #050505; font-size: 0.95rem; }
.friend-status { color: #65676B; font-size: 0.85rem; }

/* CHAT */
.chat-container { background: #FFF; border-radius: 8px; height: 600px; display: flex; flex-direction: column; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.chat-header { padding: 12px 16px; border-bottom: 1px solid #E5E7EB; font-weight: 600; display: flex; justify-content: space-between; align-items: center; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; background: #FFF; }
.message { display: flex; gap: 8px; margin-bottom: 8px; align-items: flex-end; }
.message.own { justify-content: flex-end; }
.message-bubble { max-width: 60%; padding: 10px 14px; border-radius: 12px; word-wrap: break-word; font-size: 0.95rem; }
.message-bubble.own { background: #0A66C2; color: #FFF; border-radius: 12px 2px 12px 12px; }
.message-bubble.other { background: #E4E6EB; color: #050505; border-radius: 2px 12px 12px 12px; }
.chat-input-area { padding: 12px 16px; border-top: 1px solid #E5E7EB; display: flex; gap: 8px; align-items: flex-end; }
.chat-input { flex: 1; border: 1px solid #CED0D4; border-radius: 20px; padding: 10px 14px; font-size: 0.95rem; }
.send-btn { background: #0A66C2; color: #FFF; border: none; border-radius: 50%; width: 36px; height: 36px; cursor: pointer; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.send-btn:hover { background: #0854A0; }

/* CALL SCREEN */
.call-screen { background: linear-gradient(135deg, #0A66C2 0%, #0854A0 100%); min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #FFF; }
.call-avatar { width: 200px; height: 200px; border-radius: 50%; background: #E4E6EB; display: flex; align-items: center; justify-content: center; font-size: 4rem; margin-bottom: 30px; border: 4px solid #FFF; overflow: hidden; }
.call-avatar img { width: 100%; height: 100%; object-fit: cover; }
.call-name { font-size: 2rem; font-weight: 700; margin-bottom: 10px; }
.call-status { font-size: 1.1rem; margin-bottom: 40px; opacity: 0.9; }
.call-buttons { display: flex; gap: 30px; }
.call-btn { width: 70px; height: 70px; border-radius: 50%; border: none; cursor: pointer; font-size: 1.8rem; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.call-accept { background: #31A24C; color: #FFF; }
.call-accept:hover { background: #28932D; transform: scale(1.1); }
.call-reject { background: #E74C3C; color: #FFF; }
.call-reject:hover { background: #C0392B; transform: scale(1.1); }

/* BUTTONS */
.btn { background: #0A66C2; color: #FFF; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.btn:hover { background: #0854A0; }
.btn-secondary { background: #E4E6EB; color: #050505; }
.btn-secondary:hover { background: #D0D2D7; }
.btn-danger { background: #E74C3C; color: #FFF; }
.btn-danger:hover { background: #C0392B; }

/* PROFILE COVER */
.profile-cover { background: linear-gradient(135deg, #0A66C2 0%, #0854A0 100%); height: 200px; border-radius: 8px; margin-bottom: 20px; position: relative; background-size: cover; background-position: center; }
.profile-pic { width: 120px; height: 120px; border-radius: 50%; background: #E4E6EB; display: flex; align-items: center; justify-content: center; font-size: 3rem; border: 4px solid #FFF; margin-top: -60px; margin-left: 20px; overflow: hidden; }
.profile-pic img { width: 100%; height: 100%; object-fit: cover; }

/* STORY VIEWERS */
.viewers-list { background: #F0F2F5; border-radius: 8px; padding: 12px; margin-top: 12px; }
.viewer-item { padding: 8px; display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.viewer-avatar { width: 32px; height: 32px; border-radius: 50%; background: #E4E6EB; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; overflow: hidden; }
.viewer-avatar img { width: 100%; height: 100%; object-fit: cover; }
.viewer-name { font-weight: 600; color: #050505; font-size: 0.9rem; }

/* PRIVACY BADGE */
.privacy-badge { display: inline-block; background: #E4E6EB; color: #050505; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-left: 8px; }

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
    if "edit_post_id" not in st.session_state: st.session_state.edit_post_id = None
    if "show_comments" not in st.session_state: st.session_state.show_comments = {}
    if "view_story" not in st.session_state: st.session_state.view_story = None
    if "search_query" not in st.session_state: st.session_state.search_query = ""
    if "ai_chat" not in st.session_state: st.session_state.ai_chat = []

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
    except: return None

db = get_db()
FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ========================================
# HELPERS
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
    except: return {"ok": False, "err": "Network error"}

def get_profile(uid):
    if not db: return None
    try:
        d = db.collection("users").document(uid).get()
        return d.to_dict() if d.exists else None
    except: return None

def save_profile(uid, data):
    if not db: return False
    try:
        db.collection("users").document(uid).set(data, merge=True)
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
    if not db: return False
    try:
        db.collection("friend_requests").add({"sender_id": sender, "receiver_id": receiver, "status": "pending", "timestamp": datetime.now().isoformat()})
        return True
    except: return False

def accept_friend_req(rid):
    if not db: return False
    try:
        r = db.collection("friend_requests").document(rid).get().to_dict()
        db.collection("friend_requests").document(rid).update({"status": "accepted"})
        fid = f"{min(r['sender_id'], r['receiver_id'])}_{max(r['sender_id'], r['receiver_id'])}"
        db.collection("friends").document(fid).set({"users": [r["sender_id"], r["receiver_id"]], "timestamp": datetime.now().isoformat()})
        return True
    except: return False

def reject_friend_req(rid):
    if not db: return False
    try:
        db.collection("friend_requests").document(rid).delete()
        return True
    except: return False

def unfriend(me_id, other_id):
    if not db: return False
    try:
        fid = f"{min(me_id, other_id)}_{max(me_id, other_id)}"
        db.collection("friends").document(fid).delete()
        return True
    except: return False

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
        return notifs[:10]
    except: return []

def add_notification(user_id, text, type_="general"):
    if not db: return
    try:
        db.collection("notifications").add({"user_id": user_id, "text": text, "type": type_, "read": False, "timestamp": datetime.now().isoformat()})
    except: pass

def search_users(query):
    if not db or not query: return []
    try:
        results = []
        for u in db.collection("users").limit(50).stream():
            user = u.to_dict()
            if query.lower() in user.get("username", "").lower() or query.lower() in user.get("full_name", "").lower():
                results.append(user)
        return results[:10]
    except: return []

def can_view_post(post, viewer_id):
    privacy = post.get("privacy", "public")
    author_id = post.get("author_id")
    
    if privacy == "public": return True
    if viewer_id == author_id: return True
    if privacy == "friends":
        if not db: return False
        try:
            fid = f"{min(viewer_id, author_id)}_{max(viewer_id, author_id)}"
            return db.collection("friends").document(fid).get().exists
        except: return False
    return False

def can_view_story(story, viewer_id):
    privacy = story.get("privacy", "public")
    author_id = story.get("author_id")
    
    if privacy == "public": return True
    if viewer_id == author_id: return True
    if privacy == "friends":
        if not db: return False
        try:
            fid = f"{min(viewer_id, author_id)}_{max(viewer_id, author_id)}"
            return db.collection("friends").document(fid).get().exists
        except: return False
    return False

def chat_with_groq(message):
    if not GROQ_API_KEY: return "AI not available"
    try:
        st.session_state.ai_chat.append({"role": "user", "content": message})
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": st.session_state.ai_chat[-10:],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        r = requests.post(url, json=data, headers=headers, timeout=10)
        if r.status_code == 200:
            response = r.json()["choices"][0]["message"]["content"]
            st.session_state.ai_chat.append({"role": "assistant", "content": response})
            return response
        return "Error communicating with AI"
    except Exception as e:
        return f"AI Error: {str(e)}"

# ========================================
# AUTH
# ========================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#0A66C2;'>🔮 Devi Social</h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login"):
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if not em or not pw:
                        st.error("Fill all fields")
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
                fn = st.text_input("Full Name")
                un = st.text_input("Username")
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                cpw = st.text_input("Confirm Password", type="password")
                ct = st.text_input("City")
                bio = st.text_area("Bio", height=60)
                dp = st.file_uploader("Profile Picture", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([fn, un, em, pw, ct, bio]):
                        st.error("All fields required")
                    elif pw != cpw:
                        st.error("Passwords don't match")
                    elif len(pw) < 6:
                        st.error("Password min 6 chars")
                    else:
                        username_exists = False
                        if db:
                            try:
                                existing = list(db.collection("users").where("username", "==", un).limit(1).stream())
                                username_exists = len(existing) > 0
                            except: pass
                        
                        if username_exists:
                            st.error("Username taken")
                        else:
                            res = firebase_auth("signUp", em, pw)
                            if res["ok"]:
                                dp_data = file_to_base64(dp)
                                data = {
                                    "user_id": res["uid"], "email": em, "username": un, "full_name": fn,
                                    "city": ct, "bio": bio, "profile_pic": dp_data or "", "cover_pic": "",
                                    "created_at": datetime.now().isoformat()
                                }
                                if save_profile(res["uid"], data):
                                    st.session_state.authenticated = True
                                    st.session_state.user = data
                                    st.success("Account created!")
                                    time.sleep(1)
                                    st.rerun()
                            else: st.error(f"Signup failed: {res['err']}")
    st.stop()

# ========================================
# MAIN APP
# ========================================
me = st.session_state.user

# ========================================
# STORY VIEWING
# ========================================
if st.session_state.view_story:
    story = st.session_state.view_story
    st.markdown("<div style='background: linear-gradient(135deg, #0A66C2 0%, #0854A0 100%); min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #FFF; padding: 20px;'>", unsafe_allow_html=True)
    
    if story.get("image"):
        st.markdown(f"<img src='{story['image']}' style='max-width: 100%; max-height: 70vh; border-radius: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='margin-bottom: 20px;'>{story.get('text', 'Story')}</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='margin-bottom: 20px;'><strong>By @{story['author_username']}</strong></p>", unsafe_allow_html=True)
    
    # Add viewer
    if db:
        try:
            viewers = story.get("viewers", [])
            if me["user_id"] not in viewers:
                viewers.append(me["user_id"])
                db.collection("stories").document(story["id"]).update({"viewers": viewers})
        except: pass
    
    # Show viewers
    st.markdown(f"<h4>👁️ {len(story.get('viewers', []))} Views</h4>", unsafe_allow_html=True)
    
    if story.get("viewers"):
        st.markdown("<div class='viewers-list'>", unsafe_allow_html=True)
        for viewer_id in story.get("viewers", [])[:10]:
            viewer = get_profile(viewer_id)
            if viewer:
                st.markdown("<div class='viewer-item'>", unsafe_allow_html=True)
                if viewer.get("profile_pic"):
                    st.markdown(f"<div class='viewer-avatar'><img src='{viewer['profile_pic']}'></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='viewer-avatar'>👤</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='viewer-name'>@{viewer['username']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Back"):
        st.session_state.view_story = None
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ========================================
# CALLING SCREEN
# ========================================
if st.session_state.calling and st.session_state.call_user:
    call_user = st.session_state.call_user
    st.markdown("<div class='call-screen'>", unsafe_allow_html=True)
    
    if call_user.get("profile_pic"):
        st.markdown(f"<div class='call-avatar'><img src='{call_user['profile_pic']}'></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='call-avatar'>📱</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='call-name'>@{call_user['username']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='call-status'>Calling...</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        c1, c2 = st.columns(2)
        if c1.button("✅", use_container_width=True):
            st.success(f"Call connected!")
            time.sleep(2)
            st.session_state.calling = False
            st.rerun()
        if c2.button("❌", use_container_width=True):
            st.session_state.calling = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ========================================
# TOP NAV
# ========================================
st.markdown("<div class='top-nav'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown("<div class='logo'>f</div>", unsafe_allow_html=True)
with col2:
    search = st.text_input("🔍 Search friends...", key="search_bar", placeholder="Search by name or username")
    if search:
        st.session_state.search_query = search
with col3:
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("🏠", key="home_nav"):
        st.session_state.page = "home"
        st.rerun()
    if c2.button("👥", key="friends_nav"):
        st.session_state.page = "friends"
        st.rerun()
    if c3.button("🤖", key="ai_nav"):
        st.session_state.page = "ai"
        st.rerun()
    if c4.button("👤", key="profile_nav"):
        st.session_state.page = "profile"
        st.rerun()
    if c5.button("🔔", key="notif_nav"):
        st.session_state.page = "notifications"
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# SEARCH RESULTS
# ========================================
if st.session_state.search_query:
    st.markdown("<h3>Search Results</h3>", unsafe_allow_html=True)
    results = search_users(st.session_state.search_query)
    if not results:
        st.info("No users found")
    else:
        for user in results:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.markdown(f"**@{user['username']}** {user['full_name']}")
            
            status = get_friend_status(me["user_id"], user["user_id"])
            if status == "none":
                if col2.button("➕", key=f"add_{user['user_id']}"):
                    send_friend_req(me["user_id"], user["user_id"])
                    add_notification(user["user_id"], f"@{me['username']} sent request!", "friend_request")
                    st.success("Request sent!")
                    st.rerun()
            elif status == "friends":
                col2.markdown("✅")
            
            if col3.button("👤", key=f"view_prof_{user['user_id']}"):
                st.session_state.view_user = user["user_id"]
                st.session_state.page = "profile"
                st.rerun()
            
            if col4.button("💬", key=f"msg_{user['user_id']}"):
                st.session_state.chat_user = user
                st.session_state.page = "chat"
                st.rerun()
    
    st.divider()

# ========================================
# HOME PAGE
# ========================================
if st.session_state.page == "home":
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Story Section
        st.markdown("<h4>Stories</h4>", unsafe_allow_html=True)
        st.markdown("<div class='story-container'>", unsafe_allow_html=True)
        
        # Create Story
        if st.button("➕ Create Story", key="create_story"):
            st.session_state.page = "create_story"
            st.rerun()
        
        # Show Stories
        if db:
            try:
                stories = list(db.collection("stories").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream())
                for story in stories:
                    s = story.to_dict()
                    if can_view_story(s, me["user_id"]):
                        if s.get("image"):
                            st.markdown(f"<div class='story-card'><img src='{s['image']}'><div class='story-label'>@{s['author_username']}</div></div>", unsafe_allow_html=True)
                            if st.button("👁️", key=f"view_story_{story.id}"):
                                st.session_state.view_story = {**s, "id": story.id}
                                st.rerun()
            except: pass
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()
        
        # Create Post
        st.markdown("<div class='post-card'>", unsafe_allow_html=True)
        st.markdown("<div style='padding: 12px 16px;'>", unsafe_allow_html=True)
        st.markdown("<div style='display: flex; gap: 12px; align-items: center; margin-bottom: 12px;'>", unsafe_allow_html=True)
        if me.get("profile_pic"):
            st.markdown(f"<div class='avatar'><img src='{me['profile_pic']}'></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='avatar'>👤</div>", unsafe_allow_html=True)
        post_text = st.text_input("", placeholder="What's on your mind?", label_visibility="collapsed", key="post_input")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        img_file = col_a.file_uploader("📷 Photo", type=["jpg", "jpeg", "png"], key="img_upload")
        vid_file = col_b.file_uploader("🎥 Video", type=["mp4", "mov"], key="vid_upload")
        voice_file = col_c.file_uploader("🎤 Voice", type=["mp3", "wav"], key="voice_upload")
        privacy = col_d.selectbox("Privacy", ["Public", "Friends", "Private"], key="post_privacy")
        
        if st.button("📤 Post", use_container_width=True):
            if post_text.strip() or img_file or vid_file or voice_file:
                img_data = file_to_base64(img_file)
                vid_data = file_to_base64(vid_file)
                voice_data = file_to_base64(voice_file)
                if db:
                    post_id = str(uuid.uuid4())
                    db.collection("posts").document(post_id).set({
                        "post_id": post_id,
                        "author_id": me["user_id"],
                        "author_name": me["full_name"],
                        "author_username": me["username"],
                        "author_pic": me.get("profile_pic", ""),
                        "author_city": me.get("city", ""),
                        "content": post_text.strip(),
                        "image": img_data,
                        "video": vid_data,
                        "voice": voice_data,
                        "likes": 0,
                        "liked_by": [],
                        "views": 0,
                        "timestamp": datetime.now().isoformat(),
                        "privacy": privacy.lower()
                    })
                    st.success("Posted!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Add content")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Posts Feed
        if db:
            try:
                posts = list(db.collection("posts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50).stream())
                
                for post in posts:
                    p = post.to_dict()
                    pid = post.id
                    
                    if not can_view_post(p, me["user_id"]):
                        continue
                    
                    st.markdown("<div class='post-card'>", unsafe_allow_html=True)
                    
                    # Header
                    st.markdown("<div class='post-header'>", unsafe_allow_html=True)
                    st.markdown("<div class='post-author'>", unsafe_allow_html=True)
                    if p.get("author_pic"):
                        st.markdown(f"<div class='avatar'><img src='{p['author_pic']}'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='avatar'>👤</div>", unsafe_allow_html=True)
                    st.markdown("<div class='post-author-info'>", unsafe_allow_html=True)
                    if st.button(f"{p['author_name']}", key=f"author_{pid}"):
                        st.session_state.view_user = p["author_id"]
                        st.session_state.page = "profile"
                        st.rerun()
                    privacy_text = f"({p.get('privacy', 'public').upper()})"
                    st.markdown(f"<div class='post-meta'>@{p['author_username']} • {p.get('author_city', '')} • {p['timestamp'][:10]} <span class='privacy-badge'>{privacy_text}</span></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if p["author_id"] == me["user_id"]:
                        if st.button("⋮", key=f"menu_{pid}"):
                            st.session_state.edit_post_id = pid
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Content
                    st.markdown(f"<div class='post-content'>{p['content']}</div>", unsafe_allow_html=True)
                    if p.get("image"):
                        st.markdown(f"<img src='{p['image']}' class='post-image'>", unsafe_allow_html=True)
                    if p.get("video"):
                        st.video(p["video"])
                    if p.get("voice"):
                        st.audio(p["voice"])
                    
                    # Footer
                    st.markdown("<div class='post-footer'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='post-stats'><span>❤️ {p['likes']} Likes</span> <span>👁️ {p.get('views', 0)} Views</span> <span>💬 Comments</span></div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='post-actions'>", unsafe_allow_html=True)
                    col_x, col_y, col_z = st.columns(3)
                    
                    liked = me["user_id"] in p.get("liked_by", [])
                    if col_x.button(f"{'❤️' if liked else '🤍'} Like", use_container_width=True, key=f"like_{pid}"):
                        ref = db.collection("posts").document(pid)
                        if liked:
                            ref.update({"likes": firestore.Increment(-1), "liked_by": firestore.ArrayRemove([me["user_id"]])})
                        else:
                            ref.update({"likes": firestore.Increment(1), "liked_by": firestore.ArrayUnion([me["user_id"]])})
                            add_notification(p["author_id"], f"@{me['username']} liked!", "like")
                        st.rerun()
                    
                    if col_y.button("💬 Comment", use_container_width=True, key=f"comment_{pid}"):
                        st.session_state.show_comments[pid] = not st.session_state.show_comments.get(pid, False)
                        st.rerun()
                    
                    if col_z.button("🔗 Share", use_container_width=True, key=f"share_{pid}"):
                        st.info(f"Share link: Post ID {pid}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Comments
                    if st.session_state.show_comments.get(pid, False):
                        st.markdown("<div class='comment-box'>", unsafe_allow_html=True)
                        
                        try:
                            comments = list(db.collection("posts").document(pid).collection("comments").stream())
                            for comment in comments:
                                c = comment.to_dict()
                                cid = comment.id
                                st.markdown("<div class='comment-item'>", unsafe_allow_html=True)
                                if c.get("author_pic"):
                                    st.markdown(f"<div class='comment-avatar'><img src='{c['author_pic']}'></div>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div class='comment-avatar'>👤</div>", unsafe_allow_html=True)
                                st.markdown("<div class='comment-content'>", unsafe_allow_html=True)
                                st.markdown(f"<div class='comment-author'>{c['author_name']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='comment-text'>{c['text']}</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                if c["author_id"] == me["user_id"] and st.button("🗑️ Delete", key=f"del_comment_{cid}"):
                                    db.collection("posts").document(pid).collection("comments").document(cid).delete()
                                    st.rerun()
                        except: pass
                        
                        with st.form(f"comment_form_{pid}"):
                            comment_text = st.text_input("Write a comment...", key=f"comment_input_{pid}")
                            if st.form_submit_button("Post", use_container_width=True):
                                if comment_text.strip() and db:
                                    db.collection("posts").document(pid).collection("comments").add({
                                        "author_id": me["user_id"],
                                        "author_name": me["full_name"],
                                        "author_pic": me.get("profile_pic", ""),
                                        "text": comment_text.strip(),
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    add_notification(p["author_id"], f"@{me['username']} commented!", "comment")
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Edit/Delete
                    if st.session_state.edit_post_id == pid and p["author_id"] == me["user_id"]:
                        st.markdown("<div style='background: #F0F2F5; padding: 12px; border-radius: 8px;'>", unsafe_allow_html=True)
                        col_edit1, col_edit2 = st.columns(2)
                        if col_edit1.button("✏️ Edit", use_container_width=True, key=f"edit_btn_{pid}"):
                            new_content = st.text_area("Edit post", value=p["content"], key=f"edit_text_{pid}")
                            if st.button("Save", key=f"save_edit_{pid}"):
                                db.collection("posts").document(pid).update({"content": new_content})
                                st.session_state.edit_post_id = None
                                st.success("Updated!")
                                st.rerun()
                        if col_edit2.button("🗑️ Delete", use_container_width=True, key=f"delete_btn_{pid}"):
                            db.collection("posts").document(pid).delete()
                            st.session_state.edit_post_id = None
                            st.success("Deleted!")
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.divider()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("<h3>Stories</h3>", unsafe_allow_html=True)
        st.info("Create a story")
    
    with col3:
        st.markdown("<h3>Online Friends</h3>", unsafe_allow_html=True)
        friends = get_my_friends(me["user_id"])
        for f in friends[:5]:
            if f:
                st.markdown(f"<div class='friend-item'>", unsafe_allow_html=True)
                if f.get("profile_pic"):
                    st.markdown(f"<div class='avatar'><img src='{f['profile_pic']}'></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='avatar'>👤</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='friend-info'><div class='friend-name'>@{f['username']}</div><div class='friend-status'>Online</div></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# CREATE STORY
# ========================================
elif st.session_state.page == "create_story":
    st.markdown("<h2>Create Story</h2>", unsafe_allow_html=True)
    
    with st.form("create_story_form"):
        story_type = st.radio("Story Type", ["Image", "Text"])
        privacy = st.selectbox("Privacy", ["Public", "Friends", "Private"])
        
        if story_type == "Image":
            img = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("Post Story"):
                if img and db:
                    img_data = file_to_base64(img)
                    db.collection("stories").add({
                        "author_id": me["user_id"],
                        "author_username": me["username"],
                        "image": img_data,
                        "text": "",
                        "viewers": [],
                        "privacy": privacy.lower(),
                        "timestamp": datetime.now().isoformat()
                    })
                    st.success("Story posted!")
                    time.sleep(1)
                    st.session_state.page = "home"
                    st.rerun()
        else:
            text = st.text_area("Story Text")
            if st.form_submit_button("Post Story"):
                if text and db:
                    db.collection("stories").add({
                        "author_id": me["user_id"],
                        "author_username": me["username"],
                        "image": "",
                        "text": text,
                        "viewers": [],
                        "privacy": privacy.lower(),
                        "timestamp": datetime.now().isoformat()
                    })
                    st.success("Story posted!")
                    time.sleep(1)
                    st.session_state.page = "home"
                    st.rerun()

# ========================================
# FRIENDS PAGE
# ========================================
elif st.session_state.page == "friends":
    st.markdown("<h2>Friends</h2>", unsafe_allow_html=True)
    
    incoming = get_incoming_reqs(me["user_id"])
    if incoming:
        st.markdown("<h3>Friend Requests</h3>", unsafe_allow_html=True)
        for req in incoming:
            sender = get_profile(req["sender_id"])
            if sender:
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(f"**@{sender['username']}** {sender['full_name']}")
                if col2.button("✅", key=f"accept_{req['id']}"):
                    accept_friend_req(req["id"])
                    add_notification(req["sender_id"], f"@{me['username']} accepted!", "friend_accept")
                    st.rerun()
                if col3.button("❌", key=f"reject_{req['id']}"):
                    reject_friend_req(req["id"])
                    st.rerun()
        st.divider()
    
    st.markdown("<h3>My Friends</h3>", unsafe_allow_html=True)
    friends = get_my_friends(me["user_id"])
    if not friends:
        st.info("No friends yet")
    else:
        for f in friends:
            if f:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                col1.markdown(f"**@{f['username']}** {f['full_name']}")
                if col2.button("💬", key=f"chat_{f['user_id']}"):
                    st.session_state.chat_user = f
                    st.session_state.page = "chat"
                    st.rerun()
                if col3.button("📞", key=f"call_{f['user_id']}"):
                    st.session_state.calling = True
                    st.session_state.call_user = f
                    st.rerun()
                if col4.button("👤", key=f"view_{f['user_id']}"):
                    st.session_state.view_user = f["user_id"]
                    st.session_state.page = "profile"
                    st.rerun()
                if col5.button("❌", key=f"unfriend_{f['user_id']}"):
                    unfriend(me["user_id"], f["user_id"])
                    st.success("Unfriended!")
                    st.rerun()

# ========================================
# AI PAGE
# ========================================
elif st.session_state.page == "ai":
    st.markdown("<h2>🤖 Devi AI Assistant</h2>", unsafe_allow_html=True)
    st.markdown("Chat with Devi, your personal AI assistant!")
    
    # Display chat history
    for msg in st.session_state.ai_chat:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Devi:** {msg['content']}")
    
    # Input
    with st.form("ai_chat_form"):
        user_input = st.text_area("Ask Devi anything...")
        if st.form_submit_button("Send"):
            if user_input.strip():
                response = chat_with_groq(user_input)
                st.rerun()

# ========================================
# PROFILE PAGE
# ========================================
elif st.session_state.page == "profile":
    uid = st.session_state.get("view_user") or me["user_id"]
    prof = get_profile(uid)
    is_me = uid == me["user_id"]
    
    if not prof:
        st.error("Profile not found")
    else:
        cover_style = f"background-image: url('{prof.get('cover_pic')}');" if prof.get("cover_pic") else ""
        st.markdown(f"<div class='profile-cover' style='{cover_style}'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if prof.get("profile_pic"):
                st.markdown(f"<div class='profile-pic'><img src='{prof['profile_pic']}'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='profile-pic'>👤</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h2>{prof['full_name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p>@{prof['username']} • {prof.get('city', '')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>{prof.get('bio', '')}</p>", unsafe_allow_html=True)
            friends_count = len(get_my_friends(uid))
            st.markdown(f"<p><strong>{friends_count}</strong> Friends</p>", unsafe_allow_html=True)
        with col3:
            if is_me:
                if st.button("Edit Profile"):
                    st.session_state.page = "edit_profile"
                    st.rerun()
            else:
                status = get_friend_status(me["user_id"], uid)
                if status == "none":
                    if st.button("➕ Add Friend"):
                        send_friend_req(me["user_id"], uid)
                        add_notification(uid, f"@{me['username']} sent request!", "friend_request")
                        st.success("Request sent!")
                        st.rerun()
                elif status == "friends":
                    st.markdown("✅ Friends")
                    if st.button("💬 Message"):
                        st.session_state.chat_user = prof
                        st.session_state.page = "chat"
                        st.rerun()
                    if st.button("📞 Call"):
                        st.session_state.calling = True
                        st.session_state.call_user = prof
                        st.rerun()
        
        st.divider()
        
        st.markdown("<h3>Posts</h3>", unsafe_allow_html=True)
        if db:
            try:
                user_posts = list(db.collection("posts").where("author_id", "==", uid).order_by("timestamp", direction=firestore.Query.DESCENDING).stream())
                if not user_posts:
                    st.info("No posts")
                for post in user_posts:
                    p = post.to_dict()
                    pid = post.id
                    
                    if not can_view_post(p, me["user_id"]):
                        continue
                    
                    st.markdown("<div class='post-card'>", unsafe_allow_html=True)
                    st.markdown("<div class='post-header'>", unsafe_allow_html=True)
                    if p.get("author_pic"):
                        st.markdown(f"<div class='avatar'><img src='{p['author_pic']}'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='avatar'>👤</div>", unsafe_allow_html=True)
                    privacy_text = f"({p.get('privacy', 'public').upper()})"
                    st.markdown(f"<div class='post-author-info'><div class='post-author-name'>{p['author_name']}</div><div class='post-meta'>{p['timestamp'][:10]} <span class='privacy-badge'>{privacy_text}</span></div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='post-content'>{p['content']}</div>", unsafe_allow_html=True)
                    if p.get("image"):
                        st.markdown(f"<img src='{p['image']}' class='post-image'>", unsafe_allow_html=True)
                    if p.get("voice"):
                        st.audio(p["voice"])
                    
                    if is_me and st.button("🗑️ Delete", key=f"del_prof_post_{pid}"):
                        db.collection("posts").document(pid).delete()
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            except: pass

# ========================================
# EDIT PROFILE
# ========================================
elif st.session_state.page == "edit_profile":
    st.markdown("<h2>Edit Profile</h2>", unsafe_allow_html=True)
    prof = get_profile(me["user_id"])
    
    with st.form("edit_profile_form"):
        new_name = st.text_input("Full Name", value=prof.get("full_name", ""))
        new_bio = st.text_area("Bio", value=prof.get("bio", ""))
        new_city = st.text_input("City", value=prof.get("city", ""))
        new_pic = st.file_uploader("Profile Picture", type=["jpg", "jpeg", "png"])
        new_cover = st.file_uploader("Cover Picture", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Save"):
            pic_data = file_to_base64(new_pic) if new_pic else prof.get("profile_pic", "")
            cover_data = file_to_base64(new_cover) if new_cover else prof.get("cover_pic", "")
            save_profile(me["user_id"], {"full_name": new_name, "bio": new_bio, "city": new_city, "profile_pic": pic_data, "cover_pic": cover_data})
            st.session_state.user = get_profile(me["user_id"])
            st.success("Updated!")
            time.sleep(1)
            st.session_state.page = "profile"
            st.rerun()

# ========================================
# CHAT PAGE
# ========================================
elif st.session_state.page == "chat":
    if not st.session_state.chat_user:
        st.info("Select a friend")
    else:
        other = st.session_state.chat_user
        st.markdown(f"<h2>Chat with @{other['username']}</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("📞 Call"):
                st.session_state.calling = True
                st.session_state.call_user = other
                st.rerun()
        
        if db:
            try:
                m1 = [{**m.to_dict(), "me": True, "id": m.id} for m in db.collection("messages").where("sender_id","==",me["user_id"]).where("receiver_id","==",other["user_id"]).stream()]
                m2 = [{**m.to_dict(), "me": False, "id": m.id} for m in db.collection("messages").where("sender_id","==",other["user_id"]).where("receiver_id","==",me["user_id"]).stream()]
                msgs = sorted(m1 + m2, key=lambda x: x.get("timestamp",""))
                
                for m in msgs:
                    is_me = m.get("me", False)
                    bubble_cls = "message-bubble own" if is_me else "message-bubble other"
                    st.markdown(f"<div style='text-align: {'right' if is_me else 'left'};'><div class='{bubble_cls}'>{m['message_body']}</div></div>", unsafe_allow_html=True)
                    
                    if m.get("voice"):
                        st.audio(m["voice"])
                    
                    if is_me and st.button("🗑️", key=f"del_msg_{m['id']}"):
                        db.collection("messages").document(m["id"]).delete()
                        st.rerun()
            except: pass
        
        with st.form("send_message"):
            col1, col2, col3 = st.columns([3, 1, 1])
            msg = col1.text_input("Message", label_visibility="collapsed")
            voice = col2.file_uploader("🎤", type=["mp3", "wav"], key="voice_msg", label_visibility="collapsed")
            if col3.form_submit_button("📤"):
                if (msg.strip() or voice) and db:
                    voice_data = file_to_base64(voice)
                    db.collection("messages").add({
                        "sender_id": me["user_id"],
                        "receiver_id": other["user_id"],
                        "message_body": msg.strip(),
                        "voice": voice_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    add_notification(other["user_id"], f"New message from @{me['username']}!", "message")
                    st.rerun()

# ========================================
# NOTIFICATIONS
# ========================================
elif st.session_state.page == "notifications":
    st.markdown("<h2>Notifications</h2>", unsafe_allow_html=True)
    notifs = get_notifications(me["user_id"])
    if not notifs:
        st.info("No notifications")
    else:
        for n in notifs:
            st.markdown(f"<div style='background: #FFF; padding: 12px; border-radius: 8px; margin-bottom: 8px;'><p>{n['text']}</p><small style='color: #65676B;'>{n.get('timestamp', '')[:10]}</small></div>", unsafe_allow_html=True)

# ========================================
# LOGOUT
# ========================================
col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
