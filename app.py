import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq
from datetime import datetime, date
import time
import os
import json
from dateutil import parser

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Devi Social",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CYBERPUNK / DARK THEME CSS
# =============================================================================
CYBERPUNK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #050510 0%, #0a0a1a 50%, #0d1b2a 100%);
        color: #e0e0e0;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #08081a 0%, #0f0f2d 100%) !important;
        border-right: 1px solid rgba(0, 243, 255, 0.3);
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00f3ff !important;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
    }

    .stButton > button {
        background: linear-gradient(90deg, #00f3ff, #0066cc) !important;
        color: #000 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.6) !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(0, 243, 255, 0.05) !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 10px; }

    .stTabs [data-baseweb="tab"] {
        background: rgba(0, 243, 255, 0.05) !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #00f3ff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 243, 255, 0.2) !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
    }

    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(0, 243, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0a1a; }
    ::-webkit-scrollbar-thumb { background: #00f3ff; border-radius: 4px; }

    .neon-text {
        color: #ff00ff;
        text-shadow: 0 0 10px rgba(255, 0, 255, 0.7);
        font-family: 'Orbitron', sans-serif;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #00f3ff, #0066cc);
        color: #000;
        padding: 12px 18px;
        border-radius: 18px 18px 0 18px;
        margin: 8px 0;
        max-width: 75%;
        float: right;
        clear: both;
        font-weight: 600;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.05rem;
        box-shadow: 0 4px 15px rgba(0, 243, 255, 0.3);
    }

    .chat-bubble-other {
        background: rgba(255, 255, 255, 0.08);
        color: #e0e0e0;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0;
        margin: 8px 0;
        max-width: 75%;
        float: left;
        clear: both;
        border: 1px solid rgba(0, 243, 255, 0.3);
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.05rem;
    }

    .post-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 243, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }

    .post-card:hover {
        border-color: #00f3ff;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.1);
        transform: translateY(-2px);
    }

    .user-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 243, 255, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }

    .user-card:hover {
        border-color: #00f3ff;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
    }

    .badge-friends {
        background: rgba(0, 255, 127, 0.2);
        border: 1px solid #00ff7f;
        color: #00ff7f;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
    }

    .comment-box {
        background: rgba(255, 255, 255, 0.02);
        border-left: 3px solid #00f3ff;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }

    .profile-header {
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.1), rgba(255, 0, 255, 0.1));
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 30px;
    }

    .profile-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 3px solid #00f3ff;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.4);
        object-fit: cover;
    }

    .whatsapp-chat {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 16px;
        border: 1px solid rgba(0, 243, 255, 0.2);
        height: 500px;
        overflow-y: auto;
        padding: 20px;
    }
