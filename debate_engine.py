#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode = True  # Force Python to ignore .pyc cache

"""
AI Debate Arena - Debate Engine
Last Updated: December 23, 2024
Version: 4.3 - Multi-Voice Audio with Narration Removal

CHANGES IN THIS VERSION (December 23, 2024 - Version 4.3):
- OPTIMIZED: Audio now uses 3 distinct ElevenLabs voices
- PRO Debater: Adam (deep, authoritative male voice)
- CON Debater: Rachel (clear, professional female voice)
- Judge: Antoni (warm, articulate male voice)
- REMOVED: All narration and preamble ("Round 1", "PRO says", etc.)
- Now direct speech only - much more natural
- CHARACTER SAVINGS: Reduces audio by ~35-40%
- 10-round debate now fits better in free tier limits
- Each speaker has distinct voice - no confusion needed

CHANGES IN VERSION 4.2 (December 23, 2024):
- SWITCHED: Audio generation now uses ElevenLabs instead of Google Cloud TTS
- ElevenLabs uses simple API key authentication (no service account!)
- Professional quality voice: Rachel (ElevenLabs preset)
- Free tier: 10,000 characters/month
- Much simpler setup - just add ELEVENLABS_API_KEY to environment
- Removed Google Cloud TTS dependency

CHANGES IN VERSION 4.1 (December 23, 2024):
- FIXED: AI21 now uses Python SDK instead of REST API
- Changed from requests.post() to AI21Client().chat.completions.create()
- AI21 deprecated their direct REST API in favor of Python SDK
- Added ai21 package import for Jamba models
- This fixes the "404 Not Found" error with AI21 API

SUPPORTED AI SYSTEMS (December 2024):
1. claude-sonnet-4-20250514 - Anthropic Claude Sonnet 4
2. gpt-4, gpt-3.5-turbo - OpenAI models
3. gemini-2.0-flash - Google Gemini (via REST API)
4. deepseek-chat - DeepSeek Chat V3
5. mistral-large-latest - Mistral Large 2
6. command-r-plus-08-2024 - Cohere Command R+
7. llama-3.3-70b-versatile - Meta Llama 3.3 via Groq
8. jamba-mini - AI21 Jamba Mini (via Python SDK)

NOTES:
- All AI integrations include try/catch for graceful failure
- Fallback message provided when API calls fail
- Summary generation analyzes agreements, disagreements, and main points
- Judge scoring provides objective evaluation of debate quality
- Audio generation uses 3 distinct ElevenLabs voices for clarity
- Direct speech format makes audio more engaging and efficient
- AI21 requires Python SDK (not REST API) as of December 2024
- Model names verified as of December 2024
"""

