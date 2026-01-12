import streamlit as st
from groq import Groq
from tavily import TavilyClient
from streamlit_mic_recorder import mic_recorder

# --- 1. Clean White Interface Design ---
st.set_page_config(page_title="Zain GPT Light", page_icon="🌤️", layout="centered")

# Custom CSS for Professional White Theme
st.markdown("""
    <style>
    /* Main Background - Pure White */
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    
    /* Chat Bubbles - Soft Grey and Light Blue */
    .stChatMessage { border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #E5E7EB; }
    
    /* User Message Bubble */
    div[data-testimonial="user"] { background-color: #F3F4F6; border: none; }
    
    /* AI Message Bubble */
    div[data-testimonial="assistant"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; }
    
    /* Header Style */
    .main-title { color: #059669; font-size: 36px; font-weight: 800; text-align: center; margin-top: -30px; margin-bottom: 10px; }
    
    /* Sidebar */
    .css-1d391kg { background-color: #F9FAFB; }
    
    /* Buttons */
    .stButton>button { background-color: #059669; color: white; border-radius: 8px; border: none; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #047857; border: none; color: white; }

    /* Input Bar Fixing */
    .stChatInputContainer { border-top: 1px solid #F3F4F6; padding-top: 10px; }
    </style>
    <div class="main-title">🌤️ Zain GPT Light</div>
    """, unsafe_allow_html=True)

# --- 2. Setup ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar ---
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Chat & Voice Logic ---
col1, col2 = st.columns([1, 5])
with col1:
    audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key='recorder')

user_input = None

if audio:
    with st.spinner("Sunte hain..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio['bytes']),
            model="whisper-large-v3",
            response_format="text",
        )
        user_input = transcription

if manual_input := st.chat_input("Yahan sawal likhein..."):
    user_input = manual_input

# --- 5. Responses ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f'<div style="color: #1F2937;">{msg["content"]}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            search = tavily.search(query=user_input, search_depth="advanced")
            context = str(search['results'])
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are Zain GPT Light. Answer in Roman Urdu. Be polite, detailed and use emojis. Context: {context}"},
                    *st.session_state.messages
                ]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
