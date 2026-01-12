import streamlit as st
from groq import Groq
from tavily import TavilyClient
import replicate
from streamlit_mic_recorder import mic_recorder

# --- 1. Studio Pro UI Settings ---
st.set_page_config(page_title="Zain AI Studio Pro", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    .main-title { color: #059669; font-size: 45px; font-weight: 900; text-align: center; margin-bottom: 0px; letter-spacing: -1px; }
    .stChatMessage { border-radius: 15px; padding: 20px; border: 1px solid #E5E7EB; margin-bottom: 15px; }
    div[data-testimonial="user"] { background-color: #F9FAFB; border: none; }
    div[data-testimonial="assistant"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; }
    .stButton>button { background-color: #059669; color: white; border-radius: 10px; font-weight: bold; height: 3em; }
    .stChatInputContainer { border-top: 1px solid #F3F4F6 !important; }
    </style>
    <div class="main-title">💎 Zain AI Studio Pro</div>
    <p style='text-align: center; color: #6B7280; font-size: 18px;'>Aapka apna premium AI dost.</p>
    """, unsafe_allow_html=True)

# --- 2. API Setup & Error Handling ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    
    client = Groq(api_key=GROQ_KEY)
    tavily = TavilyClient(api_key=TAVILY_KEY)
except Exception as e:
    st.error("Oho! Keys missing hain. Streamlit Secrets mein teeno keys lazmi dalein.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar Configuration ---
with st.sidebar:
    st.markdown("<h2 style='color: #059669;'>⚙️ Studio Settings</h2>", unsafe_allow_html=True)
    selected_model = st.selectbox("AI Model Select Karein", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    creativity = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.8)
    internet_toggle = st.toggle("Live Internet Search", value=True)
    
    st.markdown("---")
    if st.button("🗑️ Reset All Conversations"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Workspace ---
tab1, tab2 = st.tabs(["💬 Personal Chat", "🎨 Image Studio"])

# --- TAB 1: MERE JAISA CHAT ENGINE ---
with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Voice and Text Input
    col_mic, col_input = st.columns([1, 8])
    with col_mic:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='studio_mic')
    
    user_input = st.chat_input("Zain bhai, aaj kya plan hai?")

    if audio:
        with st.spinner("Aapki awaz samajh raha hoon..."):
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio['bytes']), model="whisper-large-v3", response_format="text")
            user_input = transcription

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_res = ""
            
            context = ""
            if internet_toggle:
                with st.spinner("Internet se dhoond raha hoon..."):
                    search = tavily.search(query=user_input, search_depth="advanced")
                    context = str(search['results'])

            # THE PROMPT: AI ko mere jaisa banane wala system message
            system_msg = f"""
            Aapka naam 'Zain AI Studio Pro' hai. Aap Zain bhai ke banaye hue ek bohot hi advance, dostana, aur zinda dil AI assistant hain.
            Aap bilkul insani andaaz mein baat karte hain, machine ki tarah dry aur boring nahi.
            
            **Rules:**
            1. Zaban: Roman Urdu, Hindi aur English ka mixture use karein (Hinglish/Urduish).
            2. Style: "Zabardast!", "Bilkul!", "Sahi kaha aapne!" jaise phrases use karein.
            3. Detailed: Jawab hamesha tafseeli aur helpful ho.
            4. Formatting: Bold text aur Emojis ka bharpoor istemal karein.
            5. Context: Use this info: {context}
            """

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

# --- TAB 2: IMAGE STUDIO ---
with tab2:
    st.subheader("🖼️ Create High-Resolution Images")
    img_prompt = st.text_area("Tasveer ka idea likhein (English best hai):", placeholder="Example: A futuristic Pakistani boy with a robot friend, 4k, cinematic...")
    
    if st.button("Generate Image ✨"):
        if img_prompt:
            with st.spinner("Wait... AI tasveer bana raha hai..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": img_prompt}
                    )
                    st.image(output[0], caption="Generated by Zain AI Studio", use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}. Replicate Key check karein.")
        else:
            st.warning("Pehle prompt likhein!")
