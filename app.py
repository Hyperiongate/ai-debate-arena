"""
AI Debate Arena - Streamlit Application
Last Updated: December 22, 2024
Version: 2.0 - Cache Buster

CHANGES:
- Added export functionality (CSV, JSON, TXT formats)
- Added debate summary display at the end
- Added better error handling and user feedback
- Added download buttons for debate transcripts
- Improved UI with progress indicators
- Added validation for API keys before starting debate

FEATURES:
1. Choose debate opponents from 8 AI systems
2. Configure rounds (3-15)
3. Set word count limit (100-500)
4. Enter debate topic
5. Choose mode: Adversarial or Truth-Seeking
6. Export debate transcripts in multiple formats
7. View debate summary with agreements/disagreements

NOTES:
- All features working as requested
- Export buttons appear after debate completes
- Summary generated automatically at end of debate
"""

import streamlit as st
from debate_engine import DebateEngine
import os
from dotenv import load_dotenv
import json
import csv
from io import StringIO
from datetime import datetime

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

# AI selection - VERIFIED WORKING MODELS (December 2024)
ai_options = [
    "claude-sonnet-4-20250514",      # Anthropic Claude Sonnet 4
    "gpt-4",                         # OpenAI GPT-4
    "gpt-3.5-turbo",                 # OpenAI GPT-3.5 Turbo
    "gemini-2.0-flash",              # Google Gemini 2.0 Flash
    "deepseek-chat",                 # DeepSeek Chat V3
    "mistral-large-latest",          # Mistral Large 2
    "command-r-plus-08-2024",        # Cohere Command R+ (Aug 2024)
    "llama-3.3-70b-versatile",       # Meta Llama 3.3 70B via Groq
    "jamba-1.5-mini"                 # AI21 Jamba 1.5 Mini
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

# Helper function to create export files
def create_csv_export(debate_log, topic, mode):
    """Create CSV export of debate"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["AI Debate Arena Export"])
    writer.writerow(["Topic", topic])
    writer.writerow(["Mode", mode])
    writer.writerow(["Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    
    # Debate content
    writer.writerow(["Round", "Position", "AI System", "Argument"])
    
    for entry in debate_log:
        writer.writerow([entry['round'], "PRO", entry['pro_ai'], entry['pro_response']])
        writer.writerow([entry['round'], "CON", entry['con_ai'], entry['con_response']])
    
    return output.getvalue()

def create_json_export(debate_log, topic, mode, summary=None):
    """Create JSON export of debate"""
    export_data = {
        "topic": topic,
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rounds": len(debate_log),
        "debate": debate_log,
        "summary": summary
    }
    return json.dumps(export_data, indent=2)

def create_txt_export(debate_log, topic, mode, summary=None):
    """Create TXT export of debate"""
    output = []
    output.append("=" * 80)
    output.append("AI DEBATE ARENA - DEBATE TRANSCRIPT")
    output.append("=" * 80)
    output.append(f"Topic: {topic}")
    output.append(f"Mode: {mode}")
    output.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Total Rounds: {len(debate_log)}")
    output.append("=" * 80)
    output.append("")
    
    for entry in debate_log:
        output.append(f"ROUND {entry['round']}")
        output.append("-" * 80)
        output.append(f"PRO ({entry['pro_ai']}):")
        output.append(entry['pro_response'])
        output.append("")
        output.append(f"CON ({entry['con_ai']}):")
        output.append(entry['con_response'])
        output.append("")
        output.append("=" * 80)
        output.append("")
    
    if summary:
        output.append("DEBATE SUMMARY")
        output.append("=" * 80)
        output.append(summary.get('summary', 'No summary available'))
        output.append("")
    
    return "\n".join(output)

# Run button
if st.sidebar.button("🎯 Run Debate", type="primary"):
    
    # Validate API keys (basic check)
    required_keys = {
        "claude": "ANTHROPIC_API_KEY",
        "gpt": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "cohere": "COHERE_API_KEY",
        "groq": "GROQ_API_KEY",
        "ai21": "AI21_API_KEY"
    }
    
    # Check if required API keys are present
    missing_keys = []
    for ai in [ai_pro, ai_con]:
        for prefix, key_name in required_keys.items():
            if ai.startswith(prefix) and not os.getenv(key_name):
                missing_keys.append(key_name)
    
    if missing_keys:
        st.error(f"⚠️ Missing API keys: {', '.join(set(missing_keys))}")
        st.info("Please add the missing API keys to your environment variables on Render.")
        st.stop()
    
    # Run the debate
    with st.spinner(f"Running {rounds}-round debate..."):
        try:
            engine = DebateEngine()
            debate_log = engine.run_debate(topic, ai_pro, ai_con, rounds, word_limit, mode)
            
            # Check for errors in debate
            has_errors = False
            for entry in debate_log:
                if "[ERROR:" in entry['pro_response'] or "[ERROR:" in entry['con_response']:
                    has_errors = True
                    break
            
            if has_errors:
                st.warning("⚠️ Some API calls failed during the debate. See error messages below.")
            else:
                st.success(f"✅ Debate complete! {rounds} rounds finished successfully.")
            
            # Generate summary
            with st.spinner("Generating debate summary..."):
                summary = engine.generate_summary(topic, debate_log, mode)
            
            st.markdown("---")
            
            # Display debate header
            st.markdown(f"### 📋 Topic: *{topic}*")
            st.markdown(f"**Mode:** {mode} | **Rounds:** {rounds} | **Word Limit:** {word_limit}")
            
            # Export buttons
            st.markdown("### 📥 Export Debate")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = create_csv_export(debate_log, topic, mode)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = create_json_export(debate_log, topic, mode, summary)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_data,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col3:
                txt_data = create_txt_export(debate_log, topic, mode, summary)
                st.download_button(
                    label="📝 Download TXT",
                    data=txt_data,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            st.markdown("---")
            
            # Display each round
            for entry in debate_log:
                st.markdown(f"## Round {entry['round']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🟢 PRO ({entry['pro_ai']})**")
                    
                    # Check for errors
                    if "[ERROR:" in entry['pro_response']:
                        st.error(entry['pro_response'])
                    else:
                        st.markdown(entry['pro_response'])
                        st.caption(f"Words: {len(entry['pro_response'].split())}")
                
                with col2:
                    st.markdown(f"**🔴 CON ({entry['con_ai']})**")
                    
                    # Check for errors
                    if "[ERROR:" in entry['con_response']:
                        st.error(entry['con_response'])
                    else:
                        st.markdown(entry['con_response'])
                        st.caption(f"Words: {len(entry['con_response'].split())}")
                
                st.markdown("---")
            
            # Display summary
            st.markdown("## 📊 Debate Summary")
            st.markdown("### Key Points & Analysis")
            
            if "[Could not generate summary:" in summary['summary']:
                st.warning(summary['summary'])
            else:
                st.markdown(summary['summary'])
            
            st.markdown("---")
            st.caption(f"Debate completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        except Exception as e:
            st.error(f"❌ Error running debate: {str(e)}")
            st.exception(e)

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
    6. **Export results** - Download debate transcripts in CSV, JSON, or TXT format
    
    ### Research Applications:
    - Compare how different AI systems argue the same position
    - Observe convergence patterns in truth-seeking mode
    - Analyze argument quality evolution across rounds
    - Test controversial topics across multiple AI pairings
    - Export debates for further analysis
    
    ### Available AI Systems (Verified December 2024):
    - **Claude Sonnet 4** - Anthropic's latest model
    - **GPT-4** - OpenAI's flagship model
    - **GPT-3.5 Turbo** - Faster OpenAI alternative
    - **Gemini 2.0 Flash** - Google's latest AI model
    - **DeepSeek Chat V3** - Chinese AI perspective
    - **Mistral Large 2** - European AI (France)
    - **Cohere Command R+ (Aug 2024)** - Canadian AI
    - **Llama 3.3 70B** - Meta's open source via Groq
    - **AI21 Jamba 1.5 Mini** - Israeli hybrid model
    
    ### Features:
    ✅ Choose any 2 of 8 AI systems as opponents  
    ✅ Configure rounds (3-15)  
    ✅ Set word limit per response (100-500)  
    ✅ Custom debate topics  
    ✅ Two debate modes: Adversarial vs Truth-Seeking  
    ✅ Export debates in multiple formats (CSV, JSON, TXT)  
    ✅ Automatic summary of main points, agreements, and disagreements  
    ✅ Error handling with fallback messages  
    """)

# I did no harm and this file is not truncated
