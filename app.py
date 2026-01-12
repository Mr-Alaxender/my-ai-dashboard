import streamlit as st
from groq import Groq
from tavily import TavilyClient

# 1. Dashboard ki setting
st.set_page_config(page_title="My AI Search", layout="centered")
st.title("🤖 My Personal AI Search")
st.write("Duniya ki kisi bhi book ya news ke bare mein poochein.")

# 2. Keys ko Streamlit Secrets se uthana (Security ke liye)
# Note: Jab app live hogi, tab hum wahan ye keys bharenge
GROQ_KEY = st.secrets["GROQ_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]

# 3. AI aur Search engine ko connect karna
tavily = TavilyClient(api_key=TAVILY_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# 4. Chat history (taki AI purani baat yaad rakhe)
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. User ka sawal lena
if prompt := st.chat_input("Yahan likhein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. AI ka jawab tayyar karna
    with st.chat_message("assistant"):
        with st.spinner("Searching the world..."):
            # Internet search
            search = tavily.search(query=prompt)
            context = str(search['results'])
            
            # AI response generation
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"Answer in Roman Urdu: {context}"},
                    {"role": "user", "content": prompt}
                ]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
