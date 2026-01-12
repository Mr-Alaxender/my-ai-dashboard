import streamlit as st
from groq import Groq
from tavily import TavilyClient
from streamlit_mic_recorder import mic_recorder

# --- 1. Pro Interface Design (ChatGPT Style) ---
st.set_page_config(page_title="Zain GPT Pro", page_icon="⚡", layout="centered")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Overall Background */
    .stApp { background-color: #212121; color: #D1D5DB; }
    
    /* Chat Bubbles */
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 12px; border: 1px solid #3e3f4b; }
    .stChatMessage[data-testimonial="user"] { background-color: #343541; }
    .stChatMessage[data-testimonial="assistant"] { background-color: #444654; }
    
    /* Custom Header */
    .main-title { color: #10a37f; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    
    /* Voice Button Styling */
    .stButton>button { background-color: #10a37f; color: white; border-radius: 20px; border: none; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #1a7f64; transform: scale(1.02); }
    
    /* Input Bar */
    .stChatInputContainer { padding: 20px; background-color: transparent !important; }
    </style>
    <div class="main-title">⚡ Zain GPT Pro</div>
    """, unsafe_allow_html=True)

# --- 2. Setup & Logic ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar (History Management) ---
with st.sidebar:
    st.title("Settings")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Voice Input (Professional Layout) ---
col1, col2 = st.columns([1, 4])
with col1:
    audio = mic_recorder(start_prompt="🎙️ Speak", stop_prompt="🛑 Stop", key='recorder')

user_input = None

if audio:
    with st.spinner("Processing voice..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio['bytes']),
            model="whisper-large-v3",
            response_format="text",
        )
        user_input = transcription

# Manual Chat Input
if manual_input := st.chat_input("Type your message here..."):
    user_input = manual_input

# --- 5. Response Generation ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display previous chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Generating Answer
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            # Real-time Web Search
            search = tavily.search(query=user_input, search_depth="advanced")
            context = str(search['results'])
            
            # Smart AI Response using Llama 3.3 70B
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are Zain GPT Pro, a smart, helpful AI. Answer in detailed Roman Urdu using this info: {context}. Use emojis and bold text to look professional."},
                    *st.session_state.messages
                ],
                temperature=0.7
            )
            full_res = response.choices[0].message.content
            message_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
