import streamlit as st
from agents import SubjectAgent, ExpertAgent
from config import BOARDS, SUBJECTS, DEFAULT_MODEL
from guardrails import input_allowed
import db

st.set_page_config(page_title="PakEd Chatbot", layout="wide")

st.markdown("""
<style>
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #ffffff; }
h1 { font-size:36px; color:#006400; font-weight:800; text-align:center; margin-bottom:20px; }
.chat-box { background: #f8fdf8; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-height:600px; overflow-y:auto; margin-bottom:15px; }
.user-msg { background:#e6ffe6; color:#000; padding:12px 15px; border-radius:20px; margin:8px 0; max-width:75%; font-weight:500; white-space:pre-wrap; }
.bot-msg { background:#006400; color:#fff; padding:12px 15px; border-radius:20px; margin:8px 0; max-width:75%; white-space:pre-wrap; }
[data-testid="stSidebar"] { background:#006400; color:#fff; font-weight:600; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color:#fff; font-weight:700; }
textarea, input { font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-radius:10px; border:1px solid #cfd8dc; padding:10px; width:100%; }
.stButton>button { background:#006400; color:#fff; font-weight:600; border-radius:12px; padding:10px 20px; transition:0.3s; }
.stButton>button:hover { background:#004d00; }
.chat-box::-webkit-scrollbar { width:8px; }
.chat-box::-webkit-scrollbar-thumb { background-color:#006400; border-radius:4px; }
.chat-box::-webkit-scrollbar-track { background:#f8fdf8; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 PakEd — Pakistani Education Chatbot")


db.init_db()


if "language" not in st.session_state:
    st.session_state.language = "English"

with st.sidebar:
    st.header("Setup")
    board = st.selectbox("Select Board", BOARDS)
    subject = st.selectbox("Select Subject", SUBJECTS)
    start = st.button("Start New Session")
    st.markdown("---")
    st.subheader("Language")
    st.session_state.language = st.radio("Choose language", ["English", "Urdu"], index=0)
    st.markdown("---")
    st.write("Model:")
    st.write(DEFAULT_MODEL)


if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.history = []


if start:
    sid = db.create_session(board, subject)
    st.session_state.session_id = sid
    st.session_state.history = []
    st.success(f"Session started (id={sid}) — Board: {board}, Subject: {subject}")


st.header(f"{subject} - {board}")

if st.session_state.session_id:
    msgs = db.get_session_messages(st.session_state.session_id)
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for m in msgs:
        if m["role"] == "user":
            st.markdown(f"<div class='user-msg'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{m['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Start a session from the sidebar to begin.")

st.markdown("---")
user_input = st.text_area("Your question", height=150, placeholder="Type your question here...")

if st.button("Send"):
    allowed, reason = input_allowed(user_input)
    if not allowed:
        st.warning(reason)
    elif not st.session_state.session_id:
        st.error("Start a session first.")
    else:
       
        db.save_message(st.session_state.session_id, "user", user_input)


        agent = SubjectAgent(board=board, subject=subject)

       
        answer = agent.ask(f"[{st.session_state.language}] {user_input}", history=st.session_state.history)


        if "I do not know" in answer or len(answer) < 10:
            expert = ExpertAgent()
            answer = expert.ask(f"[{st.session_state.language}] Student question (board={board}, subject={subject}): {user_input}")

  
        db.save_message(st.session_state.session_id, "bot", answer)

        
        if "rerun_toggle" not in st.session_state:
            st.session_state.rerun_toggle = False
        st.session_state.rerun_toggle = not st.session_state.rerun_toggle













