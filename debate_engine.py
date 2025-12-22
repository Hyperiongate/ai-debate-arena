import anthropic
import openai
from google import generativeai as genai
import os

class DebateEngine:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        openai.api_key = os.getenv("OPENAI_API_KEY")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    def get_response(self, ai_system, prompt, max_words=200):
        """Get response from specified AI system"""
        
        if ai_system.startswith("claude"):
            return self._get_claude_response(prompt, max_words)
        elif ai_system.startswith("gpt"):
            return self._get_openai_response(ai_system, prompt, max_words)
        elif ai_system.startswith("gemini"):
            return self._get_gemini_response(prompt, max_words)
        else:
            return "AI system not supported"
    
    def _get_claude_response(self, prompt, max_words):
        """Get response from Claude"""
        message = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_words * 2,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _get_openai_response(self, model, prompt, max_words):
        """Get response from OpenAI"""
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_words * 2
        )
        return response.choices[0].message.content
    
    def _get_gemini_response(self, prompt, max_words):
        """Get response from Gemini"""
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text

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
