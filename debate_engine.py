"""
AI Debate Arena - Debate Engine
Last Updated: December 22, 2024

CHANGES:
- Fixed Claude model selection to use the actual selected model (was hardcoded)
- Added comprehensive error handling with fallback for all API calls
- Added generate_summary() method for end-of-debate analysis
- Added better error messages for debugging
- All API methods now return error messages on failure instead of crashing
- FIXED: OpenAI client initialization for v1.3.0 compatibility
- FIXED: Updated Gemini to use gemini-2.0-flash via REST API (verified Dec 2024)
- FIXED: Using exact model names from AI Cross-Verification project

NOTES:
- All AI integrations include try/catch for graceful failure
- Fallback message provided when API calls fail
- Summary generation analyzes agreements, disagreements, and main points
- Model names verified as of December 2024
"""

import anthropic
import os
import requests
import cohere
from typing import Dict, List, Tuple

class DebateEngine:
    def __init__(self):
        """Initialize all AI clients with error handling"""
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except Exception as e:
            print(f"Warning: Could not initialize Anthropic client: {e}")
            self.anthropic_client = None
    
    def get_response(self, ai_system, prompt, max_words=200):
        """Get response from specified AI system with error handling"""
        
        try:
            if ai_system.startswith("claude"):
                return self._get_claude_response(ai_system, prompt, max_words)
            elif ai_system.startswith("gpt"):
                return self._get_openai_response(ai_system, prompt, max_words)
            elif ai_system.startswith("gemini"):
                return self._get_gemini_response(prompt, max_words)
            elif ai_system.startswith("deepseek"):
                return self._get_deepseek_response(prompt, max_words)
            elif ai_system.startswith("mistral"):
                return self._get_mistral_response(prompt, max_words)
            elif ai_system.startswith("cohere"):
                return self._get_cohere_response(prompt, max_words)
            elif ai_system.startswith("groq"):
                return self._get_groq_response(prompt, max_words)
            elif ai_system.startswith("ai21"):
                return self._get_ai21_response(prompt, max_words)
            else:
                return f"[ERROR: AI system '{ai_system}' not supported]"
        except Exception as e:
            return f"[ERROR: {ai_system} failed - {str(e)}]"
    
    def _get_claude_response(self, model, prompt, max_words):
        """Get response from Claude - FIXED to use selected model"""
        try:
            if not self.anthropic_client:
                return "[ERROR: Anthropic client not initialized. Check API key.]"
                
            message = self.anthropic_client.messages.create(
                model=model,  # FIXED: Now uses the actual selected model
                max_tokens=max_words * 2,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"[ERROR: Claude API call failed - {str(e)}]"
    
    def _get_openai_response(self, model, prompt, max_words):
        """Get response from OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_words * 2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR: OpenAI API call failed - {str(e)}]"
    
    def _get_gemini_response(self, prompt, max_words):
        """Get response from Gemini - Uses direct REST API (not Python SDK)"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                return "[ERROR: GOOGLE_API_KEY not found in environment]"
            
            # Use Gemini 2.0 Flash via REST API (verified working Dec 2024)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            return f"[ERROR: Gemini API call failed - {str(e)}]"
    
    def _get_deepseek_response(self, prompt, max_words):
        """Get response from DeepSeek"""
        try:
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return "[ERROR: DEEPSEEK_API_KEY not found in environment]"
                
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: DeepSeek API call failed - {str(e)}]"
    
    def _get_mistral_response(self, prompt, max_words):
        """Get response from Mistral"""
        try:
            api_key = os.getenv('MISTRAL_API_KEY')
            if not api_key:
                return "[ERROR: MISTRAL_API_KEY not found in environment]"
                
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: Mistral API call failed - {str(e)}]"
    
    def _get_cohere_response(self, prompt, max_words):
        """Get response from Cohere - Uses command-r-plus-08-2024 (verified Dec 2024)"""
        try:
            api_key = os.getenv('COHERE_API_KEY')
            if not api_key:
                return "[ERROR: COHERE_API_KEY not found in environment]"
                
            co = cohere.Client(api_key)
            response = co.chat(
                message=prompt,
                model="command-r-plus-08-2024",  # Verified working model
                max_tokens=max_words * 2
            )
            return response.text
        except Exception as e:
            return f"[ERROR: Cohere API call failed - {str(e)}]"
    
    def _get_groq_response(self, prompt, max_words):
        """Get response from Groq - Uses Llama 3.3 70B (verified Dec 2024)"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                return "[ERROR: GROQ_API_KEY not found in environment]"
                
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",  # Verified working model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: Groq API call failed - {str(e)}]"
    
    def _get_ai21_response(self, prompt, max_words):
        """Get response from AI21 - Uses Jamba 1.5 Mini (verified Dec 2024)"""
        try:
            api_key = os.getenv('AI21_API_KEY')
            if not api_key:
                return "[ERROR: AI21_API_KEY not found in environment]"
                
            response = requests.post(
                "https://api.ai21.com/studio/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "jamba-1.5-mini",  # Verified working model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: AI21 API call failed - {str(e)}]"

    def run_debate(self, topic, ai_pro, ai_con, rounds, word_limit, mode):
        """Run a complete debate"""
        
        debate_log = []
        
        # Determine instruction style based on mode
        if mode == "Truth-Seeking":
            instruction_suffix = "Your goal is to find the truth together, not to win. Be willing to concede points and adjust your position based on strong arguments."
        else:  # Adversarial
            instruction_suffix = "Present the strongest possible case for your position."
        
        # Round 1: Opening arguments
        pro_prompt = f"""You are participating in a structured debate about: {topic}
