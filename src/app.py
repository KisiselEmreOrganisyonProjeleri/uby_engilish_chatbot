import streamlit as st
from src.config import LEVELS
from src.services.gemini_chat import GeminiChatService
from src.helpers.logger import get_logger
import re # Import regex for case-insensitive replacement

logger = get_logger("StreamlitApp")

st.set_page_config(page_title="AI English Chat", page_icon="🗣️", layout="centered")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; }
    .stTextInput > div > div > input { font-size: 1.2rem; }
    .stButton > button { font-size: 1.1rem; border-radius: 1.5rem; }
    .stChatMessage { border-radius: 1.5rem; }
    .highlight-red { color: red; font-weight: bold; }
    @media (max-width: 600px) {
        .block-container { padding: 0.5rem; }
        .stTextInput > div > div > input { font-size: 1rem; }
        .stButton > button { font-size: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🗣️ AI English Conversation Practice")

# Initialize session state variables if they don't exist
if "chat_service" not in st.session_state:
    st.session_state.chat_service = None
if "focus_word" not in st.session_state:
    st.session_state.focus_word = None
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None
if "last_student_message" not in st.session_state:
    st.session_state.last_student_message = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

level = st.selectbox("Select your English level:", LEVELS, key="level_select")

if st.button("Start Conversation", use_container_width=True):
    try:
        st.session_state.chat_service = GeminiChatService(level)
        word = st.session_state.chat_service.start_conversation()
        st.session_state.focus_word = word
        st.session_state.last_evaluation = None # Clear previous evaluation
        st.session_state.last_student_message = None # Clear previous message
        st.session_state.user_input = "" # Clear input
        st.rerun() # Use st.rerun instead of st.experimental_rerun
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        st.error("Failed to start conversation. Please check your configuration and Excel files.")

if "clear_input" in st.session_state and st.session_state.clear_input:
    st.session_state.user_input = ""
    st.session_state.clear_input = False

if st.session_state.get("chat_service"):
    focus_word = st.session_state.focus_word
    st.markdown(f"<div style='text-align:center; font-size:1.1rem; color:#666;'>Focus word: <b>{focus_word}</b></div>", unsafe_allow_html=True)
    st.divider()
    # Display chat history
    for role, msg in st.session_state.chat_service.get_history():
        if role in ["system", "focus_word"]:
            continue
        elif role == "student":
            st.chat_message("user").write(msg)
            st.session_state.last_student_message = msg # Update last student message
        elif role == "ai":
            # Highlight the focus word (case-insensitive)
            highlighted_msg = re.sub(rf'({re.escape(focus_word)})', r'<span class="highlight-red">\1</span>', msg, flags=re.IGNORECASE)
            st.chat_message("assistant").markdown(highlighted_msg, unsafe_allow_html=True)

    # Display evaluation if it exists
    if st.session_state.last_evaluation:
        st.info(f"Değerlendirme: {st.session_state.last_evaluation}")

    # Input and buttons
    user_input = st.text_input("Type your message...", key="user_input", placeholder="Write your reply here")
    col1, col2 = st.columns([3, 1])
    with col1:
        send_clicked = st.button("Send", use_container_width=True)
    with col2:
        eval_clicked = st.button("Değerlendir", key="eval_button", use_container_width=True)

    # Handle Send button click
    if send_clicked and user_input:
        try:
            ai_response = st.session_state.chat_service.send_student_message(user_input)
            st.session_state.last_evaluation = None
            st.session_state.clear_input = True  # flag set
            st.rerun()
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            st.error("An error occurred during the conversation. Please try again.")

    # Handle Evaluate button click
    if eval_clicked:
        if st.session_state.last_student_message:
            try:
                evaluation = st.session_state.chat_service.evaluate_message(st.session_state.last_student_message)
                st.session_state.last_evaluation = evaluation # Store evaluation
                st.rerun() # Use st.rerun instead of st.experimental_rerun
            except Exception as e:
                logger.error(f"Error during evaluation: {e}")
                st.error("An error occurred during evaluation.")
                st.session_state.last_evaluation = "Değerlendirme yapılamadı."
        else:
            st.warning("Değerlendirilecek bir mesajınız bulunmuyor.")
            st.session_state.last_evaluation = None