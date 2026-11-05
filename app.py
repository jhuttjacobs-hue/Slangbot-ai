import os
import random
import streamlit as st
from openai import OpenAI

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VibeBot AI", page_icon="🤖", layout="centered")
st.title("🤖 VibeBot AI")
st.caption("The customizable AI chatbot with full control over its personality toggles.")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Bot Personality Settings")

use_emojis = st.sidebar.toggle("Enable Emojis", value=True, help="Allows the AI to use expressive emojis.")
use_slang = st.sidebar.toggle("Enable Slang", value=True, help="Allows the AI to use Gen-Z slang and casual text shortcuts.")
use_gifs = st.sidebar.toggle("Enable GIFs", value=True, help="Instructs the AI to embed relevant GIPHY/Tenor visual links.")

st.sidebar.divider()

# API Configuration
st.sidebar.subheader("🔑 API Configuration")
api_provider = st.sidebar.selectbox("LLM Provider", ["OpenAI", "Groq", "Ollama (Local)", "Fallback Simulation Mode"])
api_key = st.sidebar.text_input("Enter API Key", type="password", disabled=(api_provider == "Ollama (Local)" or api_provider == "Fallback Simulation Mode"))

# --- DYNAMIC SYSTEM PROMPT CONSTRUCTOR ---
def build_system_prompt(emojis, slang, gifs):
    prompt_segments = [
        "You are VibeBot, an incredibly engaging and responsive AI companion. Your response structure is strictly dictated by the following layout rules:"
    ]
    
    # Emoji rule
    if emojis:
        prompt_segments.append("- EMOJIS: ALWAYS use vibrant and contextual emojis throughout your sentences to express mood and enthusiasm.")
    else:
        prompt_segments.append("- EMOJIS: Do NOT use any emojis under any circumstances. Keep your text completely clean of emoticons or graphic characters.")
        
    # Slang rule
    if slang:
        prompt_segments.append("- SLANG: Use current Gen-Z slang, internet vernacular, and abbreviations (e.g., 'no cap', 'bet', 'fr fr', 'bussin', 'lowkey', 'skibidi', 'rizz', 'cooking'). Sound casual, warm, and highly expressive.")
    else:
        prompt_segments.append("- SLANG: Maintain an articulate, clean, and standard grammatical tone. Avoid all internet jargon, slang terms, or modern colloquial phrases.")
        
    # GIF rule
    if gifs:
        prompt_segments.append("- GIFs: At the very end of your response, you MUST append a relevant markdown GIF syntax line from public sources (e.g., `![gif](https://giphy.com)`). Ensure the URL path looks like a standard valid public gif image asset to show the user.")
    else:
        prompt_segments.append("- GIFs: Do NOT append any image links, markdown images, or GIF links to the end of your response.")

    return " ".join(prompt_segments)

# --- BACKEND LLM CALL ROUTER ---
def get_ai_response(messages, provider, key, system_prompt):
    # Construct formatting list
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    # Run structural fallback if selected or key is missing
    if provider == "Fallback Simulation Mode" or (provider == "OpenAI" and not key) or (provider == "Groq" and not key):
        return mock_llm_response(messages[-1]["content"], use_emojis, use_slang, use_gifs)
        
    try:
        if provider == "OpenAI":
            client = OpenAI(api_key=key)
            model_name = "gpt-4o-mini"
        elif provider == "Groq":
            client = OpenAI(base_url="https://groq.com", api_key=key)
            model_name = "llama3-8b-8192"
        elif provider == "Ollama (Local)":
            client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            model_name = "llama3"
            
        response = client.chat.completions.create(
            model=model_name,
            messages=full_messages,
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ **Connection Error:** Could not reach the provider ({str(e)}). Defaulting to Simulation mode rules..."

# --- FALLBACK SIMULATION DATABASE ---
def mock_llm_response(user_input, emojis, slang, gifs):
    responses = [
        "That's wild! Tell me more about what you're thinking.",
        "Honestly, I was just thinking about exactly that.",
        "We are completely on the same wavelength right now.",
        "I'm locked in. What's the next step on this roadmap?"
    ]
    base = random.choice(responses)
    
    if slang:
        base = base.replace("That's wild!", "Yo that's lowkey unhinged fr fr! 🔥")
        base = base.replace("Tell me more", "Keep cooking")
        base = base.replace("completely on the same wavelength", "majorly vibing right now, no cap")
    if not emojis:
        base = base.replace("🔥", "")
        
    emoji_pool = ["🚀", "✨", "💯", "🤯", "😎", "👾"] if emojis else []
    emoji_str = " " + "".join(random.sample(emoji_pool, 2)) if emoji_pool else ""
    
    gif_str = "\n\n![vibe](https://giphy.com)" if gifs else ""
    
    return f"{base}{emoji_str}{gif_str}"

# --- CHAT SESSION MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt ingestion
if prompt := st.chat_input("Say something to VibeBot..."):
    # Render user chat bubble
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate personality configuration
    current_system_prompt = build_system_prompt(use_emojis, use_slang, use_gifs)
    
    # Process and render bot response
    with st.chat_message("assistant"):
        with st.spinner("Vibing..."):
            ai_reply = get_ai_response(st.session_state.messages, api_provider, api_key, current_system_prompt)
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