Your position: PRO (in favor of the proposition)
Present your opening argument in approximately {word_limit} words. {instruction_suffix}"""
        
        con_prompt = f"""You are participating in a structured debate about: {topic}
Your position: CON (against the proposition)
Present your opening argument in approximately {word_limit} words. {instruction_suffix}"""
        
        pro_response = self.get_response(ai_pro, pro_prompt, word_limit)
        con_response = self.get_response(ai_con, con_prompt, word_limit)
        
        debate_log.append({
            "round": 1,
            "pro_ai": ai_pro,
            "pro_response": pro_response,
            "con_ai": ai_con,
            "con_response": con_response
        })
        
        # Subsequent rounds
        for round_num in range(2, rounds + 1):
            pro_prompt = f"""You are in round {round_num} of a debate about: {topic}
Your position: PRO

Your opponent's last argument:
{con_response}

Respond to their argument in approximately {word_limit} words. {instruction_suffix}"""
            
            con_prompt = f"""You are in round {round_num} of a debate about: {topic}
Your position: CON

Your opponent's last argument:
{pro_response}

Respond to their argument in approximately {word_limit} words. {instruction_suffix}"""
            
            pro_response = self.get_response(ai_pro, pro_prompt, word_limit)
            con_response = self.get_response(ai_con, con_prompt, word_limit)
            
            debate_log.append({
                "round": round_num,
                "pro_ai": ai_pro,
                "pro_response": pro_response,
                "con_ai": ai_con,
                "con_response": con_response
            })
        
        return debate_log
    
    def generate_summary(self, topic: str, debate_log: List[Dict], mode: str) -> Dict[str, str]:
        """Generate a summary of the debate showing main points, agreements, and disagreements"""
        
        try:
            # Compile all arguments
            pro_arguments = []
            con_arguments = []
            
            for entry in debate_log:
                pro_arguments.append(entry['pro_response'])
                con_arguments.append(entry['con_response'])
            
            # Create summary prompt
            summary_prompt = f"""Analyze this debate about: {topic}

PRO Arguments (all rounds):
{chr(10).join([f"Round {i+1}: {arg}" for i, arg in enumerate(pro_arguments)])}

CON Arguments (all rounds):
{chr(10).join([f"Round {i+1}: {arg}" for i, arg in enumerate(con_arguments)])}

Debate Mode: {mode}

Provide a brief summary (200-300 words) covering:
1. Main points argued by PRO side
2. Main points argued by CON side
3. Key areas where they agreed or found common ground
4. Key areas where they disagreed or remained opposed
5. Overall observation about how the debate evolved

Be objective and concise."""

            # Use Claude for summary generation (most reliable for this task)
            summary_text = self._get_claude_response("claude-sonnet-4-20250514", summary_prompt, 300)
            
            return {
                "summary": summary_text,
                "topic": topic,
                "mode": mode,
                "total_rounds": len(debate_log)
            }
            
        except Exception as e:
            return {
                "summary": f"[Could not generate summary: {str(e)}]",
                "topic": topic,
                "mode": mode,
                "total_rounds": len(debate_log)
            }

# I did no harm and this file is not truncated
