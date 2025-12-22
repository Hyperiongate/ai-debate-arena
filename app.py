import streamlit as st
from debate_engine import DebateEngine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="AI Debate Arena", page_icon="⚔️", layout="wide")

# Title
st.title("⚔️ AI Debate Arena")
st.markdown("*Research tool for AI-to-AI debate analysis*")

# Sidebar controls
st.sidebar.header("Debate Configuration")

# Topic input
topic = st.sidebar.text_input("Debate Topic", 
    value="Universal Basic Income should be implemented nationally within 5 years",
    help="Enter the proposition to be debated")

# AI selection
ai_options = [
    "claude-sonnet-4-20250514",
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-3.5-turbo",
    "gemini-pro"
]

col1, col2 = st.sidebar.columns(2)
with col1:
    ai_pro = st.selectbox("PRO AI", ai_options, index=0)
with col2:
    ai_con = st.selectbox("CON AI", ai_options, index=1)

# Debate parameters
rounds = st.sidebar.slider("Number of Rounds", min_value=3, max_value=15, value=5)
word_limit = st.sidebar.slider("Words per Turn", min_value=100, max_value=500, value=200, step=50)

# Mode selection
mode = st.sidebar.radio("Debate Mode", ["Adversarial", "Truth-Seeking"])

# Run button
if st.sidebar.button("🎯 Run Debate", type="primary"):
    
    # Validate API keys
    if not os.getenv("ANTHROPIC_API_KEY") and ai_pro.startswith("claude"):
        st.error("Anthropic API key not found!")
        st.stop()
    if not os.getenv("OPENAI_API_KEY") and (ai_pro.startswith("gpt") or ai_con.startswith("gpt")):
        st.error("OpenAI API key not found!")
        st.stop()
    if not os.getenv("GOOGLE_API_KEY") and (ai_pro.startswith("gemini") or ai_con.startswith("gemini")):
        st.error("Google API key not found!")
        st.stop()
    
    with st.spinner(f"Running {rounds}-round debate..."):
        engine = DebateEngine()
        debate_log = engine.run_debate(topic, ai_pro, ai_con, rounds, word_limit, mode)
        
        # Display results
        st.success(f"✅ Debate complete! {rounds} rounds finished.")
        
        st.markdown("---")
        st.markdown(f"### 📋 Topic: *{topic}*")
        st.markdown(f"**Mode:** {mode} | **Rounds:** {rounds} | **Word Limit:** {word_limit}")
        
        # Display each round
        for entry in debate_log:
            st.markdown(f"## Round {entry['round']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🟢 PRO ({entry['pro_ai']})**")
                st.markdown(entry['pro_response'])
                st.caption(f"Words: {len(entry['pro_response'].split())}")
            
            with col2:
                st.markdown(f"**🔴 CON ({entry['con_ai']})**")
                st.markdown(entry['con_response'])
                st.caption(f"Words: {len(entry['con_response'].split())}")
            
            st.markdown("---")

else:
    # Instructions
    st.info("👈 Configure your debate in the sidebar and click 'Run Debate' to begin")
    
    st.markdown("""
    ### How to Use:
    1. **Enter a debate topic** - Make it a clear proposition (e.g., "X should happen")
    2. **Select AI systems** - Choose which AIs will argue PRO and CON
    3. **Set parameters** - Rounds (3-15), word limit (100-500)
    4. **Choose mode**:
       - **Adversarial**: AIs try to win the debate
       - **Truth-Seeking**: AIs collaborate to find the best answer
    5. **Run the debate** - Watch the arguments unfold round by round
    
    ### Research Applications:
    - Compare how different AI systems argue the same position
    - Observe convergence patterns in truth-seeking mode
    - Analyze argument quality evolution across rounds
    - Test controversial topics across multiple AI pairings
    """)
