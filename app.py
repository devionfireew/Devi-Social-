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
# FACEBOOK + WHATSAPP INSPIRED CSS
# ========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&display=swap');

* { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.stApp { background: #f0f2f5; color: #1c1e21; }

/* Top Navigation Bar */
.top-nav {
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.nav-logo { font-size: 1.5rem; font-weight: 700; color: #0a66c2; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { cursor: pointer; font-size: 1.2rem; }
.nav-icon:hover { opacity: 0.7; }

/* Profile Menu (Three Lines) */
.profile-menu-btn { cursor: pointer; font-size: 1.5rem; }
.profile-menu { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.profile-menu-item { padding: 10px 12px; cursor: pointer; border-radius: 6px; }
.profile-menu-item:hover { background: #f0f2f5; }

/* Chat Styling */
.chat-container { background: #fff; border-radius: 8px; border: 1px solid #e5e7eb; height: 600px; overflow-y: auto; padding: 16px; }
.chat-bubble-user { background: #0a66c2; color: #fff; padding: 10px 14px; border-radius: 18px 18px 2px 18px; margin: 6px 0; max-width: 70%; float: right; clear: both; word-wrap: break-word; }
.chat-bubble-other { background: #e4e6eb; color: #1c1e21; padding: 10px 14px; border-radius: 18px 18px 18px 2px; margin: 6px 0; max-width: 70%; float: left; clear: both; word-wrap: break-word; }
.chat-image { max-width: 200px; border-radius: 12px; margin: 6px 0; }

/* WhatsApp Call Screen */
.call-screen { background: linear-gradient(135deg, #0a66c2 0%, #0854a0 100%); color: #fff; border-radius: 16px; padding: 40px; text-align: center; min-height: 500px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.call-user-pic { width: 150px; height: 150px; border-radius: 50%; margin-bottom: 20px; border: 4px solid #fff; object-fit: cover; }
.call-user-name { font-size: 2rem; font-weight: 700; margin-bottom: 10px; }
.call-status { font-size: 1.1rem; opacity: 0.9; margin-bottom: 30px; }
.call-buttons { display: flex; gap: 20px; justify-content: center; margin-top: 30px; }
.call-btn { padding: 15px 30px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; border: none; }
.call-accept { background: #31a24c; color: #fff; }
.call-reject { background: #f02849; color: #fff; }

/* Post Card */
.post-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.post-actions { display: flex; gap: 10px; margin-top: 12px; }
.post-action-btn { flex: 1; padding: 8px; border: none; background: #f0f2f5; border-radius: 6px; cursor: pointer; font-weight: 500; }
.post-action-btn:hover { background: #e4e6eb; }

/* Friend List */
.friend-item { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; }
.friend-pic { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; }

/* Notification Badge */
.notification-badge { background: #f02849; color: #fff; border-radius: 50%; padding: 2px 6px; font-size: 0.75rem; font-weight: 600; }

/* Three Line Menu */
.three-line-menu { background: #fff; border-radius: 8px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.menu-item { padding: 10px 12px; cursor: pointer; border-radius: 6px; }
.menu-item:hover { background: #f0f2f5; }

</style>
""", unsafe_allow_html=True)

# ========================================
# SESSION STATE
# ========================================
def init_session_state():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if "user" not in st.session_state: st.session_state.user = None
    if "page" not in st.session_state: st.session_state.page = "Home"
    if "chat_user" not in st.session_state: st.session_state.chat_user = None
    if "view_user" not in st.session_state: st.session_state.view_user = None
    if "ai_msgs" not in st.session_state: st.session_state.ai_msgs = []
    if "edit_post" not in st.session_state: st.session_state.edit_post = None
    if "calling" not in st.session_state: st.session_state.calling = False
    if "call_user" not in st.session_state: st.session_state.call_user = None
    if "show_profile_menu" not in st.session_state: st.session_state.show_profile_menu = False

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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; font-size:3rem; color:#0a66c2;'>🔮 Devi Social</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#65676b; font-size:1.1rem;'>Connect. Share. Grow.</p>", unsafe_allow_html=True)
        
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
    st.stop()

# ========================================
# MAIN APP
# ========================================
me = st.session_state.user
page = st.session_state.page

# ========================================
# TOP NAVIGATION BAR (Facebook Style)
# ========================================
st.markdown("<div class='top-nav'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown("<div class='nav-logo'>🔮 Devi</div>", unsafe_allow_html=True)

with col2:
    nav_cols = st.columns(5)
    if nav_cols[0].button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    if nav_cols[1].button("👤 Profile", use_container_width=True):
        st.session_state.page = "Profile"
        st.session_state.view_user = me["user_id"]
        st.rerun()
    if nav_cols[2].button("👥 Requests", use_container_width=True):
        st.session_state.page = "Requests"
        st.rerun()
    
    notifs = get_notifications(me["user_id"]) if db else []
    unread = len([n for n in notifs if not n.get("read", False)])
    badge = f" ({unread})" if unread > 0 else ""
    if nav_cols[3].button(f"🔔 Notifs{badge}", use_container_width=True):
        st.session_state.page = "Notifications"
        st.rerun()
    
    if nav_cols[4].button("🎥 Video", use_container_width=True):
        st.session_state.page = "Video"
        st.rerun()

with col3:
    if st.button("☰"):
        st.session_state.show_profile_menu = not st.session_state.show_profile_menu
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Profile Menu (Three Lines)
if st.session_state.show_profile_menu:
    st.markdown("<div class='three-line-menu'>", unsafe_allow_html=True)
    if st.button("⚙️ Edit Profile", use_container_width=True):
        st.session_state.page = "EditProfile"
        st.session_state.show_profile_menu = False
        st.rerun()
    if st.button("💬 Messages", use_container_width=True):
        st.session_state.page = "Chats"
        st.session_state.show_profile_menu = False
        st.rerun()
    if st.button("👫 Friends", use_container_width=True):
        st.session_state.page = "Friends"
        st.session_state.show_profile_menu = False
        st.rerun()
    if st.button("🤖 AI Studio", use_container_width=True):
        st.session_state.page = "AI"
        st.session_state.show_profile_menu = False
        st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ========================================
# HOME PAGE (Feed)
# ========================================
if page == "Home":
    st.markdown("<h2>📰 Home Feed</h2>", unsafe_allow_html=True)
    
    # Create Post
    st.markdown("<div class='post-card'>", unsafe_allow_html=True)
    st.subheader("✨ What's on your mind?")
    post_text = st.text_area("", placeholder="Share your thoughts...", height=80, label_visibility="collapsed", key="post_text")
    privacy = st.selectbox("Privacy", ["Public", "Friends Only", "Private"], key="privacy_select")
    
    friends = get_my_friends(me["user_id"])
    if friends:
        mention_opts = [f"@{f['username']}" for f in friends if f]
        if mention_opts:
            selected = st.multiselect("🏷️ Mention Friends", mention_opts, key="mention_select")
            if selected: post_text += " " + " ".join(selected)
    
    c1, c2 = st.columns(2)
    img_file = c1.file_uploader("🖼️ Upload Image", type=["jpg", "jpeg", "png", "gif"], key="img_upload")
    vid_file = c2.file_uploader("🎥 Upload Video", type=["mp4", "mov", "avi"], key="vid_upload")
    
    if st.button("🚀 Publish", use_container_width=True):
        img_data = file_to_base64(img_file)
        vid_data = file_to_base64(vid_file)
        if post_text.strip() or img_data or vid_data:
            mentions = re.findall(r'@(\w+)', post_text)
            if db:
                db.collection("posts").add({
                    "author_id": me["user_id"], "author_name": me["full_name"], "author_username": me["username"],
                    "author_city": me.get("city", ""), "author_pic": me.get("profile_pic", ""),
                    "content": post_text.strip(), "image": img_data, "video": vid_data,
                    "mentions": mentions, "privacy": privacy,
                    "timestamp": datetime.now().isoformat(), "likes": 0, "liked_by": [], "shares": 0
                })
                for m in mentions:
                    for f in friends:
                        if f and f.get("username") == m:
                            add_notification(f["user_id"], f"@{me['username']} mentioned you in a post!", "mention")
            st.success("Posted!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Add some content to post")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Show Posts
    if db:
        try:
            all_posts = list(db.collection("posts").limit(100).stream())
            filtered_posts = []
            for p in all_posts:
                d = p.to_dict()
                pid = p.id
                if d.get("privacy") == "Public":
                    filtered_posts.append((pid, d))
                elif d.get("privacy") == "Friends Only":
                    if d["author_id"] == me["user_id"] or get_friend_status(me["user_id"], d["author_id"]) == "friends":
                        filtered_posts.append((pid, d))
                elif d.get("privacy") == "Private" and d["author_id"] == me["user_id"]:
                    filtered_posts.append((pid, d))
            
            filtered_posts.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)
            
            for pid, p in filtered_posts[:50]:
                ts = ""
                if p.get("timestamp"):
                    try: ts = parser.parse(p["timestamp"]).strftime("%b %d, %Y · %I:%M %p")
                    except: ts = p["timestamp"][:16]
                
                st.markdown("<div class='post-card'>", unsafe_allow_html=True)
                
                # Post Header
                cols = st.columns([0.1, 0.7, 0.2])
                with cols[0]:
                    if p.get("author_pic"): st.image(p["author_pic"], width=40)
                    else: st.markdown("👤")
                
                with cols[1]:
                    if st.button(f"**{p['author_name']}** @{p['author_username']}", key=f"author_{pid}"):
                        st.session_state.view_user = p["author_id"]
                        st.session_state.page = "Profile"
                        st.rerun()
                    st.caption(f"📍 {p.get('author_city', '')} · {ts}")
                
                with cols[2]:
                    if p.get("author_id") == me["user_id"]:
                        if st.button("✏️", key=f"edit_{pid}"): st.session_state.edit_post = pid; st.rerun()
                        if st.button("🗑️", key=f"del_{pid}"):
                            db.collection("posts").document(pid).delete()
                            st.success("Deleted!")
                            time.sleep(1)
                            st.rerun()
                
                # Post Content
                content = p.get("content", "")
                for mention in p.get("mentions", []): content = content.replace(f"@{mention}", f"<span style='color:#0a66c2; font-weight:600;'>@{mention}</span>")
                if content: st.markdown(f"<p style='font-size:1rem; line-height:1.5;'>{content}</p>", unsafe_allow_html=True)
                if p.get("image"): st.image(p["image"], use_container_width=True)
                if p.get("video"): st.video(p["video"])
                
                # Post Actions
                liked = me["user_id"] in p.get("liked_by", [])
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.button(f"{'❤️' if liked else '🤍'} {p.get('likes', 0)}", key=f"like_{pid}"):
                        ref = db.collection("posts").document(pid)
                        if liked:
                            ref.update({"likes": firestore.Increment(-1), "liked_by": firestore.ArrayRemove([me["user_id"]])})
                        else:
                            ref.update({"likes": firestore.Increment(1), "liked_by": firestore.ArrayUnion([me["user_id"]])})
                        st.rerun()
                with c2:
                    comment_count = len(list(db.collection("posts").document(pid).collection("comments").stream()))
                    st.button(f"💬 {comment_count}", key=f"com_count_{pid}")
                with c3:
                    st.button(f"🔗 Share", key=f"share_count_{pid}")
                
                # Comments
                with st.expander("💬 Comments"):
                    for c in db.collection("posts").document(pid).collection("comments").stream():
                        cd = c.to_dict()
                        cid = c.id
                        st.markdown(f"**{cd['author_name']}**: {cd['text']}")
                        
                        for r in db.collection("posts").document(pid).collection("comments").document(cid).collection("replies").stream():
                            rd = r.to_dict()
                            st.markdown(f"  └ **{rd['author_name']}**: {rd['text']}")
                        
                        with st.form(f"reply_{cid}", clear_on_submit=True):
                            reply_text = st.text_input("Reply...", key=f"reply_in_{cid}")
                            if st.form_submit_button("Reply") and reply_text.strip():
                                db.collection("posts").document(pid).collection("comments").document(cid).collection("replies").add({
                                    "author_id": me["user_id"], "author_name": me["full_name"], "author_pic": me.get("profile_pic", ""),
                                    "text": reply_text.strip(), "timestamp": datetime.now().isoformat()
                                })
                                st.rerun()
                    
                    with st.form(f"com_{pid}", clear_on_submit=True):
                        com = st.text_input("Write a comment...", key=f"com_in_{pid}")
                        if st.form_submit_button("Post") and com.strip():
                            db.collection("posts").document(pid).collection("comments").add({
                                "author_id": me["user_id"], "author_name": me["full_name"], "author_pic": me.get("profile_pic", ""),
                                "text": com.strip(), "timestamp": datetime.now().isoformat()
                            })
                            if p["author_id"] != me["user_id"]:
                                add_notification(p["author_id"], f"@{me['username']} commented on your post!", "comment")
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()
        except Exception as e:
            st.error(f"Error loading posts: {str(e)}")

# ========================================
# CHATS PAGE (WhatsApp Style)
# ========================================
elif page == "Chats":
    st.markdown("<h2>💬 Messages</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.2, 2])
    
    with c1:
        st.markdown("<h3>Chats</h3>", unsafe_allow_html=True)
        search = st.text_input("Search...", placeholder="Find a friend", key="chat_search")
        
        friends = get_my_friends(me["user_id"])
        if friends:
            for f in friends:
                if not f: continue
                if st.button(f"👤 @{f['username']}", key=f"chatf_{f['user_id']}", use_container_width=True):
                    st.session_state.chat_user = f
                    st.rerun()
    
    with c2:
        if not st.session_state.chat_user:
            st.markdown("<div style='text-align:center; padding:40px; color:#65676b;'><p style='font-size:1.2rem;'>💬 Select a contact to start messaging</p></div>", unsafe_allow_html=True)
        else:
            other = st.session_state.chat_user
            
            # Chat Header
            header_cols = st.columns([0.1, 0.6, 0.3])
            with header_cols[0]:
                if other.get("profile_pic"): st.image(other["profile_pic"], width=40)
                else: st.markdown("👤")
            with header_cols[1]:
                st.markdown(f"<h3 style='margin:0;'>@{other['username']}</h3><p style='margin:0; color:#65676b; font-size:0.9rem;'>{other.get('full_name','')}</p>", unsafe_allow_html=True)
            with header_cols[2]:
                if st.button("📞 Call", key=f"call_{other['user_id']}"):
                    st.session_state.calling = True
                    st.session_state.call_user = other
                    st.rerun()
            
            st.divider()
            
            # Messages
            if db:
                try:
                    m1 = [{**m.to_dict(), "me": True} for m in db.collection("messages").where("sender_id","==",me["user_id"]).where("receiver_id","==",other["user_id"]).stream()]
                    m2 = [{**m.to_dict(), "me": False} for m in db.collection("messages").where("sender_id","==",other["user_id"]).where("receiver_id","==",me["user_id"]).stream()]
                    msgs = sorted(m1 + m2, key=lambda x: x.get("timestamp",""))
                    
                    with st.container():
                        if not msgs:
                            st.markdown("<p style='text-align:center; color:#65676b; padding:40px;'>No messages yet. Say hello! 👋</p>", unsafe_allow_html=True)
                        else:
                            for m in msgs:
                                is_me = m.get("me", False)
                                cls = "chat-bubble-user" if is_me else "chat-bubble-other"
                                align = "right" if is_me else "left"
                                tm = m.get("timestamp", "")[11:16]
                                
                                if m.get("message_type") == "image":
                                    st.markdown(f"<div style='text-align:{align};'><img src='{m['message_body']}' class='chat-image'></div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div style='text-align:{align};'><div class='{cls}'>{m['message_body']}</div><div style='font-size:0.7rem; color:#999; text-align:{align};'>{tm}</div></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error loading messages: {str(e)}")
            
            st.divider()
            
            # Message Input
            with st.form("msg_form", clear_on_submit=True):
                cols = st.columns([3, 1, 1])
                txt = cols[0].text_input("Message...", label_visibility="collapsed", placeholder="Type a message...")
                img_msg = cols[1].file_uploader("📷", type=["jpg", "jpeg", "png"], key="msg_img")
                
                if cols[2].form_submit_button("📤"):
                    if txt.strip() and db:
                        db.collection("messages").add({
                            "sender_id": me["user_id"], "receiver_id": other["user_id"],
                            "message_body": txt.strip(), "message_type": "text", "timestamp": datetime.now().isoformat()
                        })
                        add_notification(other["user_id"], f"New message from @{me['username']}!", "message")
                        st.rerun()
                    elif img_msg and db:
                        img_data = file_to_base64(img_msg)
                        db.collection("messages").add({
                            "sender_id": me["user_id"], "receiver_id": other["user_id"],
                            "message_body": img_data, "message_type": "image", "timestamp": datetime.now().isoformat()
                        })
                        add_notification(other["user_id"], f"New image from @{me['username']}!", "message")
                        st.rerun()

# ========================================
# CALLING SCREEN (WhatsApp Style)
# ========================================
if st.session_state.calling and st.session_state.call_user:
    call_user = st.session_state.call_user
    st.markdown("<div class='call-screen'>", unsafe_allow_html=True)
    
    if call_user.get("profile_pic"):
        st.image(call_user["profile_pic"], width=150)
    else:
        st.markdown("<div style='width:150px; height:150px; border-radius:50%; background:#e5e7eb; margin:auto; margin-bottom:20px;'></div>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 class='call-user-name'>@{call_user['username']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='call-status'>Calling...</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        pass
    with col2:
        if st.button("✅ Accept Call", use_container_width=True):
            st.success(f"Call connected with @{call_user['username']}!")
            time.sleep(2)
            st.session_state.calling = False
            st.rerun()
    with col3:
        pass
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        pass
    with col2:
        if st.button("❌ Reject Call", use_container_width=True):
            st.session_state.calling = False
            st.rerun()
    with col3:
        pass
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ========================================
# PROFILE PAGE
# ========================================
elif page == "Profile":
    uid = st.session_state.get("view_user") or me["user_id"]
    prof = get_profile(uid)
    is_me = uid == me["user_id"]
    
    if not prof:
        st.error("Profile not found")
        st.stop()
    
    cover = prof.get("cover_pic", "")
    if cover:
        st.image(cover, use_container_width=True)
    else:
        st.markdown("<div style='height:200px; background:linear-gradient(135deg,#0a66c2,#0854a0); border-radius:8px;'></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        pic = prof.get("profile_pic", "")
        if pic:
            st.image(pic, width=120)
        else:
            st.markdown("<div style='width:120px;height:120px;border-radius:50%;background:#e5e7eb;display:flex;align-items:center;justify-content:center;font-size:3rem;margin:auto;'>👤</div>", unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"<h1>{prof['full_name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3>@{prof['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"📍 {prof.get('city','')} · 🎂 {prof.get('birthday','')}")
        st.markdown(f"📝 {prof.get('bio','')}")
        friends_count = len(list(db.collection("friends").where("users", "array_contains", uid).stream())) if db else 0
        st.markdown(f"<p style='font-weight:600;'><strong>{friends_count}</strong> Friends</p>", unsafe_allow_html=True)
    
    with c3:
        if is_me:
            if st.button("⚙️ Edit Profile"):
                st.session_state.page = "EditProfile"
                st.rerun()
        else:
            status = get_friend_status(me["user_id"], uid)
            if status == "none":
                if st.button("➕ Add Friend"):
                    send_friend_req(me["user_id"], uid)
                    add_notification(uid, f"@{me['username']} sent you a friend request!", "friend_request")
                    st.success("Request sent!")
                    time.sleep(1)
                    st.rerun()
            elif status == "friends":
                st.markdown("<p style='color:#31a24c;'>✨ Friends</p>", unsafe_allow_html=True)
                if st.button("💬 Message"):
                    st.session_state.chat_user = prof
                    st.session_state.page = "Chats"
                    st.rerun()
    
    st.divider()
    st.markdown("<h3>Posts</h3>", unsafe_allow_html=True)
    
    if db:
        try:
            user_posts = list(db.collection("posts").where("author_id", "==", uid).limit(50).stream())
            user_posts.sort(key=lambda x: x.to_dict().get("timestamp", ""), reverse=True)
            if not user_posts:
                st.info("No posts yet")
            for post in user_posts:
                p = post.to_dict()
                st.markdown("<div class='post-card'>", unsafe_allow_html=True)
                st.markdown(f"<p>{p.get('content','')}</p>", unsafe_allow_html=True)
                if p.get("image"): st.image(p["image"], use_container_width=True)
                if p.get("video"): st.video(p["video"])
                st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading posts: {str(e)}")

# ========================================
# EDIT PROFILE PAGE
# ========================================
elif page == "EditProfile":
    st.markdown("<h2>⚙️ Edit Profile</h2>", unsafe_allow_html=True)
    prof = get_profile(me["user_id"])
    
    with st.form("edit_profile"):
        new_name = st.text_input("Display Name", value=prof.get("full_name", ""))
        new_bio = st.text_area("Bio", value=prof.get("bio", ""))
        new_city = st.text_input("City", value=prof.get("city", ""))
        prof_file = st.file_uploader("New Profile Pic", type=["jpg", "jpeg", "png"])
        cover_file = st.file_uploader("New Cover Pic", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Save Changes"):
            updates = {"full_name": new_name, "bio": new_bio, "city": new_city}
            if prof_file: updates["profile_pic"] = file_to_base64(prof_file)
            if cover_file: updates["cover_pic"] = file_to_base64(cover_file)
            if db: db.collection("users").document(me["user_id"]).update(updates)
            st.session_state.user = get_profile(me["user_id"])
            st.success("✅ Profile updated!")
            time.sleep(1)
            st.session_state.page = "Profile"
            st.rerun()

# ========================================
# FRIEND REQUESTS PAGE
# ========================================
elif page == "Requests":
    st.markdown("<h2>👥 Friend Requests</h2>", unsafe_allow_html=True)
    incoming = get_incoming_reqs(me["user_id"])
    if not incoming:
        st.info("No friend requests")
    for req in incoming:
        sender = get_profile(req["sender_id"])
        if sender:
            st.markdown("<div class='friend-item'>", unsafe_allow_html=True)
            cols = st.columns([1, 3, 1, 1])
            if sender.get("profile_pic"):
                cols[0].image(sender["profile_pic"], width=50)
            else:
                cols[0].markdown("👤")
            cols[1].markdown(f"**@{sender['username']}**<br>{sender['full_name']}", unsafe_allow_html=True)
            if cols[2].button("✅", key=f"acc_{req['id']}"):
                accept_friend_req(req["id"])
                add_notification(req["sender_id"], f"@{me['username']} accepted your friend request!", "friend_accept")
                st.success("Friend added!")
                time.sleep(1)
                st.rerun()
            if cols[3].button("❌", key=f"rej_{req['id']}"):
                if db: db.collection("friend_requests").document(req["id"]).delete()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# NOTIFICATIONS PAGE
# ========================================
elif page == "Notifications":
    st.markdown("<h2>🔔 Notifications</h2>", unsafe_allow_html=True)
    notifs = get_notifications(me["user_id"])
    if not notifs:
        st.info("No notifications")
    for n in notifs:
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            bg = "#e7f3ff" if not n.get("read") else "transparent"
            st.markdown(f"<div style='background:{bg};padding:15px;border-radius:8px;border:1px solid #e5e7eb;margin-bottom:10px;'><p>{n['text']}</p><small style='color:#65676b;'>{n.get('timestamp','')[:16]}</small></div>", unsafe_allow_html=True)
        with col2:
            if not n.get("read") and st.button("✓", key=f"read_{n['id']}"):
                if db: db.collection("notifications").document(n["id"]).update({"read": True})
                st.rerun()

# ========================================
# FRIENDS PAGE
# ========================================
elif page == "Friends":
    st.markdown("<h2>👥 My Friends</h2>", unsafe_allow_html=True)
    friends = get_my_friends(me["user_id"])
    if not friends:
        st.info("No friends yet. Go to Profile to find people!")
    else:
        for f in friends:
            if not f: continue
            st.markdown("<div class='friend-item'>", unsafe_allow_html=True)
            cols = st.columns([1, 2, 1])
            if f.get("profile_pic"):
                cols[0].image(f["profile_pic"], width=50)
            else:
                cols[0].markdown("👤")
            cols[1].markdown(f"**@{f['username']}**<br>{f['full_name']}", unsafe_allow_html=True)
            if cols[2].button("💬", key=f"fchat_{f['user_id']}"):
                st.session_state.chat_user = f
                st.session_state.page = "Chats"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# VIDEO PAGE
# ========================================
elif page == "Video":
    st.markdown("<h2>🎥 Videos</h2>", unsafe_allow_html=True)
    st.info("Video feature coming soon!")

# ========================================
# AI STUDIO
# ========================================
elif page == "AI":
    st.markdown("<h2>🤖 AI Studio</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("<h3>Chat with Devi AI</h3>", unsafe_allow_html=True)
        for msg in st.session_state.ai_msgs:
            is_user = msg["role"] == "user"
            cls = "chat-bubble-user" if is_user else "chat-bubble-other"
            align = "right" if is_user else "left"
            st.markdown(f"<div style='text-align:{align};'><div class='{cls}'>{msg['content']}</div></div>", unsafe_allow_html=True)
        
        with st.form("ai_chat", clear_on_submit=True):
            p = st.text_input("Ask anything...", placeholder="Type your question")
            if st.form_submit_button("Send") and p.strip():
                st.session_state.ai_msgs.append({"role": "user", "content": p})
                try:
                    client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
                    resp = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "system", "content": "You are Devi AI, a helpful assistant."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_msgs],
                        max_tokens=1024
                    )
                    st.session_state.ai_msgs.append({"role": "assistant", "content": resp.choices[0].message.content})
                except Exception as e:
                    st.error(str(e))
                st.rerun()