</style>
"""

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

# =============================================================================
# FIREBASE INITIALIZATION
# =============================================================================
@st.cache_resource
def get_db():
    try:
        if not firebase_admin._apps:
            fbase_secrets = dict(st.secrets.get("fbase", {}))
            if fbase_secrets:
                cred = credentials.Certificate(fbase_secrets)
                firebase_admin.initialize_app(cred)
                return firestore.client()

            local_json_path = "serviceAccountKey.json"
            if os.path.exists(local_json_path):
                with open(local_json_path, "r") as f:
                    json_data = json.load(f)
                cred = credentials.Certificate(json_data)
                firebase_admin.initialize_app(cred)
                return firestore.client()

            st.error("Firebase credentials not found!")
            return None
    except Exception as e:
        st.error(f"Firebase error: {e}")
        return None

db = get_db()
FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")
AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

# =============================================================================
# SESSION STATE (PERSISTENT)
# =============================================================================
def init_state():
    defaults = {
        "authenticated": False,
        "user": None,
        "id_token": None,
        "current_page": "Feed",
        "selected_chat_user": None,
        "ai_messages": [],
        "view_profile_user": None,
        "last_activity": time.time()
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =============================================================================
# AUTH HELPERS
# =============================================================================
def api_sign_up(email, password):
    url = f"{AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        data = r.json()
        if r.status_code == 200:
            return {"ok": True, "uid": data["localId"], "token": data["idToken"]}
        return {"ok": False, "err": data.get("error", {}).get("message", "Unknown error")}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def api_sign_in(email, password):
    url = f"{AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        data = r.json()
        if r.status_code == 200:
            return {"ok": True, "uid": data["localId"], "token": data["idToken"]}
        return {"ok": False, "err": data.get("error", {}).get("message", "Unknown error")}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def fetch_profile(uid):
    if not db: return None
    try:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        return None

def save_profile(uid, data):
    if not db: return False
    try:
        db.collection("users").document(uid).set(data)
        return True
    except Exception as e:
        return False

def do_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =============================================================================
# FRIEND SYSTEM
# =============================================================================
def get_friend_status(me_id, other_id):
    if not db or me_id == other_id: return "self"
    fid = f"{min(me_id, other_id)}_{max(me_id, other_id)}"
    if db.collection("friends").document(fid).get().exists:
        return "friends"
    reqs = list(db.collection("friend_requests").where("receiver_id", "==", me_id).get())
    for r in reqs:
        d = r.to_dict()
        if d.get("sender_id") == other_id and d.get("status") == "pending":
            return "pending_received"
    reqs = list(db.collection("friend_requests").where("sender_id", "==", me_id).get())
    for r in reqs:
        d = r.to_dict()
        if d.get("receiver_id") == other_id and d.get("status") == "pending":
            return "pending_sent"
    return "none"

def send_friend_request(sender_id, receiver_id):
    if not db: return False
    try:
        db.collection("friend_requests").add({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        })
        return True
    except: return False

def accept_friend_request(req_doc_id):
    if not db: return False
    try:
        req_ref = db.collection("friend_requests").document(req_doc_id)
        req = req_ref.get().to_dict()
        sender_id, receiver_id = req["sender_id"], req["receiver_id"]
        req_ref.update({"status": "accepted"})
        fid = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        db.collection("friends").document(fid).set({
            "user1": sender_id, "user2": receiver_id,
            "users": [sender_id, receiver_id],
            "timestamp": datetime.now().isoformat()
        })
        return True
    except: return False

def reject_friend_request(req_doc_id):
    if not db: return False
    try:
        db.collection("friend_requests").document(req_doc_id).update({"status": "rejected"})
        return True
    except: return False

def cancel_friend_request(req_doc_id):
    if not db: return False
    try:
        db.collection("friend_requests").document(req_doc_id).delete()
        return True
    except: return False

def get_incoming_requests(user_id):
    if not db: return []
    reqs = list(db.collection("friend_requests").where("receiver_id", "==", user_id).get())
    return [{**r.to_dict(), "id": r.id} for r in reqs if r.to_dict().get("status") == "pending"]

def get_outgoing_request_id(sender_id, receiver_id):
    if not db: return None
    reqs = list(db.collection("friend_requests").where("sender_id", "==", sender_id).get())
    for r in reqs:
        d = r.to_dict()
        if d.get("receiver_id") == receiver_id and d.get("status") == "pending":
            return r.id
    return None

def get_friends(user_id):
    if not db: return []
    docs = list(db.collection("friends").where("users", "array_contains", user_id).get())
    friends = []
    for d in docs:
        data = d.to_dict()
        other = data["user1"] if data["user2"] == user_id else data["user2"]
        prof = fetch_profile(other)
        if prof: friends.append(prof)
    return friends

# =============================================================================
# SEARCH HELPERS
# =============================================================================
def search_users(query, exclude_id):
    if not db or not query: return []
    q = query.lower()
    docs = list(db.collection("users").limit(100).get())
    return [d.to_dict() for d in docs if d.to_dict().get("user_id") != exclude_id and (
        q in d.to_dict().get("username", "").lower() or
        q in d.to_dict().get("full_name", "").lower() or
        q in d.to_dict().get("email", "").lower() or
        q in d.to_dict().get("city", "").lower())]

def search_posts(query):
    if not db or not query: return []
    q = query.lower()
    docs = list(db.collection("posts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).get())
    results = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        if (q in data.get("post_content", "").lower() or
            q in data.get("author_name", "").lower() or
            q in data.get("author_username", "").lower()):
            results.append(data)
    return results

# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style='text-align:center; padding:30px 0;'>
                <h1 style='font-family:Orbitron; font-size:2.2rem; margin:0; color:#00f3ff;'> Devi Social</h1>
                <p style='color:#ff00ff; font-size:0.95rem; margin-top:8px; font-family:Rajdhani;'>Connect. Chat. Create.</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.authenticated and st.session_state.user:
            me = st.session_state.user
            incoming = get_incoming_requests(me["user_id"])
            if incoming:
                st.markdown(f"""
                    <div style='background:rgba(255,0,255,0.1); border:1px solid #ff00ff; border-radius:10px; padding:12px; margin-bottom:15px; text-align:center;'>
                        <span style='color:#ff00ff; font-family:Orbitron; font-size:0.9rem;'> {len(incoming)} Friend Request{'s' if len(incoming)>1 else ''}</span>
                    </div>
                """, unsafe_allow_html=True)

            # Profile pic in sidebar
            avatar_url = me.get("profile_pic", "")
            if avatar_url:
                st.image(avatar_url, width=80)
            st.markdown(f"""
                <div style='text-align:center; padding:20px; background:rgba(0,243,255,0.05); border-radius:12px; margin-bottom:25px; border:1px solid rgba(0,243,255,0.25);'>
                    <h3 style='margin:0; color:#00f3ff; font-family:Orbitron;'>@{me.get('username','user')}</h3>
                    <p style='margin:5px 0 0 0; color:#aaa; font-family:Rajdhani; font-size:1rem;'>{me.get('full_name','')}</p>
                    <p style='margin:2px 0 0 0; color:#666; font-size:0.8rem;'> {me.get('city','Unknown')}</p>
                </div>
            """, unsafe_allow_html=True)

            nav_items = [
                (" Feed", "Feed"),
                (" Search", "Search"),
                (" Chats", "Chats"),
                (" Friends", "Friends"),
                (" My Profile", "Profile"),
                (" AI Studio", "AI Studio")
            ]
            for label, page in nav_items:
                if st.button(label, use_container_width=True, key=f"nav_{page}"):
                    st.session_state.current_page = page
                    st.session_state.view_profile_user = None
                    st.rerun()

            st.divider()
            if st.button(" Logout", use_container_width=True, key="btn_logout"):
                do_logout()
        else:
            st.markdown("""
                <div style='text-align:center; padding:30px; color:#555; font-family:Rajdhani;'>
                    <p>Sign in to access the Devi universe</p>
                </div>
            """, unsafe_allow_html=True)

# =============================================================================
# AUTH SCREEN
# =============================================================================
def auth_screen():
    c1, c2, c3 = st.columns([1, 2.5, 1])
    with c2:
        st.markdown("""
            <div style='text-align:center; padding:50px 0 30px 0;'>
                <h1 style='font-size:3.5rem; font-family:Orbitron;'> Devi Social</h1>
                <p class='neon-text' style='font-size:1.2rem; margin-top:10px;'>The Future of Social Connection</p>
            </div>
        """, unsafe_allow_html=True)

        t1, t2 = st.tabs([" Login", " Sign Up"])

        with t1:
            with st.form("login"):
                st.subheader("Welcome Back")
                em = st.text_input("Email", placeholder="you@devi.social")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if not em or not pw:
                        st.error("Please fill in all fields")
                    else:
                        with st.spinner("Authenticating..."):
                            res = api_sign_in(em, pw)
                            if res["ok"]:
                                prof = fetch_profile(res["uid"])
                                if prof:
                                    st.session_state.authenticated = True
                                    st.session_state.user = prof
                                    st.session_state.id_token = res["token"]
                                    st.success("Welcome back!")
                                    time.sleep(0.8)
                                    st.rerun()
                                else:
                                    st.error("Profile not found")
                            else:
                                st.error(res["err"])

        with t2:
            with st.form("signup"):
                st.subheader("Join the Network")
                ca, cb = st.columns(2)
                with ca:
                    full_name = st.text_input("Full Name *", placeholder="Neo Anderson")
                    username = st.text_input("Username *", placeholder="neo")
                    email = st.text_input("Email *", placeholder="neo@matrix.com")
                    password = st.text_input("Password *", type="password", help="Minimum 6 characters")
                with cb:
                    birthday = st.date_input("Birthday *", value=date(2000, 1, 1), max_value=date.today())
                    city = st.text_input("City / Location *", placeholder="Zion")
                    bio = st.text_area("Bio / About Me *", placeholder="Tell the world who you are...", height=95)
                    confirm_password = st.text_input("Confirm Password *", type="password")

                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([full_name, username, email, password, city, bio]):
                        st.error("All fields are required")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating your profile..."):
                            if db:
                                existing = list(db.collection("users").where("username", "==", username).limit(1).get())
                                if existing:
                                    st.error("Username already taken")
                                    st.stop()

                            res = api_sign_up(email, password)
                            if res["ok"]:
                                profile_data = {
                                    "user_id": res["uid"],
                                    "email": email,
                                    "username": username,
                                    "full_name": full_name,
                                    "birthday": birthday.isoformat(),
                                    "city": city,
                                    "bio": bio,
                                    "profile_pic": "",
                                    "created_at": datetime.now().isoformat()
                                }
                                if save_profile(res["uid"], profile_data):
                                    st.session_state.authenticated = True
                                    st.session_state.user = profile_data
                                    st.session_state.id_token = res["token"]
                                    st.success("Welcome to Devi Social!")
                                    time.sleep(0.8)
                                    st.rerun()
                                else:
                                    st.error("Failed to save profile")
                            else:
                                st.error(res["err"])

# =============================================================================
# PROFILE MODULE
# =============================================================================
def profile_module():
    me = st.session_state.user
    view_id = st.session_state.get("view_profile_user")
    
    # If viewing someone else's profile
    if view_id and view_id != me["user_id"]:
        profile = fetch_profile(view_id)
        is_me = False
    else:
        profile = me
        is_me = True

    if not profile:
        st.error("Profile not found")
        return

    st.markdown(f"""
        <div class='profile-header'>
            <h1 style='font-family:Orbitron; color:#00f3ff;'> {profile.get('full_name', 'User')}</h1>
            <p style='color:#ff00ff; font-family:Rajdhani; font-size:1.2rem;'>@{profile.get('username', '')}</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        pic = profile.get("profile_pic", "")
        if pic:
            st.image(pic, width=150)
        else:
            st.markdown("""
                <div style='width:150px; height:150px; border-radius:50%; background:linear-gradient(135deg,#00f3ff,#ff00ff); display:flex; align-items:center; justify-content:center; font-size:3rem;'></div>
            """, unsafe_allow_html=True)

        if is_me:
            st.subheader(" Update Profile Picture")
            new_pic_url = st.text_input("Image URL (Imgur, etc.)", placeholder="https://i.imgur.com/xxx.jpg", key="profile_pic_url")
            if st.button("Update Picture", use_container_width=True):
                if new_pic_url:
                    db.collection("users").document(me["user_id"]).update({"profile_pic": new_pic_url})
                    st.session_state.user["profile_pic"] = new_pic_url
                    st.success("Profile picture updated!")
                    time.sleep(0.5)
                    st.rerun()

    with c2:
        st.markdown(f"""
            <div style='font-family:Rajdhani; font-size:1.1rem;'>
                <p><strong style='color:#00f3ff;'> Email:</strong> {profile.get('email', '')}</p>
                <p><strong style='color:#00f3ff;'> City:</strong> {profile.get('city', '')}</p>
                <p><strong style='color:#00f3ff;'> Birthday:</strong> {profile.get('birthday', '')}</p>
                <p><strong style='color:#00f3ff;'> Bio:</strong> {profile.get('bio', '')}</p>
            </div>
        """, unsafe_allow_html=True)

        if not is_me:
            status = get_friend_status(me["user_id"], profile["user_id"])
            if status == "none":
                if st.button(" Add Friend", use_container_width=True):
                    send_friend_request(me["user_id"], profile["user_id"])
                    st.success("Friend request sent!")
                    time.sleep(0.5)
                    st.rerun()
            elif status == "friends":
                st.markdown("<span class='badge-friends'> Friends</span>", unsafe_allow_html=True)
                if st.button(" Message", use_container_width=True):
                    st.session_state.selected_chat_user = profile
                    st.session_state.current_page = "Chats"
                    st.rerun()

    # Show user's posts
    st.divider()
    st.subheader(" Posts")
    posts = list(db.collection("posts").where("author_id", "==", profile["user_id"]).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).get())
    if not posts:
        st.info("No posts yet")
    for post in posts:
        p = post.to_dict()
        try:
            ts = parser.parse(p["timestamp"]).strftime("%b %d, %Y � %I:%M %p")
        except:
            ts = p.get("timestamp", "")
        st.markdown(f"""
            <div class='post-card'>
                <div style='color:#e0e0e0; font-family:Rajdhani; font-size:1.1rem; line-height:1.6;'>
                    {p.get('post_content','')}
                </div>
                <div style='color:#444; font-size:0.75rem; font-family:Rajdhani; margin-top:10px;'>{ts}</div>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FEED MODULE (with Images, Videos, Comments)
# =============================================================================
def feed_module():
    st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='font-family:Orbitron;'> Social Feed</h1>
            <p style='color:#888; font-family:Rajdhani; font-size:1.1rem;'>Share your thoughts with the Devi community</p>
        </div>
    """, unsafe_allow_html=True)

    if not db:
        st.error("Database unavailable")
        return

    me = st.session_state.user

    # Create Post
    with st.container():
        st.subheader(" Create Post")
        post_text = st.text_area("What's on your mind?", placeholder="Share something amazing...", height=80, key="post_input")
        
        c1, c2 = st.columns(2)
        with c1:
            image_url = st.text_input(" Image URL (optional)", placeholder="https://i.imgur.com/xxx.jpg", key="post_image")
        with c2:
            video_url = st.text_input(" Video URL (optional)", placeholder="https://youtube.com/...", key="post_video")
        
        if st.button(" Publish", key="btn_post"):
            if post_text.strip() or image_url or video_url:
                db.collection("posts").add({
                    "author_id": me["user_id"],
                    "author_name": me["full_name"],
                    "author_username": me["username"],
                    "author_city": me.get("city", ""),
                    "author_pic": me.get("profile_pic", ""),
                    "post_content": post_text.strip(),
                    "image_url": image_url,
                    "video_url": video_url,
                    "timestamp": datetime.now().isoformat(),
                    "likes_count": 0,
                    "liked_by": []
                })
                st.success("Posted successfully!")
                st.rerun()
            else:
                st.warning("Please enter some content or add a media URL")

    st.divider()
    st.subheader(" Latest Updates")

    posts = list(db.collection("posts").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50).get())
    if not posts:
        st.info("No posts yet. Be the first to share something!")

    for post in posts:
        p = post.to_dict()
        pid = post.id

        try:
            ts = parser.parse(p["timestamp"]).strftime("%b %d, %Y � %I:%M %p")
        except:
            ts = p.get("timestamp", "")

        likes = p.get("likes_count", 0)
        liked_by = p.get("liked_by", [])
        already_liked = me["user_id"] in liked_by

        # Author pic
        author_pic = p.get("author_pic", "")
        pic_html = f"<img src='{author_pic}' style='width:40px; height:40px; border-radius:50%; border:2px solid #00f3ff; margin-right:10px; object-fit:cover;'>" if author_pic else ""

        st.markdown(f"""
            <div class='post-card'>
                <div style='display:flex; align-items:center; margin-bottom:12px; cursor:pointer;' onclick='window.location.href=\"?profile={p.get("author_id","")}\"'>
                    {pic_html}
                    <div>
                        <span style='color:#00f3ff; font-family:Orbitron; font-size:1.15rem;'>{p.get('author_name','Anonymous')}</span>
                        <span style='color:#666; font-family:Rajdhani;'> @{p.get('author_username','')}</span>
                        <div style='color:#555; font-size:0.8rem; font-family:Rajdhani;'> {p.get('author_city','')} � {ts}</div>
                    </div>
                </div>
                <div style='color:#e0e0e0; font-family:Rajdhani; font-size:1.1rem; line-height:1.6; margin:15px 0;'>
                    {p.get('post_content','')}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Image
        img = p.get("image_url", "")
        if img:
            st.image(img, use_container_width=True)

        # Video
        vid = p.get("video_url", "")
        if vid:
            st.video(vid)

        # Like button
        c1, c2, c3 = st.columns([1, 1, 8])
        with c1:
            label = f"{'' if already_liked else ''} {likes}"
            if st.button(label, key=f"like_{pid}"):
                ref = db.collection("posts").document(pid)
                if not already_liked:
                    ref.update({
                        "likes_count": firestore.Increment(1),
                        "liked_by": firestore.ArrayUnion([me["user_id"]])
                    })
                else:
                    ref.update({
                        "likes_count": firestore.Increment(-1),
                        "liked_by": firestore.ArrayRemove([me["user_id"]])
                    })
                st.rerun()
        with c2:
            if st.button(f" Comments", key=f"comment_btn_{pid}"):
                st.session_state[f"show_comments_{pid}"] = not st.session_state.get(f"show_comments_{pid}", False)
                st.rerun()

        # Comments Section
        if st.session_state.get(f"show_comments_{pid}", False):
            st.markdown("<div style='margin-left:20px; border-left:2px solid rgba(0,243,255,0.3); padding-left:15px;'>", unsafe_allow_html=True)
            
            # Show existing comments
            comments = list(db.collection("posts").document(pid).collection("comments").order_by("timestamp").get())
            for c in comments:
                cd = c.to_dict()
                cts = cd.get("timestamp", "")[:16].replace("T", " ")
                st.markdown(f"""
                    <div class='comment-box'>
                        <strong style='color:#00f3ff;'>{cd.get('author_name','')}</strong>
                        <span style='color:#666; font-size:0.8rem;'> @{cd.get('author_username','')} � {cts}</span>
                        <p style='margin:5px 0 0 0; color:#e0e0e0;'>{cd.get('text','')}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Add comment
            with st.form(f"comment_form_{pid}", clear_on_submit=True):
                comment_text = st.text_input("Write a comment...", key=f"comment_input_{pid}")
                if st.form_submit_button("Post Comment"):
                    if comment_text.strip():
                        db.collection("posts").document(pid).collection("comments").add({
                            "author_id": me["user_id"],
                            "author_name": me["full_name"],
                            "author_username": me["username"],
                            "text": comment_text.strip(),
                            "timestamp": datetime.now().isoformat()
                        })
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # View Profile button
        if p.get("author_id") != me["user_id"]:
            if st.button(f" View @{p.get('author_username')}'s Profile", key=f"view_profile_{pid}"):
                st.session_state.view_profile_user = p["author_id"]
                st.session_state.current_page = "Profile"
                st.rerun()

        st.markdown("<hr style='border-color:rgba(0,243,255,0.1); margin:20px 0;'>", unsafe_allow_html=True)

# =============================================================================
# SEARCH MODULE
# =============================================================================
def search_module():
    st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='font-family:Orbitron;'> Search</h1>
            <p style='color:#888; font-family:Rajdhani; font-size:1.1rem;'>Find people and posts across the Devi network</p>
        </div>
    """, unsafe_allow_html=True)

    if not db:
        st.error("Database unavailable")
        return

    me = st.session_state.user
    t1, t2 = st.tabs([" Find People", " Search Posts"])

    with t1:
        query = st.text_input("Search by name, username, email or city...", placeholder="Type to search...", key="search_users_input")
        if query:
            results = search_users(query, me["user_id"])
            if not results:
                st.info("No users found")
            else:
                st.markdown(f"<p style='color:#888; font-family:Rajdhani;'>Found {len(results)} result(s)</p>", unsafe_allow_html=True)
                for u in results:
                    status = get_friend_status(me["user_id"], u["user_id"])
                    with st.container():
                        pic = u.get("profile_pic", "")
                        pic_html = f"<img src='{pic}' style='width:60px; height:60px; border-radius:50%; border:2px solid #00f3ff; margin-right:15px; object-fit:cover;'>" if pic else ""
                        st.markdown(f"""
                            <div class='user-card'>
                                <div style='display:flex; align-items:center;'>
                                    {pic_html}
                                    <div>
                                        <h3 style='margin:0; color:#00f3ff; font-family:Orbitron;'>@{u.get('username','user')}</h3>
                                        <p style='margin:4px 0; color:#ccc; font-family:Rajdhani; font-size:1.05rem;'><strong>{u.get('full_name','')}</strong></p>
                                        <p style='margin:2px 0; color:#888; font-size:0.9rem; font-family:Rajdhani;'> {u.get('city','')}</p>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        cols = st.columns([1, 1, 1])
                        if status == "none":
                            with cols[0]:
                                if st.button(" Add Friend", use_container_width=True, key=f"addf_{u['user_id']}"):
                                    send_friend_request(me["user_id"], u["user_id"])
                                    st.success("Friend request sent!")
                                    time.sleep(0.5)
                                    st.rerun()
                            with cols[1]:
                                if st.button(" Profile", use_container_width=True, key=f"prof_{u['user_id']}"):
                                    st.session_state.view_profile_user = u["user_id"]
                                    st.session_state.current_page = "Profile"
                                    st.rerun()
                        elif status == "friends":
                            with cols[0]:
                                st.markdown("<span class='badge-friends'> Friends</span>", unsafe_allow_html=True)
                            with cols[1]:
                                if st.button(" Message", use_container_width=True, key=f"msgfr_{u['user_id']}"):
                                    st.session_state.selected_chat_user = u
                                    st.session_state.current_page = "Chats"
                                    st.rerun()
                            with cols[2]:
                                if st.button(" Profile", use_container_width=True, key=f"prof2_{u['user_id']}"):
                                    st.session_state.view_profile_user = u["user_id"]
                                    st.session_state.current_page = "Profile"
                                    st.rerun()

    with t2:
        query = st.text_input("Search posts by keyword, author or city...", placeholder="Type to search posts...", key="search_posts_input")
        if query:
            results = search_posts(query)
            if not results:
                st.info("No posts found")
            else:
                for p in results:
                    pid = p["id"]
                    try:
                        ts = parser.parse(p["timestamp"]).strftime("%b %d, %Y � %I:%M %p")
                    except:
                        ts = p.get("timestamp", "")
                    likes = p.get("likes_count", 0)
                    liked_by = p.get("liked_by", [])
                    already_liked = me["user_id"] in liked_by

                    st.markdown(f"""
                        <div class='post-card'>
                            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                                <div>
                                    <span style='color:#00f3ff; font-family:Orbitron; font-size:1.15rem;'>{p.get('author_name','')}</span>
                                    <span style='color:#666; font-family:Rajdhani;'> @{p.get('author_username','')}</span>
                                </div>
                                <span style='color:#555; font-size:0.8rem; font-family:Rajdhani;'>{ts}</span>
                            </div>
                            <div style='color:#e0e0e0; font-family:Rajdhani; font-size:1.1rem; line-height:1.6; margin:15px 0;'>
                                {p.get('post_content','')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if p.get("image_url"):
                        st.image(p["image_url"], use_container_width=True)

                    c1, c2 = st.columns([1, 10])
                    with c1:
                        label = f"{'' if already_liked else ''} {likes}"
                        if st.button(label, key=f"search_like_{pid}"):
                            ref = db.collection("posts").document(pid)
                            if not already_liked:
                                ref.update({
                                    "likes_count": firestore.Increment(1),
                                    "liked_by": firestore.ArrayUnion([me["user_id"]])
                                })
                            else:
                                ref.update({
                                    "likes_count": firestore.Increment(-1),
                                    "liked_by": firestore.ArrayRemove([me["user_id"]])
                                })
                            st.rerun()

# =============================================================================
# CHATS MODULE (WhatsApp Style)
# =============================================================================
def chat_module():
    st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='font-family:Orbitron;'> Devi Messenger</h1>
            <p style='color:#888; font-family:Rajdhani; font-size:1.1rem;'>WhatsApp-style messaging</p>
        </div>
    """, unsafe_allow_html=True)

    if not db:
        st.error("Database unavailable")
        return

    me = st.session_state.user
    c1, c2 = st.columns([1, 2.5])

    # Contacts Sidebar
    with c1:
        st.subheader(" Chats")
        search = st.text_input("Search contacts...", placeholder="username...")

        # Show friends first, then others
        friends = get_friends(me["user_id"])
        all_users = list(db.collection("users").limit(100).get())
        others = [u.to_dict() for u in all_users if u.to_dict().get("user_id") != me["user_id"] and u.to_dict() not in friends]

        if friends:
            st.markdown("<p style='color:#00ff7f; font-family:Rajdhani;'> Friends</p>", unsafe_allow_html=True)
            for f in friends:
                pic = f.get("profile_pic", "")
                pic_html = f"<img src='{pic}' style='width:35px; height:35px; border-radius:50%; border:1px solid #00f3ff; margin-right:8px; object-fit:cover;'>" if pic else ""
                if st.button(f"{pic_html} @{f.get('username','')}", use_container_width=True, key=f"chatf_{f['user_id']}"):
                    st.session_state.selected_chat_user = f
                    st.rerun()

        if search:
            s = search.lower()
            filtered = [u for u in others if s in u.get("username", "").lower() or s in u.get("email", "").lower()]
            if filtered:
                st.markdown("<p style='color:#888; font-family:Rajdhani;'>Others</p>", unsafe_allow_html=True)
                for u in filtered:
                    if st.button(f"@{u.get('username','')}", use_container_width=True, key=f"chatu_{u['user_id']}"):
                        st.session_state.selected_chat_user = u
                        st.rerun()

    # Chat Window
    with c2:
        if not st.session_state.get("selected_chat_user"):
            st.markdown("""
                <div style='text-align:center; padding:120px 20px; color:#444; font-family:Rajdhani;'>
                    <h2>Select a contact to start messaging</h2>
                    <p>Your conversations will appear here</p>
                </div>
            """, unsafe_allow_html=True)
            return

        other = st.session_state.selected_chat_user
        pic = other.get("profile_pic", "")
        pic_html = f"<img src='{pic}' style='width:40px; height:40px; border-radius:50%; border:2px solid #00f3ff; margin-right:10px; object-fit:cover;'>" if pic else ""
        
        st.markdown(f"""
            <div style='padding:15px; background:rgba(0,243,255,0.05); border-radius:12px; margin-bottom:15px; border:1px solid rgba(0,243,255,0.25); display:flex; align-items:center;'>
                {pic_html}
                <div>
                    <h3 style='margin:0; color:#00f3ff; font-family:Orbitron;'>@{other.get('username', 'user')}</h3>
                    <p style='margin:0; color:#888; font-family:Rajdhani; font-size:0.9rem;'>{other.get('full_name', '')}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Messages
        uid1, uid2 = me["user_id"], other["user_id"]
        m1 = list(db.collection("messages").where("sender_id", "==", uid1).where("receiver_id", "==", uid2).get())
        m2 = list(db.collection("messages").where("sender_id", "==", uid2).where("receiver_id", "==", uid1).get())

        msgs = []
        for m in m1:
            d = m.to_dict(); d["dir"] = "sent"; msgs.append(d)
        for m in m2:
            d = m.to_dict(); d["dir"] = "received"; msgs.append(d)
        msgs.sort(key=lambda x: x.get("timestamp", ""))

        chat_container = st.container()
        with chat_container:
            if not msgs:
                st.markdown("""
                    <div style='text-align:center; padding:60px; color:#444; font-family:Rajdhani;'>
                        <p>No messages yet. Say hello! </p>
                    </div>
                """, unsafe_allow_html=True)

            for m in msgs:
                is_sent = m["dir"] == "sent"
                cls = "chat-bubble-user" if is_sent else "chat-bubble-other"
                align = "right" if is_sent else "left"
                tm = m.get("timestamp", "")[11:16]
                st.markdown(f"""
                    <div style='text-align:{align}; margin:8px 0; overflow:hidden;'>
                        <div class='{cls}' style='display:inline-block; text-align:left;'>
                            {m.get('message_body', '')}
                        </div>
                        <div style='clear:both;'></div>
                        <div style='font-size:0.65rem; color:#555; margin-top:2px; text-align:{align}; font-family:Rajdhani;'>{tm}</div>
                    </div>
                """, unsafe_allow_html=True)

        # Message Input (WhatsApp style at bottom)
        st.divider()
        with st.form("msg_form", clear_on_submit=True):
            cols = st.columns([5, 1])
            with cols[0]:
                txt = st.text_input("Message...", placeholder="Type a message...", label_visibility="collapsed", key="msg_input")
            with cols[1]:
                submitted = st.form_submit_button("", use_container_width=True)
            if submitted and txt.strip():
                db.collection("messages").add({
                    "sender_id": me["user_id"],
                    "sender_name": me["full_name"],
                    "receiver_id": other["user_id"],
                    "receiver_name": other["full_name"],
                    "message_body": txt.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "read": False
                })
                st.rerun()

# =============================================================================
# FRIENDS MODULE
# =============================================================================
def friends_module():
    st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='font-family:Orbitron;'> Friends</h1>
            <p style='color:#888; font-family:Rajdhani; font-size:1.1rem;'>Manage your connections</p>
        </div>
    """, unsafe_allow_html=True)

    if not db:
        st.error("Database unavailable")
        return

    me = st.session_state.user
    incoming = get_incoming_requests(me["user_id"])
    if incoming:
        st.markdown(f"""
            <div style='background:rgba(255,0,255,0.05); border:1px solid #ff00ff; border-radius:12px; padding:20px; margin-bottom:30px;'>
                <h3 style='color:#ff00ff; font-family:Orbitron; margin:0 0 15px 0;'> Friend Requests ({len(incoming)})</h3>
            </div>
        """, unsafe_allow_html=True)
        for req in incoming:
            sender = fetch_profile(req["sender_id"])
            if sender:
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.markdown(f"""
                        <div style='font-family:Rajdhani;'>
                            <strong style='color:#00f3ff; font-size:1.1rem;'>@{sender.get('username','')}</strong><br>
                            <span style='color:#aaa;'>{sender.get('full_name','')} �  {sender.get('city','')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button(" Accept", use_container_width=True, key=f"accept_{req['id']}"):
                        accept_friend_request(req["id"])
                        st.success("You are now friends!")
                        time.sleep(0.5)
                        st.rerun()
                with cols[2]:
                    if st.button(" Reject", use_container_width=True, key=f"reject_{req['id']}"):
                        reject_friend_request(req["id"])
                        st.rerun()
        st.divider()

    st.subheader("My Friends")
    friends = get_friends(me["user_id"])
    if not friends:
        st.info("No friends yet. Go to  Search to find people!")
    else:
        for f in friends:
            pic = f.get("profile_pic", "")
            pic_html = f"<img src='{pic}' style='width:50px; height:50px; border-radius:50%; border:2px solid #00f3ff; margin-right:10px; object-fit:cover;'>" if pic else ""
            with st.container():
                st.markdown(f"""
                    <div class='user-card'>
                        <div style='display:flex; align-items:center;'>
                            {pic_html}
                            <div>
                                <h3 style='margin:0; color:#00f3ff; font-family:Orbitron;'>@{f.get('username','')}</h3>
                                <p style='margin:4px 0 0 0; color:#ccc; font-family:Rajdhani;'>{f.get('full_name','')} �  {f.get('city','')}</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    if st.button(" Message", use_container_width=True, key=f"frmsg_{f['user_id']}"):
                        st.session_state.selected_chat_user = f
                        st.session_state.current_page = "Chats"
                        st.rerun()
                with cols[1]:
                    if st.button(" Profile", use_container_width=True, key=f"frview_{f['user_id']}"):
                        st.session_state.view_profile_user = f["user_id"]
                        st.session_state.current_page = "Profile"
                        st.rerun()

# =============================================================================
# AI STUDIO
# =============================================================================
def ai_module():
    st.markdown("""
        <div style='text-align:center; margin-bottom:30px;'>
            <h1 style='font-family:Orbitron;'> AI Studio</h1>
            <p style='color:#888; font-family:Rajdhani; font-size:1.1rem;'>Powered by Groq LLM</p>
        </div>
    """, unsafe_allow_html=True)

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader(" AI Chat")
        chat_box = st.container()
        with chat_box:
            if not st.session_state.ai_messages:
                st.markdown("""
                    <div style='text-align:center; padding:60px; color:#444; font-family:Rajdhani;'>
                        <p>Start a conversation with Devi AI</p>
                    </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.ai_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                        <div style='text-align:right; margin:12px 0;'>
                            <div style='background:linear-gradient(135deg,#00f3ff,#0066cc); color:#000; padding:12px 18px; border-radius:18px 18px 0 18px; display:inline-block; max-width:80%; text-align:left; font-family:Rajdhani; font-weight:600; font-size:1.05rem; box-shadow:0 4px 15px rgba(0,243,255,0.3);'>
                                {msg['content']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='text-align:left; margin:12px 0;'>
                            <div style='background:rgba(255,255,255,0.07); color:#e0e0e0; padding:12px 18px; border-radius:18px 18px 18px 0; display:inline-block; max-width:80%; border:1px solid rgba(0,243,255,0.3); font-family:Rajdhani; font-size:1.05rem;'>
                                {msg['content']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        with st.form("ai_form", clear_on_submit=True):
            prompt = st.text_input("Ask anything...", placeholder="How can I help you today?", key="ai_ask")
            cc = st.columns([4, 1])
            with cc[1]:
                submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and prompt.strip():
                st.session_state.ai_messages.append({"role": "user", "content": prompt.strip()})
                try:
                    groq_key = st.secrets.get("GROQ_API_KEY", "")
                    if not groq_key:
                        st.error("GROQ_API_KEY not found")
                    else:
                        client = Groq(api_key=groq_key)
                        msgs = [{"role": "system", "content": "You are Devi AI, a helpful assistant for Devi Social users. Be creative, concise, and friendly."}]
                        msgs += [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_messages]

                        with st.spinner("Thinking..."):
                            resp = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=msgs,
                                max_tokens=1024,
                                temperature=0.7
                            )
                            reply = resp.choices[0].message.content
                            st.session_state.ai_messages.append({"role": "assistant", "content": reply})
                            st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")
                    st.session_state.ai_messages.pop()

    with c2:
        st.subheader(" Caption Generator")
        st.markdown("""
            <div style='background:rgba(255,0,255,0.05); border:1px solid rgba(255,0,255,0.3); border-radius:12px; padding:18px; margin-bottom:20px;'>
                <p style='color:#ff00ff; font-family:Rajdhani; font-size:1rem;'>Generate engaging post captions instantly!</p>
            </div>
        """, unsafe_allow_html=True)

        topic = st.text_area("What's your post about?", placeholder="Describe your mood, photo, or topic...", height=80, key="cap_topic")
        tone = st.selectbox("Tone", ["Casual", "Professional", "Funny", "Inspirational", "Poetic", "Rebellious"], key="cap_tone")

        if st.button(" Generate Caption", use_container_width=True, key="btn_cap"):
            if topic.strip():
                try:
                    groq_key = st.secrets.get("GROQ_API_KEY", "")
                    if not groq_key:
                        st.error("GROQ_API_KEY missing")
                    else:
                        client = Groq(api_key=groq_key)
                        p = f"Generate a creative social media caption about: {topic}. Tone: {tone}. Under 80 words. Include relevant hashtags."
                        with st.spinner("Generating..."):
                            resp = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[{"role": "user", "content": p}],
                                max_tokens=256,
                                temperature=0.8
                            )
                            cap = resp.choices[0].message.content
                            st.markdown(f"""
                                <div style='background:rgba(0,243,255,0.05); border:1px solid #00f3ff; border-radius:12px; padding:18px; margin-top:15px;'>
                                    <p style='color:#00f3ff; font-family:Orbitron; font-weight:bold; margin-bottom:10px;'>Generated Caption:</p>
                                    <p style='color:#e0e0e0; font-family:Rajdhani; line-height:1.6; font-size:1.05rem;'>{cap}</p>
                                </div>
                            """, unsafe_allow_html=True)

                            if st.button(" Use in Feed", key="btn_use_cap"):
                                st.session_state["post_input"] = cap
                                st.session_state.current_page = "Feed"
                                st.success("Copied to Feed!")
                                time.sleep(0.5)
                                st.rerun()
                except Exception as e:
                    st.error(f"Generation failed: {e}")
            else:
                st.warning("Enter a topic")

# =============================================================================
# MAIN ROUTER
# =============================================================================
def main():
    render_sidebar()
    if not st.session_state.authenticated:
        auth_screen()
    else:
        page = st.session_state.get("current_page", "Feed")
        if page == "Feed":
            feed_module()
        elif page == "Search":
            search_module()
        elif page == "Chats":
            chat_module()
        elif page == "Friends":
            friends_module()
        elif page == "Profile":
            profile_module()
        elif page == "AI Studio":
            ai_module()

if __name__ == "__main__":
    main()
