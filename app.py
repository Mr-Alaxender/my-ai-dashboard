import streamlit as st
from groq import Groq
from tavily import TavilyClient
import replicate
from streamlit_mic_recorder import mic_recorder

# --- 1. UI Configuration (AI Studio Pro) ---
st.set_page_config(page_title="Zain AI Studio Pro", page_icon="💎", layout="wide")

# Premium White Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    .main-title { color: #059669; font-size: 42px; font-weight: 900; text-align: center; margin-bottom: 5px; }
    .stChatMessage { border-radius: 15px; padding: 20px; border: 1px solid #E5E7EB; margin-bottom: 15px; }
    div[data-testimonial="user"] { background-color: #F9FAFB; border: none; }
    div[data-testimonial="assistant"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; }
    .stButton>button { background-color: #059669; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .stChatInputContainer { border-top: 1px solid #F3F4F6 !important; }
    </style>
    <div class="main-title">💎 Zain AI Studio Pro</div>
    <p style='text-align: center; color: #6B7280;'>Advanced Multilingual Workspace | Voice | Image | Search</p>
    """, unsafe_allow_html=True)

# --- 2. Keys & Setup ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    
    client = Groq(api_key=GROQ_KEY)
    tavily = TavilyClient(api_key=TAVILY_KEY)
except Exception as e:
    st.error("Secrets are missing! Please add GROQ_API_KEY, TAVILY_API_KEY, and REPLICATE_API_TOKEN in Streamlit Settings.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar Controls ---
with st.sidebar:
    st.markdown("<h2 style='color: #059669;'>⚙️ Studio Settings</h2>", unsafe_allow_html=True)
    selected_model = st.selectbox("AI Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    creativity = st.slider("Creativity Level", 0.0, 1.0, 0.7)
    internet_toggle = st.toggle("Live Web Access", value=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear All History"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Workspace (Tabs) ---
tab1, tab2 = st.tabs(["💬 Professional Chat", "🎨 Image Studio"])

# --- TAB 1: CHAT ENGINE ---
with tab1:
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Section
    col1, col2 = st.columns([1, 6])
    with col1:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='studio_mic')
    
    user_input = st.chat_input("Ask me anything...")

    if audio:
        with st.spinner("Decoding voice..."):
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio['bytes']), model="whisper-large-v3", response_format="text")
            user_input = transcription

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_res = ""
            
            # Web Search if enabled
            context = ""
            if internet_toggle:
                with st.spinner("Searching web..."):
                    search = tavily.search(query=user_input, search_depth="advanced")
                    context = str(search['results'])

            # AI Persona
            system_msg = f"""
            You are 'Zain AI Studio Pro'. You are an elite, friendly, and smart assistant.
            Response Style: Use Roman Urdu/Hindi mixed with English. Be detailed and helpful.
            Current Context: {context}
            Always use emojis and bold text for key points.
            """

            # Streaming Response
            completion = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": system_msg}, *st.session_state.messages],
                temperature=creativity,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

# --- TAB 2: IMAGE ENGINE ---
with tab2:
    st.subheader("🖼️ Create High-End Images")
    img_prompt = st.text_area("Describe your image (English recommended):", 
                              placeholder="Example: A futuristic Lahore city with flying cars, cinematic lighting, 8k resolution...")
    
    if st.button("Generate Masterpiece ✨"):
        if img_prompt:
            with st.spinner("AI is painting your imagination..."):
                try:
                    # Using FLUX-Schnell for speed and quality
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": img_prompt}
                    )
                    st.image(output[0], caption="Generated by Zain AI Studio", use_container_width=True)
                    st.success("Your image is ready!")
                except Exception as e:
                    st.error(f"Error: {e}. Please check your Replicate Token in Secrets.")
        else:
            st.warning("Please enter a prompt first!")
