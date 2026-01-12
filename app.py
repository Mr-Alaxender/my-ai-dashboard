import streamlit as st
from groq import Groq
from tavily import TavilyClient
from streamlit_mic_recorder import mic_recorder

# --- ChatGPT Pro Interface ---
st.set_page_config(page_title="Zain GPT Voice", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #212121; color: #ececf1; }
    h1 { color: #10a37f; }
    .voice-box { border: 1px solid #10a37f; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🎙️ Zain GPT Voice")

# API Keys
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VOICE INPUT SECTION ---
st.write("Bol kar sawal poochein:")
audio = mic_recorder(start_prompt="🔴 Record (Bolain)", stop_prompt="🟢 Stop", key='recorder')

user_input = None

# Agar audio record ho jaye
if audio:
    with st.spinner("Aapki awaz samajh raha hoon..."):
        # Awaz ko text mein badalna (Whisper Model)
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio['bytes']),
            model="whisper-large-v3",
            response_format="text",
        )
        user_input = transcription

# Manual Type karne ke liye
manual_input = st.chat_input("Ya yahan type karein...")
if manual_input:
    user_input = manual_input

# --- MAIN LOGIC ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # AI Response
    with st.chat_message("assistant"):
        with st.spinner("Internet se dhoond raha hoon..."):
            search = tavily.search(query=user_input, search_depth="advanced")
            context = str(search['results'])
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are Zain GPT. Use this info to answer in Roman Urdu/Hindi: {context}"},
                    *st.session_state.messages
                ]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
