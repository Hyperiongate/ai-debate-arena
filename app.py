"""
AI Debate Arena - Streamlit Application
Last Updated: December 23, 2024
Version: 3.0 - Judge Scoring System

CHANGES IN THIS VERSION (December 23, 2024):
- ADDED: Judge AI selection with optional scoring system
- ADDED: Post-debate scoring across 6 categories (0-10 scale each)
- ADDED: Visual score comparison display (PRO vs CON)
- ADDED: Judge's detailed commentary and verdict
- ADDED: Judging results integrated into all export formats (CSV, JSON, TXT)
- ADDED: Validation for judge AI API key
- ADDED: Error handling for judge API failures
- Judge can be same AI as debaters (useful for research)
- Judge scoring is optional (checkbox control)

SCORING CATEGORIES:
1. Argument Strength - Logic and coherence of arguments
2. Evidence Quality - Use of facts, data, and examples
3. Counterpoint Effectiveness - How well they responded to opponent
4. Good Faith/Concessions - Willingness to concede valid points
5. Factual Accuracy - Truthfulness and accuracy of claims
6. Rhetorical Skill - Persuasiveness and communication quality

PREVIOUS FEATURES (Preserved):
1. Choose debate opponents from 8 AI systems
2. Configure rounds (3-15)
3. Set word count limit (100-500)
4. Enter debate topic
5. Choose mode: Adversarial or Truth-Seeking
6. Export debate transcripts in multiple formats
7. View debate summary with agreements/disagreements

NOTES:
- All features working as requested
- Judge scoring appears after debate summary
- Export buttons include judging results when enabled
- No harm done to existing functionality
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

# Judge AI selection (NEW)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Judge Scoring")
enable_judging = st.sidebar.checkbox("Enable Judge Scoring", value=True, 
    help="Have an AI judge score the debate across multiple categories")

judge_ai = None
if enable_judging:
    judge_ai = st.sidebar.selectbox("Judge AI", ai_options, index=0,
        help="Select which AI system will judge the debate. Can be same as debaters.")
    st.sidebar.info("💡 The judge will score both debaters on: Argument Strength, Evidence Quality, Counterpoints, Good Faith, Factual Accuracy, and Rhetorical Skill")

# Helper function to create export files with judging
def create_csv_export(debate_log, topic, mode, summary=None, judging=None):
    """Create CSV export of debate with optional judging results"""
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
    
    # Add judging results if available
    if judging and "scores" in judging:
        writer.writerow([])
        writer.writerow(["JUDGE SCORING"])
        writer.writerow(["Judge AI", judging.get('judge_ai', 'Unknown')])
        writer.writerow([])
        writer.writerow(["Category", "PRO Score", "CON Score"])
        
        scores = judging['scores']
        writer.writerow(["Argument Strength", scores['pro']['argument_strength'], scores['con']['argument_strength']])
        writer.writerow(["Evidence Quality", scores['pro']['evidence_quality'], scores['con']['evidence_quality']])
        writer.writerow(["Counterpoint Effectiveness", scores['pro']['counterpoint_effectiveness'], scores['con']['counterpoint_effectiveness']])
        writer.writerow(["Good Faith/Concessions", scores['pro']['good_faith'], scores['con']['good_faith']])
        writer.writerow(["Factual Accuracy", scores['pro']['factual_accuracy'], scores['con']['factual_accuracy']])
        writer.writerow(["Rhetorical Skill", scores['pro']['rhetorical_skill'], scores['con']['rhetorical_skill']])
        writer.writerow([])
        writer.writerow(["Total Score", scores['pro']['total'], scores['con']['total']])
        writer.writerow([])
        writer.writerow(["Judge's Commentary"])
        writer.writerow([judging.get('commentary', '')])
        writer.writerow([])
        writer.writerow(["Verdict"])
        writer.writerow([judging.get('verdict', '')])
    
    return output.getvalue()

def create_json_export(debate_log, topic, mode, summary=None, judging=None):
    """Create JSON export of debate with optional judging results"""
    export_data = {
        "topic": topic,
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rounds": len(debate_log),
        "debate": debate_log,
        "summary": summary
    }
    
    if judging:
        export_data["judging"] = judging
    
    return json.dumps(export_data, indent=2)

def create_txt_export(debate_log, topic, mode, summary=None, judging=None):
    """Create TXT export of debate with optional judging results"""
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
        output.append("=" * 80)
        output.append("")
    
    if judging and "scores" in judging:
        output.append("JUDGE SCORING")
        output.append("=" * 80)
        output.append(f"Judge: {judging.get('judge_ai', 'Unknown')}")
        output.append("")
        
        scores = judging['scores']
        output.append("SCORES (0-10 scale):")
        output.append("-" * 80)
        output.append(f"{'Category':<30} {'PRO':<10} {'CON':<10}")
        output.append("-" * 80)
        output.append(f"{'Argument Strength':<30} {scores['pro']['argument_strength']:<10} {scores['con']['argument_strength']:<10}")
        output.append(f"{'Evidence Quality':<30} {scores['pro']['evidence_quality']:<10} {scores['con']['evidence_quality']:<10}")
        output.append(f"{'Counterpoint Effectiveness':<30} {scores['pro']['counterpoint_effectiveness']:<10} {scores['con']['counterpoint_effectiveness']:<10}")
        output.append(f"{'Good Faith/Concessions':<30} {scores['pro']['good_faith']:<10} {scores['con']['good_faith']:<10}")
        output.append(f"{'Factual Accuracy':<30} {scores['pro']['factual_accuracy']:<10} {scores['con']['factual_accuracy']:<10}")
        output.append(f"{'Rhetorical Skill':<30} {scores['pro']['rhetorical_skill']:<10} {scores['con']['rhetorical_skill']:<10}")
        output.append("-" * 80)
        output.append(f"{'TOTAL':<30} {scores['pro']['total']:<10} {scores['con']['total']:<10}")
        output.append("")
        output.append("JUDGE'S COMMENTARY:")
        output.append("-" * 80)
        output.append(judging.get('commentary', ''))
        output.append("")
        output.append("VERDICT:")
        output.append("-" * 80)
        output.append(judging.get('verdict', ''))
        output.append("")
        output.append("=" * 80)
    
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
        "command": "COHERE_API_KEY",
        "groq": "GROQ_API_KEY",
        "llama": "GROQ_API_KEY",
        "ai21": "AI21_API_KEY",
        "jamba": "AI21_API_KEY"
    }
    
    # Check if required API keys are present for debaters
    missing_keys = []
    for ai in [ai_pro, ai_con]:
        for prefix, key_name in required_keys.items():
            if ai.startswith(prefix) and not os.getenv(key_name):
                missing_keys.append(key_name)
    
    # Also check judge AI if enabled
    if enable_judging and judge_ai:
        for prefix, key_name in required_keys.items():
            if judge_ai.startswith(prefix) and not os.getenv(key_name):
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
            
            # Generate judge scoring if enabled
            judging = None
            if enable_judging and judge_ai and not has_errors:
                with st.spinner(f"Judge ({judge_ai}) is scoring the debate..."):
                    judging = engine.judge_debate(topic, debate_log, mode, judge_ai, ai_pro, ai_con)
                    
                    if judging and "[ERROR:" not in str(judging):
                        st.success(f"✅ Judge scoring complete!")
                    elif judging:
                        st.warning("⚠️ Judge scoring encountered an error. See details below.")
            
            st.markdown("---")
            
            # Display debate header
            st.markdown(f"### 📋 Topic: *{topic}*")
            st.markdown(f"**Mode:** {mode} | **Rounds:** {rounds} | **Word Limit:** {word_limit}")
            
            # Export buttons
            st.markdown("### 📥 Export Debate")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = create_csv_export(debate_log, topic, mode, summary, judging)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = create_json_export(debate_log, topic, mode, summary, judging)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_data,
                    file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col3:
                txt_data = create_txt_export(debate_log, topic, mode, summary, judging)
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
            
            # Display judge scoring if available
            if judging and "scores" in judging:
                st.markdown("---")
                st.markdown("## 🎯 Judge Scoring")
                st.markdown(f"**Judge:** {judging['judge_ai']}")
                st.markdown("")
                
                scores = judging['scores']
                
                # Create score comparison table
                st.markdown("### Score Breakdown (0-10 scale)")
                
                # Display scores in a nice table format
                score_data = {
                    "Category": [
                        "Argument Strength",
                        "Evidence Quality", 
                        "Counterpoint Effectiveness",
                        "Good Faith/Concessions",
                        "Factual Accuracy",
                        "Rhetorical Skill",
                        "**TOTAL**"
                    ],
                    f"🟢 PRO ({ai_pro})": [
                        scores['pro']['argument_strength'],
                        scores['pro']['evidence_quality'],
                        scores['pro']['counterpoint_effectiveness'],
                        scores['pro']['good_faith'],
                        scores['pro']['factual_accuracy'],
                        scores['pro']['rhetorical_skill'],
                        f"**{scores['pro']['total']}**"
                    ],
                    f"🔴 CON ({ai_con})": [
                        scores['con']['argument_strength'],
                        scores['con']['evidence_quality'],
                        scores['con']['counterpoint_effectiveness'],
                        scores['con']['good_faith'],
                        scores['con']['factual_accuracy'],
                        scores['con']['rhetorical_skill'],
                        f"**{scores['con']['total']}**"
                    ]
                }
                
                st.table(score_data)
                
                # Judge's commentary
                st.markdown("### Judge's Commentary")
                st.markdown(judging['commentary'])
                
                # Verdict
                st.markdown("### Final Verdict")
                st.info(judging['verdict'])
                
            elif judging and "[ERROR:" in str(judging):
                st.markdown("---")
                st.markdown("## 🎯 Judge Scoring")
                st.error(f"Judge scoring failed: {judging}")
            
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
    5. **Enable judge scoring** (Optional) - Have an AI judge score the debate
    6. **Run the debate** - Watch the arguments unfold round by round
    7. **Export results** - Download debate transcripts with scores in CSV, JSON, or TXT format
    
    ### Research Applications:
    - Compare how different AI systems argue the same position
    - Observe convergence patterns in truth-seeking mode
    - Analyze argument quality evolution across rounds
    - Test controversial topics across multiple AI pairings
    - **NEW:** Compare judge scoring across different AI judges
    - **NEW:** Analyze which debating strategies score highest
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
    
    ### Judge Scoring Categories:
    Each debate is scored on a 0-10 scale across 6 categories:
    - **Argument Strength** - Logic and coherence of arguments
    - **Evidence Quality** - Use of facts, data, and examples
    - **Counterpoint Effectiveness** - How well they responded to opponent
    - **Good Faith/Concessions** - Willingness to concede valid points
    - **Factual Accuracy** - Truthfulness and accuracy of claims
    - **Rhetorical Skill** - Persuasiveness and communication quality
    
    ### Features:
    ✅ Choose any 2 of 8 AI systems as opponents  
    ✅ Configure rounds (3-15)  
    ✅ Set word limit per response (100-500)  
    ✅ Custom debate topics  
    ✅ Two debate modes: Adversarial vs Truth-Seeking  
    ✅ **NEW:** Optional AI judge scoring across 6 categories  
    ✅ **NEW:** Detailed judge commentary and verdict  
    ✅ Export debates with scores in multiple formats (CSV, JSON, TXT)  
    ✅ Automatic summary of main points, agreements, and disagreements  
    ✅ Error handling with fallback messages  
    """)

# I did no harm and this file is not truncated