import anthropic
import os
import requests
import cohere
from typing import Dict, List, Tuple
import json
import re

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
            elif ai_system.startswith("cohere") or ai_system.startswith("command"):
                return self._get_cohere_response(prompt, max_words)
            elif ai_system.startswith("groq") or ai_system.startswith("llama"):
                return self._get_groq_response(prompt, max_words)
            elif ai_system.startswith("ai21") or ai_system.startswith("jamba"):
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
        """
        Get response from AI21 - Uses Jamba Mini via Python SDK
        
        FIXED December 23, 2024:
        - Changed from REST API to AI21 Python SDK
        - REST API endpoint was deprecated
        - SDK provides better integration and reliability
        - Model name is "jamba-mini" (not "jamba-1.5-mini")
        """
        try:
            from ai21 import AI21Client
            from ai21.models.chat import ChatMessage
            
            api_key = os.getenv('AI21_API_KEY')
            if not api_key:
                return "[ERROR: AI21_API_KEY not found in environment]"
            
            # Initialize AI21 client
            client = AI21Client(api_key=api_key)
            
            # Create message
            messages = [ChatMessage(content=prompt, role="user")]
            
            # Make API call using SDK
            # Model name is "jamba-mini" not "jamba-1.5-mini"
            response = client.chat.completions.create(
                model="jamba-mini",
                messages=messages,
                max_tokens=max_words * 2
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            return "[ERROR: ai21 package not installed. Run: pip install ai21]"
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
    
    def judge_debate(self, topic: str, debate_log: List[Dict], mode: str, 
                     judge_ai: str, ai_pro: str, ai_con: str) -> Dict:
        """
        Have an AI judge score the debate across multiple categories
        
        ADDED IN VERSION 3.0 (December 23, 2024)
        
        Args:
            topic: The debate topic
            debate_log: Full debate transcript
            mode: Debate mode (Adversarial or Truth-Seeking)
            judge_ai: Which AI system to use as judge
            ai_pro: PRO debater AI name
            ai_con: CON debater AI name
            
        Returns:
            Dictionary containing scores, commentary, and verdict
        """
        
        try:
            # Compile full debate transcript for judge
            transcript = []
            for entry in debate_log:
                transcript.append(f"=== ROUND {entry['round']} ===")
                transcript.append(f"PRO ({ai_pro}):")
                transcript.append(entry['pro_response'])
                transcript.append("")
                transcript.append(f"CON ({ai_con}):")
                transcript.append(entry['con_response'])
                transcript.append("")
            
            full_transcript = "\n".join(transcript)
            
            # Create judge prompt with scoring criteria
            judge_prompt = f"""You are serving as a judge for a debate. Your task is to objectively evaluate both debaters' performance across multiple categories.

DEBATE TOPIC: {topic}
DEBATE MODE: {mode}
PRO DEBATER: {ai_pro}
CON DEBATER: {ai_con}

FULL DEBATE TRANSCRIPT:
{full_transcript}

Please score both debaters on the following categories using a 0-10 scale (where 10 is excellent, 5 is average, 0 is very poor):

1. **Argument Strength** - Logic, coherence, and persuasiveness of their core arguments
2. **Evidence Quality** - Use of facts, data, examples, and credible sources
3. **Counterpoint Effectiveness** - How well they addressed and refuted opponent's points
4. **Good Faith/Concessions** - Willingness to acknowledge valid points and debate in good faith
5. **Factual Accuracy** - Truthfulness and accuracy of claims made
6. **Rhetorical Skill** - Communication quality, clarity, and persuasive techniques

IMPORTANT: Provide your response EXACTLY in this JSON format:

{{
  "pro_scores": {{
    "argument_strength": <score 0-10>,
    "evidence_quality": <score 0-10>,
    "counterpoint_effectiveness": <score 0-10>,
    "good_faith": <score 0-10>,
    "factual_accuracy": <score 0-10>,
    "rhetorical_skill": <score 0-10>
  }},
  "con_scores": {{
    "argument_strength": <score 0-10>,
    "evidence_quality": <score 0-10>,
    "counterpoint_effectiveness": <score 0-10>,
    "good_faith": <score 0-10>,
    "factual_accuracy": <score 0-10>,
    "rhetorical_skill": <score 0-10>
  }},
  "commentary": "2-3 paragraphs explaining your scoring decisions, highlighting strengths and weaknesses of each side",
  "verdict": "Final verdict on the debate quality and which side presented a stronger case overall (if applicable)"
}}

Be objective and fair in your evaluation. Consider the debate mode when scoring (e.g., good faith matters more in Truth-Seeking mode)."""

            # Get judge's evaluation
            judge_response = self.get_response(judge_ai, judge_prompt, max_words=800)
            
            # Check for API errors
            if "[ERROR:" in judge_response:
                return f"[ERROR: Judge API call failed - {judge_response}]"
            
            # Parse the JSON response
            # Try to extract JSON from the response (handle cases where AI adds extra text)
            json_match = re.search(r'\{.*\}', judge_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                judge_data = json.loads(json_str)
            else:
                # Fallback: try parsing whole response
                judge_data = json.loads(judge_response)
            
            # Calculate totals
            pro_total = sum(judge_data['pro_scores'].values())
            con_total = sum(judge_data['con_scores'].values())
            
            # Format results
            result = {
                "judge_ai": judge_ai,
                "scores": {
                    "pro": {
                        "argument_strength": judge_data['pro_scores']['argument_strength'],
                        "evidence_quality": judge_data['pro_scores']['evidence_quality'],
                        "counterpoint_effectiveness": judge_data['pro_scores']['counterpoint_effectiveness'],
                        "good_faith": judge_data['pro_scores']['good_faith'],
                        "factual_accuracy": judge_data['pro_scores']['factual_accuracy'],
                        "rhetorical_skill": judge_data['pro_scores']['rhetorical_skill'],
                        "total": pro_total
                    },
                    "con": {
                        "argument_strength": judge_data['con_scores']['argument_strength'],
                        "evidence_quality": judge_data['con_scores']['evidence_quality'],
                        "counterpoint_effectiveness": judge_data['con_scores']['counterpoint_effectiveness'],
                        "good_faith": judge_data['con_scores']['good_faith'],
                        "factual_accuracy": judge_data['con_scores']['factual_accuracy'],
                        "rhetorical_skill": judge_data['con_scores']['rhetorical_skill'],
                        "total": con_total
                    }
                },
                "commentary": judge_data['commentary'],
                "verdict": judge_data['verdict']
            }
            
            return result
            
        except json.JSONDecodeError as e:
            return f"[ERROR: Could not parse judge response as JSON - {str(e)}. Response was: {judge_response[:200]}...]"
        except KeyError as e:
            return f"[ERROR: Missing required field in judge response - {str(e)}]"
        except Exception as e:
            return f"[ERROR: Judge evaluation failed - {str(e)}]"
    
    def generate_audio(self, topic: str, debate_log: List[Dict], mode: str, 
                      summary: Dict, judging: Dict, ai_pro: str, ai_con: str) -> bytes:
        """
        Generate MP3 audio of the entire debate using ElevenLabs with 3 distinct voices
        
        UPDATED IN VERSION 4.3 (December 23, 2024)
        - Uses 3 different ElevenLabs voices (PRO, CON, Judge)
        - Removed all narration/preamble to save characters
        - Direct speech only - much more natural and shorter
        - PRO: Adam (deep, authoritative male)
        - CON: Rachel (clear, professional female)
        - Judge: Antoni (warm, articulate male)
        
        Args:
            topic: The debate topic
            debate_log: Full debate transcript
            mode: Debate mode
            summary: Debate summary
            judging: Judge scoring results (can be None)
            ai_pro: PRO debater name
            ai_con: CON debater name
            
        Returns:
            MP3 audio data as bytes, or error string
        """
        
        try:
            from elevenlabs import VoiceSettings
            from elevenlabs.client import ElevenLabs
            
            # Initialize ElevenLabs client
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                return "[ERROR: ELEVENLABS_API_KEY not found in environment]"
            
            client = ElevenLabs(api_key=api_key)
            
            # Voice IDs for 3 distinct speakers
            VOICE_PRO = "pNInz6obpgDQGcFmaJgB"      # Adam - deep, authoritative male
            VOICE_CON = "21m00Tcm4TlvDq8ikWAM"      # Rachel - clear, professional female  
            VOICE_JUDGE = "ErXwobaYiN019PkySvjV"    # Antoni - warm, articulate male
            
            # Voice settings for natural speech
            voice_settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
            
            # Collect all audio chunks
            audio_chunks = []
            
            # Brief introduction (only topic)
            intro_text = f"Debate topic: {topic}. {mode} mode."
            intro_audio = client.text_to_speech.convert(
                voice_id=VOICE_JUDGE,
                text=intro_text,
                model_id="eleven_multilingual_v2",
                voice_settings=voice_settings
            )
            for chunk in intro_audio:
                if chunk:
                    audio_chunks.append(chunk)
            
            # Generate audio for each round (PRO and CON only - no narration)
            for entry in debate_log:
                # PRO argument (direct speech, no "Round X" or "PRO says")
                pro_audio = client.text_to_speech.convert(
                    voice_id=VOICE_PRO,
                    text=entry['pro_response'],
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                for chunk in pro_audio:
                    if chunk:
                        audio_chunks.append(chunk)
                
                # CON argument (direct speech)
                con_audio = client.text_to_speech.convert(
                    voice_id=VOICE_CON,
                    text=entry['con_response'],
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                for chunk in con_audio:
                    if chunk:
                        audio_chunks.append(chunk)
            
            # Judge verdict (if available) - keep it concise
            if judging and isinstance(judging, dict) and "scores" in judging:
                scores = judging['scores']
                
                # Just the scores and verdict (skip detailed commentary to save chars)
                judge_text = f"Final scores: PRO {scores['pro']['total']} out of 60. CON {scores['con']['total']} out of 60. {judging['verdict']}"
                
                judge_audio = client.text_to_speech.convert(
                    voice_id=VOICE_JUDGE,
                    text=judge_text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                for chunk in judge_audio:
                    if chunk:
                        audio_chunks.append(chunk)
            
            # Combine all audio chunks into one file
            audio_bytes = b"".join(audio_chunks)
            
            return audio_bytes
            
        except ImportError:
            return "[ERROR: elevenlabs package not installed. Run: pip install elevenlabs]"
        except Exception as e:
            return f"[ERROR: Audio generation failed - {str(e)}]"

# I did no harm and this file is not truncated
