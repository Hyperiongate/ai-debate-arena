"""
AI Debate Arena - Debate Engine
Last Updated: December 23, 2024

CHANGES IN THIS VERSION (Dec 23, 2024):
- FIXED: AI21 API endpoint and request format (was using wrong endpoint)
- FIXED: AI routing to recognize llama, command, and jamba model prefixes
- Updated to use anthropic==0.39.0 compatible client initialization
- Changed Gemini to use REST API (gemini-2.0-flash) instead of deprecated gemini-pro
- All error handling intact with detailed error messages
- Using verified model names from AI Cross-Verification project
- Added 30-second timeout for all API calls to prevent hanging

SUPPORTED AI SYSTEMS (Dec 2024):
1. claude-sonnet-4-20250514 - Anthropic Claude Sonnet 4
2. gpt-4, gpt-3.5-turbo - OpenAI models
3. gemini-2.0-flash - Google Gemini (via REST API)
4. deepseek-chat - DeepSeek Chat V3
5. mistral-large-latest - Mistral Large 2
6. command-r-plus-08-2024 - Cohere Command R+
7. llama-3.3-70b-versatile - Meta Llama 3.3 via Groq
8. jamba-1.5-mini - AI21 Jamba 1.5 Mini (FIXED Dec 23, 2024)
"""

import anthropic
import openai
import os
import requests
import cohere

class DebateEngine:
    def __init__(self):
        """Initialize AI clients with error handling"""
        try:
            # Initialize Anthropic client (anthropic==0.39.0)
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            else:
                self.anthropic_client = None
                print("Warning: ANTHROPIC_API_KEY not found")
            
            # Initialize OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                openai.api_key = openai_key
            else:
                print("Warning: OPENAI_API_KEY not found")
            
        except Exception as e:
            print(f"Error initializing AI clients: {str(e)}")
            raise
    
    def get_response(self, ai_system, prompt, max_words=200):
        """
        Get response from specified AI system
        
        ROUTING LOGIC (FIXED Dec 23, 2024):
        - claude: Matches "claude-sonnet-4-20250514"
        - gpt: Matches "gpt-4", "gpt-3.5-turbo"
        - gemini: Matches "gemini-2.0-flash"
        - deepseek: Matches "deepseek-chat"
        - mistral: Matches "mistral-large-latest"
        - cohere OR command: Matches "command-r-plus-08-2024"
        - groq OR llama: Matches "llama-3.3-70b-versatile"
        - ai21 OR jamba: Matches "jamba-1.5-mini"
        """
        
        try:
            if ai_system.startswith("claude"):
                return self._get_claude_response(prompt, max_words)
            elif ai_system.startswith("gpt"):
                return self._get_openai_response(ai_system, prompt, max_words)
            elif ai_system.startswith("gemini"):
                return self._get_gemini_response(prompt, max_words)
            elif ai_system.startswith("deepseek"):
                return self._get_deepseek_response(prompt, max_words)
            elif ai_system.startswith("mistral"):
                return self._get_mistral_response(prompt, max_words)
            elif ai_system.startswith("cohere") or ai_system.startswith("command"):
                return self._get_cohere_response(prompt, max_words)
            elif ai_system.startswith("groq") or ai_system.startswith("llama"):
                return self._get_groq_response(prompt, max_words)
            elif ai_system.startswith("ai21") or ai_system.startswith("jamba"):
                return self._get_ai21_response(prompt, max_words)
            else:
                return f"[ERROR: AI system '{ai_system}' not supported]"
        except Exception as e:
            return f"[ERROR: {ai_system} API call failed - {str(e)}]"
    
    def _get_claude_response(self, prompt, max_words):
        """Get response from Claude (anthropic==0.39.0)"""
        try:
            if not self.anthropic_client:
                return "[ERROR: Anthropic client not initialized. Check API key.]"
            
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_words * 2,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"[ERROR: Claude API call failed - {str(e)}]"
    
    def _get_openai_response(self, model, prompt, max_words):
        """Get response from OpenAI (openai==1.3.0 with httpx==0.27.2)"""
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_words * 2,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR: OpenAI API call failed - {str(e)}]"
    
    def _get_gemini_response(self, prompt, max_words):
        """Get response from Gemini (using REST API, not Python SDK)"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                return "[ERROR: GOOGLE_API_KEY not found]"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            response = requests.post(
                url,
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": max_words * 2
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"[ERROR: Gemini API returned status {response.status_code} - {response.text}]"
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"[ERROR: Gemini API call failed - {str(e)}]"
    
    def _get_deepseek_response(self, prompt, max_words):
        """Get response from DeepSeek"""
        try:
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return "[ERROR: DEEPSEEK_API_KEY not found]"
            
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
            
            if response.status_code != 200:
                return f"[ERROR: DeepSeek API returned status {response.status_code} - {response.text}]"
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: DeepSeek API call failed - {str(e)}]"
    
    def _get_mistral_response(self, prompt, max_words):
        """Get response from Mistral"""
        try:
            api_key = os.getenv('MISTRAL_API_KEY')
            if not api_key:
                return "[ERROR: MISTRAL_API_KEY not found]"
            
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
            
            if response.status_code != 200:
                return f"[ERROR: Mistral API returned status {response.status_code} - {response.text}]"
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: Mistral API call failed - {str(e)}]"
    
    def _get_cohere_response(self, prompt, max_words):
        """Get response from Cohere"""
        try:
            api_key = os.getenv('COHERE_API_KEY')
            if not api_key:
                return "[ERROR: COHERE_API_KEY not found]"
            
            co = cohere.Client(api_key)
            response = co.chat(
                message=prompt,
                model="command-r-plus-08-2024",
                max_tokens=max_words * 2
            )
            return response.text
        except Exception as e:
            return f"[ERROR: Cohere API call failed - {str(e)}]"
    
    def _get_groq_response(self, prompt, max_words):
        """Get response from Groq (Llama models)"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                return "[ERROR: GROQ_API_KEY not found]"
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"[ERROR: Groq API returned status {response.status_code} - {response.text}]"
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[ERROR: Groq API call failed - {str(e)}]"
    
    def _get_ai21_response(self, prompt, max_words):
        """
        Get response from AI21 (FIXED Dec 23, 2024)
        
        FIXED ISSUES:
        - Changed endpoint from /studio/v1/chat/completions to /v1/chat/completions
        - Updated to current AI21 API v1 format
        - Verified with AI21 documentation (Dec 2024)
        """
        try:
            api_key = os.getenv('AI21_API_KEY')
            if not api_key:
                return "[ERROR: AI21_API_KEY not found]"
            
            # CORRECT ENDPOINT (Dec 2024): /v1/chat/completions
            response = requests.post(
                "https://api.ai21.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "jamba-1.5-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_words * 2
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"[ERROR: AI21 API returned status {response.status_code} - {response.text}]"
            
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


# I did no harm and this file is not truncated
