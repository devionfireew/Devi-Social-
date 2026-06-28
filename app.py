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

st.set_page_config(page_title="Devi Social", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
.stApp { background: linear-gradient(135deg, #050510 0%, #0a0a1a 50%, #0d1b2a 100%); color: #e0e0e0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #08081a 0%, #0f0f2d 100%) !important; border-right: 1px solid rgba(0, 243, 255, 0.3); }
h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.4); }
.stButton > button { background: linear-gradient(90deg, #00f3ff, #0066cc) !important; color: #000 !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 700 !important; border: none !important; border-radius: 8px !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(0, 243, 255, 0.05) !important; border: 1px solid rgba(0, 243, 255, 0.4) !important; color: #fff !important; border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important; }
.post-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 243, 255, 0.2); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
.profile-header { background: linear-gradient(135deg, rgba(0, 243, 255, 0.1), rgba(255, 0, 255, 0.1)); border: 1px solid rgba(0, 243, 255, 0.3); border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 30px; }
.chat-bubble-user { background: linear-gradient(135deg, #00f3ff, #0066cc); color: #000; padding: 10px 16px; border-radius: 18px 18px 0 18px; margin: 6px 0; max-width: 70%; float: right; clear: both; font-weight: 600; font-family: 'Rajdhani', sans-serif; }
.chat-bubble-other { background: rgba(255, 255, 255, 0.08); color: #e0e0e0; padding: 10px 16px; border-radius: 18px 18px 18px 0; margin: 6px 0; max-width: 70%; float: left; clear: both; border: 1px solid rgba(0, 243, 255, 0.3); font-family: 'Rajdhani', sans-serif; }
.comment-box { background: rgba(255, 255, 255, 0.02); border-left: 3px solid #00f3ff; padding: 8px 12px; margin: 6px 0; border-radius: 0 8px 8px 0; }
.contact-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 243, 255, 0.15); border-radius: 12px; padding: 12px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# Firebase
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

# Session
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "Feed"
if "chat_user" not in st.session_state: st.session_state.chat_user = None
if "view_user" not in st.session_state: st.session_state.view_user = None
if "ai_msgs" not in st.session_state: st.session_state.ai_msgs = []

# Auth
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
    d = db.collection("users").document(uid).get()
    return d.to_dict() if d.exists else None

def save_profile(uid, data):
    if not db: return False
    db.collection("users").document(uid).set(data)
    return True

# Friends
def get_friend_status(me_id, other_id):
    if not db or me_id == other_id: return "self"
    fid = f"{min(me_id, other_id)}_{max(me_id, other_id)}"
    if db.collection("friends").document(fid).get().exists: return "friends"
    for r in db.collection("friend_requests").where("receiver_id", "==", me_id).get():
        if r.to_dict().get("sender_id") == other_id and r.to_dict().get("status") == "pending": return "pending_in"
    for r in db.collection("friend_requests").where("sender_id", "==", me_id).get():
        if r.to_dict().get("receiver_id") == other_id and r.to_dict().get("status") == "pending": return "pending_out"
    return "none"

def send_friend_req(sender, receiver):
    db.collection("friend_requests").add({"sender_id": sender, "receiver_id": receiver, "status": "pending", "time": datetime.now().isoformat()})

def accept_friend_req(rid):
    r = db.collection("friend_requests").document(rid).get().to_dict()
    db.collection("friend_requests").document(rid).update({"status": "accepted"})
    fid = f"{min(r['sender_id'], r['receiver_id'])}_{max(r['sender_id'], r['receiver_id'])}"
    db.collection("friends").document(fid).set({"users": [r["sender_id"], r["receiver_id"]], "time": datetime.now().isoformat()})

def get_my_friends(uid):
    if not db: return []
    result = []
    for d in db.collection("friends").where("users", "array_contains", uid).get():
        data = d.to_dict()
        other = data["users"][0] if data["users"][1] == uid else data["users"][1]
        p = get_profile(other)
        if p: result.append(p)
    return result

def get_incoming_reqs(uid):
    return [{**r.to_dict(), "id": r.id} for r in db.collection("friend_requests").where("receiver_id", "==", uid).get() if r.to_dict().get("status") == "pending"]

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align:center; font-size:2rem;'>🔮 Devi Social</h1>", unsafe_allow_html=True)
    if st.session_state.authenticated and st.session_state.user:
        u = st.session_state.user
        st.markdown(f"<p style='text-align:center; color:#00f3ff;'>@{u['username']}</p>", unsafe_allow_html=True)
        for label, page in [("📰 Feed", "Feed"), ("🔍 Search", "Search"), ("💬 Chats", "Chats"), ("👥 Friends", "Friends"), ("👤 Profile", "Profile"), ("🤖 AI Studio", "AI")]:
            if st.button(label, use_container_width=True):
                st.session_state.page = page
                st.session_state.view_user = None
                st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

# Auth Screen
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; font-size:3rem;'>🔮 Devi Social</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab1:
            with st.form("login"):
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    res = firebase_auth("signInWithPassword", em, pw)
                    if res["ok"]:
                        prof = get_profile(res["uid"])
                        if prof:
                            st.session_state.authenticated = True
                            st.session_state.user = prof
                            st.rerun()
                        else: st.error("Profile not found")
                    else: st.error(res["err"])
        with tab2:
            with st.form("signup"):
                fn = st.text_input("Full Name")
                un = st.text_input("Username")
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                bd = st.date_input("Birthday", value=date(2000,1,1), max_value=date.today())
                ct = st.text_input("City")
                bio = st.text_area("Bio")
                cpw = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account"):
                    if not all([fn, un, em, pw, ct, bio]): st.error("All fields required")
                    elif pw != cpw: st.error("Passwords don't match")
                    elif len(pw) < 6: st.error("Password too short")
                    else:
                        if db and list(db.collection("users").where("username", "==", un).limit(1).get()):
                            st.error("Username taken"); st.stop()
                        res = firebase_auth("signUp", em, pw)
                        if res["ok"]:
                            data = {"user_id": res["uid"], "email": em, "username": un, "full_name": fn, "birthday": bd.isoformat(), "city": ct, "bio": bio, "profile_pic": "", "cover_pic": "", "created_at": datetime.now().isoformat()}
                            if save_profile(res["uid"], data):
                                st.session_state.authenticated = True
                                st.session_state.user = data
                                st.rerun()
                            else: st.error("Failed to save")
                        else: st.error(res["err"])
    st.stop()

# Main App
me = st.session_state.user
page = st.session_state.page

# FEED
if page == "Feed":
    st.markdown("<h1 style='text-align:center;'>📰 Social Feed</h1>", unsafe_allow_html=True)
    with st.container():
        st.subheader("✨ Create Post")
        post_text = st.text_area("What's on your mind?", height=80, key="post_text")
        c1, c2 = st.columns(2)
        img_url = c1.text_input("🖼️ Image URL (optional)", placeholder="https://i.imgur.com/xxx.jpg")
        vid_url = c2.text_input("🎥 Video URL (optional)", placeholder="YouTube link...")
        if st.button("🚀 Publish"):
            if post_text.strip() or img_url or vid_url:
                db.collection("posts").add({"author_id": me["user_id"], "author_name": me["full_name"], "author_username": me["username"], "author_city": me.get("city", ""), "author_pic": me.get("profile_pic", ""), "content": post_text.strip(), "image": img_url, "video": vid_url, "timestamp": datetime.now().isoformat(), "likes": 0, "liked_by": []})
                st.success("Posted!"); st.rerun()
            else: st.warning("Add some content")
    st.divider()
    
    # Get all posts and sort in Python (no index needed)
    all_posts = list(db.collection("posts").limit(100).get())
    all_posts.sort(key=lambda x: x.to_dict().get("timestamp", ""), reverse=True)
    
    for post in all_posts[:50]:
        p = post.to_dict(); pid = post.id
        ts = ""
        if p.get("timestamp"):
            try: ts = parser.parse(p["timestamp"]).strftime("%b %d · %I:%M %p")
            except: ts = p["timestamp"][:16]
        cols = st.columns([0.1, 0.9])
        with cols[0]:
            if p.get("author_pic"): st.image(p["author_pic"], width=40)
            else: st.markdown("👤")
        with cols[1]:
            if st.button(f"**{p['author_name']}**  @{p['author_username']}", key=f"author_{pid}"):
                st.session_state.view_user = p["author_id"]
                st.session_state.page = "Profile"
                st.rerun()
            st.caption(f"📍 {p.get('author_city', '')} · {ts}")
        if p.get("content"): st.markdown(f"<p style='font-size:1.1rem;'>{p['content']}</p>", unsafe_allow_html=True)
        if p.get("image"): st.image(p["image"], use_container_width=True)
        if p.get("video"): st.video(p["video"])
        liked = me["user_id"] in p.get("liked_by", [])
        if st.button(f"{'❤️' if liked else '🤍'} {p.get('likes', 0)}", key=f"like_{pid}"):
            ref = db.collection("posts").document(pid)
            if liked: ref.update({"likes": firestore.Increment(-1), "liked_by": firestore.ArrayRemove([me["user_id"]])})
            else: ref.update({"likes": firestore.Increment(1), "liked_by": firestore.ArrayUnion([me["user_id"]])})
            st.rerun()
        with st.expander("💬 Comments"):
            for c in db.collection("posts").document(pid).collection("comments").get():
                cd = c.to_dict()
                st.markdown(f"<div class='comment-box'><b>{cd['author_name']}</b>: {cd['text']}</div>", unsafe_allow_html=True)
            with st.form(f"com_{pid}", clear_on_submit=True):
                com = st.text_input("Write a comment...", key=f"com_in_{pid}")
                if st.form_submit_button("Post") and com.strip():
                    db.collection("posts").document(pid).collection("comments").add({"author_id": me["user_id"], "author_name": me["full_name"], "text": com.strip(), "timestamp": datetime.now().isoformat()})
                    st.rerun()
        st.markdown("---")

# SEARCH
elif page == "Search":
    st.markdown("<h1 style='text-align:center;'>🔍 Search</h1>", unsafe_allow_html=True)
    q = st.text_input("Search users by name, username, or city...")
    if q:
        for u in db.collection("users").limit(100).get():
            d = u.to_dict()
            if d["user_id"] == me["user_id"]: continue
            if q.lower() in d.get("username","").lower() or q.lower() in d.get("full_name","").lower() or q.lower() in d.get("city","").lower():
                cols = st.columns([1, 3])
                with cols[0]:
                    if d.get("profile_pic"): st.image(d["profile_pic"], width=60)
                    else: st.markdown("👤")
                with cols[1]:
                    st.markdown(f"<h3>@{d['username']}</h3><p>{d['full_name']} · {d['city']}</p>", unsafe_allow_html=True)
                    status = get_friend_status(me["user_id"], d["user_id"])
                    c1, c2 = st.columns(2)
                    if status == "none":
                        if c1.button("➕ Add Friend", key=f"add_{d['user_id']}"):
                            send_friend_req(me["user_id"], d["user_id"])
                            st.success("Request sent!"); time.sleep(1); st.rerun()
                    elif status == "friends": c1.markdown("<p style='color:#00ff7f;'>✨ Friends</p>", unsafe_allow_html=True)
                    elif status == "pending_in": c1.markdown("<p style='color:#ffa500;'>⏳ They sent request</p>", unsafe_allow_html=True)
                    elif status == "pending_out": c1.markdown("<p style='color:#ffa500;'>⏳ Request sent</p>", unsafe_allow_html=True)
                    if c2.button("👤 View Profile", key=f"view_{d['user_id']}"):
                        st.session_state.view_user = d["user_id"]
                        st.session_state.page = "Profile"
                        st.rerun()

# CHATS
elif page == "Chats":
    st.markdown("<h1 style='text-align:center;'>💬 Devi Messenger</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Chats")
        search = st.text_input("Search...")
        friends = get_my_friends(me["user_id"])
        if friends:
            st.markdown("<p style='color:#00ff7f;'>Friends</p>", unsafe_allow_html=True)
            for f in friends:
                if not f: continue
                cols = st.columns([0.3, 0.7])
                with cols[0]:
                    if f.get("profile_pic"): st.image(f["profile_pic"], width=40)
                    else: st.markdown("👤")
                with cols[1]:
                    if st.button(f"@{f['username']}", key=f"chatf_{f['user_id']}", use_container_width=True):
                        st.session_state.chat_user = f
                        st.rerun()
        if search:
            st.markdown("<p style='color:#888;'>All Users</p>", unsafe_allow_html=True)
            for u in db.collection("users").limit(100).get():
                d = u.to_dict()
                if d["user_id"] == me["user_id"]: continue
                if search.lower() in d.get("username","").lower():
                    if st.button(f"@{d['username']}", key=f"chatu_{d['user_id']}", use_container_width=True):
                        st.session_state.chat_user = d
                        st.rerun()
    with c2:
        if not st.session_state.chat_user:
            st.info("Select a contact to start messaging")
        else:
            other = st.session_state.chat_user
            header_cols = st.columns([0.1, 0.9])
            with header_cols[0]:
                if other.get("profile_pic"): st.image(other["profile_pic"], width=40)
                else: st.markdown("👤")
            with header_cols[1]:
                st.markdown(f"<h3>@{other['username']}</h3><p>{other.get('full_name','')}</p>", unsafe_allow_html=True)
            st.markdown("---")
            m1 = [{**m.to_dict(), "me": True} for m in db.collection("messages").where("sender_id","==",me["user_id"]).where("receiver_id","==",other["user_id"]).get()]
            m2 = [{**m.to_dict(), "me": False} for m in db.collection("messages").where("sender_id","==",other["user_id"]).where("receiver_id","==",me["user_id"]).get()]
            msgs = sorted(m1 + m2, key=lambda x: x.get("timestamp",""))
            chat_box = st.container()
            with chat_box:
                if not msgs: st.markdown("<p style='text-align:center; color:#666;'>No messages yet. Say hello! 👋</p>", unsafe_allow_html=True)
                for m in msgs:
                    is_me = m.get("me", False)
                    cls = "chat-bubble-user" if is_me else "chat-bubble-other"
                    align = "right" if is_me else "left"
                    tm = m.get("timestamp", "")[11:16]
                    st.markdown(f"<div style='text-align:{align}; margin:8px 0; overflow:hidden;'><div class='{cls}'>{m['message_body']}</div><div style='clear:both;'></div><div style='font-size:0.7rem; color:#555; text-align:{align};'>{tm}</div></div>", unsafe_allow_html=True)
            st.markdown("---")
            with st.form("msg_form", clear_on_submit=True):
                cols = st.columns([4, 1])
                txt = cols[0].text_input("Message...", label_visibility="collapsed")
                if cols[1].form_submit_button("📤") and txt.strip():
                    db.collection("messages").add({"sender_id": me["user_id"], "receiver_id": other["user_id"], "message_body": txt.strip(), "timestamp": datetime.now().isoformat()})
                    st.rerun()

# FRIENDS
elif page == "Friends":
    st.markdown("<h1 style='text-align:center;'>👥 Friends</h1>", unsafe_allow_html=True)
    incoming = get_incoming_reqs(me["user_id"])
    if incoming:
        st.subheader("🔔 Friend Requests")
        for req in incoming:
            sender = get_profile(req["sender_id"])
            if sender:
                cols = st.columns([3, 1, 1])
                cols[0].markdown(f"**@{sender['username']}** {sender['full_name']}")
                if cols[1].button("✅ Accept", key=f"acc_{req['id']}"):
                    accept_friend_req(req["id"])
                    st.success("Friend added!"); time.sleep(1); st.rerun()
                if cols[2].button("❌ Reject", key=f"rej_{req['id']}"):
                    db.collection("friend_requests").document(req["id"]).delete()
                    st.rerun()
        st.markdown("---")
    st.subheader("My Friends")
    friends = get_my_friends(me["user_id"])
    if not friends: st.info("No friends yet. Go to Search to find people!")
    else:
        for f in friends:
            if not f: continue
            cols = st.columns([1, 2, 1])
            with cols[0]:
                if f.get("profile_pic"): st.image(f["profile_pic"], width=50)
                else: st.markdown("👤")
            cols[1].markdown(f"**@{f['username']}**<br>{f['full_name']}", unsafe_allow_html=True)
            if cols[2].button("💬 Chat", key=f"fchat_{f['user_id']}"):
                st.session_state.chat_user = f
                st.session_state.page = "Chats"
                st.rerun()

# PROFILE
elif page == "Profile":
    uid = st.session_state.get("view_user") or me["user_id"]
    prof = get_profile(uid)
    is_me = uid == me["user_id"]
    if not prof:
        st.error("Profile not found")
        st.stop()
    cover = prof.get("cover_pic", "")
    if cover: st.image(cover, use_container_width=True)
    else: st.markdown("<div style='height:200px; background:linear-gradient(135deg,#00f3ff,#ff00ff); border-radius:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        pic = prof.get("profile_pic", "")
        if pic: st.image(pic, width=120)
        else: st.markdown("<div style='width:120px;height:120px;border-radius:50%;background:#333;display:flex;align-items:center;justify-content:center;font-size:3rem;margin:auto;'>👤</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h1>{prof['full_name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#00f3ff;'>@{prof['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"📍 {prof.get('city','')} · 🎂 {prof.get('birthday','')}")
        st.markdown(f"📝 {prof.get('bio','')}")
        friends_count = len(list(db.collection("friends").where("users", "array_contains", uid).get()))
        st.markdown(f"**{friends_count}** Friends")
    with c3:
        if is_me:
            st.subheader("Edit Profile")
            new_pic = st.text_input("Profile Pic URL", value=prof.get("profile_pic", ""))
            new_cover = st.text_input("Cover Pic URL", value=prof.get("cover_pic", ""))
            if st.button("Update Profile"):
                db.collection("users").document(uid).update({"profile_pic": new_pic, "cover_pic": new_cover})
                st.session_state.user = get_profile(uid)
                st.success("Updated!"); time.sleep(1); st.rerun()
        else:
            status = get_friend_status(me["user_id"], uid)
            if status == "none":
                if st.button("➕ Add Friend"):
                    send_friend_req(me["user_id"], uid)
                    st.success("Request sent!"); time.sleep(1); st.rerun()
            elif status == "friends":
                st.markdown("<p style='color:#00ff7f;'>✨ Friends</p>", unsafe_allow_html=True)
                if st.button("💬 Message"):
                    st.session_state.chat_user = prof
                    st.session_state.page = "Chats"
                    st.rerun()
            elif status == "pending_in": st.markdown("<p style='color:#ffa500;'>⏳ They sent you a request</p>", unsafe_allow_html=True)
            elif status == "pending_out": st.markdown("<p style='color:#ffa500;'>⏳ Request sent</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Posts")
    # FIXED: No order_by with where - sort in Python instead
    user_posts = list(db.collection("posts").where("author_id", "==", uid).limit(50).get())
    user_posts.sort(key=lambda x: x.to_dict().get("timestamp", ""), reverse=True)
    if not user_posts: st.info("No posts yet")
    for post in user_posts:
        p = post.to_dict()
        st.markdown(f"<div class='post-card'><p>{p.get('content','')}</p></div>", unsafe_allow_html=True)
        if p.get("image"): st.image(p["image"], use_container_width=True)
        if p.get("video"): st.video(p["video"])

# AI STUDIO
elif page == "AI":
    st.markdown("<h1 style='text-align:center;'>🤖 AI Studio</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Chat with Devi AI")
        for msg in st.session_state.ai_msgs:
            is_user = msg["role"] == "user"
            cls = "chat-bubble-user" if is_user else "chat-bubble-other"
            align = "right" if is_user else "left"
            st.markdown(f"<div style='text-align:{align};'><div class='{cls}'>{msg['content']}</div></div>", unsafe_allow_html=True)
        with st.form("ai_chat", clear_on_submit=True):
            p = st.text_input("Ask anything...")
            if st.form_submit_button("Send") and p.strip():
                st.session_state.ai_msgs.append({"role": "user", "content": p})
                try:
                    client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
                    resp = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": "You are Devi AI, a helpful assistant."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_msgs], max_tokens=1024)
                    st.session_state.ai_msgs.append({"role": "assistant", "content": resp.choices[0].message.content})
                except Exception as e: st.error(str(e))
                st.rerun()
    with c2:
        st.subheader("✨ Caption Generator")
        topic = st.text_area("Post topic...")
        tone = st.selectbox("Tone", ["Casual", "Funny", "Professional", "Inspirational"])
        if st.button("Generate"):
            try:
                client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
                resp = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": f"Create a {tone} social media caption about: {topic}. Under 80 words. Add hashtags."}], max_tokens=256)
                cap = resp.choices[0].message.content
                st.markdown(f"<div style='background:rgba(0,243,255,0.1);padding:15px;border-radius:10px;border:1px solid #00f3ff;'>{cap}</div>", unsafe_allow_html=True)
                if st.button("Use in Feed"):
                    st.session_state["post_text"] = cap
                    st.session_state.page = "Feed"
                    st.rerun()
            except Exception as e: st.error(str(e))
