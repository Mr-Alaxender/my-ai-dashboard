import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- 1. Cool Interface Design ---
st.set_page_config(page_title="Zain's Pro AI", page_icon="⚡", layout="centered")

# Custom CSS for Dark Mode and better look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    h1 { color: #00ffcc; text-shadow: 2px 2px 5px #000; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("⚡ Zain's Personal Pro AI")
st.write("Duniya ka koi bhi sawal ho, internet se dhoond kar jawab milega!")

# --- 2. Setup ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]

tavily = TavilyClient(api_key=TAVILY_KEY)
groq_client = Groq(api_key=GROQ_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Logic (Asli Dimagh) ---
if prompt := st.chat_input("Puchiye, main hazir hoon..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Zara ruko, internet par check kar raha hoon... 🔍"):
            search = tavily.search(query=prompt, search_depth="advanced")
            context = str(search['results'])
            
            # AI ko "Dost" banane ki hidayat
            system_instruction = f"""
            Aap ek professional magar dostana AI assistant hain. 
            In search results ko parh kar Roman Urdu mein mazeedar tareeke se jawab dein: {context}
            Boring machine ki tarah jawab na dein. Point-wise samjhayein aur emojis use karein.
            """
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Maine model badal diya hai, ye zyada samajhdaar hai!
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            full_ans = response.choices[0].message.content
            st.markdown(full_ans)
            st.session_state.messages.append({"role": "assistant", "content": full_ans})
