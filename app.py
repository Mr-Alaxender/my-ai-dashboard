import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- 1. ChatGPT Style UI ---
st.set_page_config(page_title="Zain GPT", page_icon="🧠", layout="centered")

# CSS for Pro look
st.markdown("""
    <style>
    .stApp { background-color: #212121; color: #ececf1; }
    .stChatMessage { border-radius: 10px; padding: 10px; margin: 5px 0; }
    .stChatInputContainer { border-top: 1px solid #4d4d4d; }
    h1 { color: #10a37f; font-family: 'SANS-SERIF'; }
    .stSpinner { color: #10a37f; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🧠 Zain GPT (Pro)")
st.caption("Internet-Connected AI | Powered by Llama 3.3 70B")

# --- 2. API Keys ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]

tavily = TavilyClient(api_key=TAVILY_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# --- 3. Chat Logic & History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Processing User Input ---
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching the web and thinking..."):
            try:
                # Search internet for real-time data
                search = tavily.search(query=prompt, search_depth="advanced")
                context = ""
                for result in search['results']:
                    context += f"\nSource: {result['url']}\nContent: {result['content']}\n"
                
                # Professional System Instruction
                system_prompt = f"""
                You are Zain GPT, a highly advanced AI similar to ChatGPT. 
                Use the following internet search results to provide a comprehensive, 
                intelligent, and friendly response in Roman Urdu/Hindi.
                
                Context: {context}
                
                Guidelines:
                1. Give detailed and long answers if necessary.
                2. Use bullet points and bold text for readability.
                3. Be conversational and smart, not like a dry machine.
                4. Always acknowledge the search results.
                """
                
                # Call the massive Llama 3.3 70B Model
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages # Passes full conversation history
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
