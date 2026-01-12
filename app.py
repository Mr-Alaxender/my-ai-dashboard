import streamlit as st
from groq import Groq
from tavily import TavilyClient
import replicate
from streamlit_mic_recorder import mic_recorder

# --- 1. Educational UI Design ---
st.set_page_config(page_title="Zain Study Studio", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1F2937; }
    .main-title { color: #059669; font-size: 40px; font-weight: 800; text-align: center; margin-bottom: 0px; }
    .stChatMessage { border-radius: 12px; padding: 20px; border: 1px solid #E5E7EB; margin-bottom: 15px; }
    div[data-testimonial="user"] { background-color: #F9FAFB; border: none; }
    div[data-testimonial="assistant"] { background-color: #FFFFFF; border: 1px solid #E5E7EB; }
    .stButton>button { background-color: #059669; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .stChatInputContainer { border-top: 1px solid #F3F4F6 !important; }
    </style>
    <div class="main-title">🎓 Zain Educational Studio</div>
    <p style='text-align: center; color: #6B7280;'>Personalized Learning & Creative AI Workspace</p>
    """, unsafe_allow_html=True)

# --- 2. API Setup ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    REPLICATE_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    
    client = Groq(api_key=GROQ_KEY)
    tavily = TavilyClient(api_key=TAVILY_KEY)
except Exception as e:
    st.error("Secrets Error: Keys missing hain. Check settings!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Sidebar (Learning Controls) ---
with st.sidebar:
    st.markdown("<h2 style='color: #059669;'>📖 Study Center</h2>", unsafe_allow_html=True)
    study_mode = st.toggle("🎓 Deep Study Mode", value=True)
    selected_model = st.selectbox("AI Intelligence", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    internet_access = st.toggle("Global Research", value=True)
    
    st.markdown("---")
    if st.button("🗑️ Reset All Sessions"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Main Workspace ---
tab1, tab2 = st.tabs(["📚 Interactive Tutor", "🎨 Educational Visuals"])

# --- TAB 1: SMART TUTOR ---
with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    col_v, col_t = st.columns([1, 8])
    with col_v:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='edu_mic')
    
    user_input = st.chat_input("Ask a question or explain a topic...")

    if audio:
        with st.spinner("Processing voice..."):
            trans = client.audio.transcriptions.create(
                file=("audio.wav", audio['bytes']), model="whisper-large-v3", response_format="text")
            user_input = trans

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_res = ""
            
            context = ""
            if internet_access:
                with st.spinner("Researching facts..."):
                    search = tavily.search(query=user_input, search_depth="advanced")
                    context = str(search['results'])

            # Smart Educational Prompt
            if study_mode:
                sys_msg = f"""
                Aap aik expert 'Personal AI Tutor' hain.
                Aapka mizaaj dostana aur sikhane wala hai.
                Zaban: Roman Urdu, Hindi aur English ka mixture.
                
                Rules:
                1. Concept ko aik dam asaan zaban mein aur misalon (examples) ke saath samjhayein.
                2. Points aur Bold text ka bharpoor use karein.
                3. Jawab detailed hona chahiye taaki user ko topic poora samajh aaye.
                4. Context: {context}
                """
            else:
                sys_msg = f"Aap aik smart assistant hain. Roman Urdu mein jawab dein. Context: {context}"

            completion = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": sys_msg}, *st.session_state.messages],
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

# --- TAB 2: VISUAL STUDIO ---
with tab2:
    st.subheader("🖼️ Generate Visual Learning Aids")
    img_prompt = st.text_area("What would you like to visualize?", 
                              placeholder="Example: Diagram of the solar system, A 3D render of a futuristic library...")
    
    if st.button("Create Visual ✨"):
        if img_prompt:
            with st.spinner("AI is creating your visual..."):
                try:
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={"prompt": img_prompt}
                    )
                    st.image(output[0], use_container_width=True)
                except Exception as e:
                    st.error("Error! Replicate key check karein.")
        else:
            st.warning("Prompt likhna zaroori hai!")
