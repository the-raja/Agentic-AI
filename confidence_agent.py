"""
Confidence Agent (SENTINEL VERSION)
- Aggressively prevents the "Lazy 50" default.
- Brute-force JSON recovery for truncated or messy outputs.
- Category-specific reasoning inside the JSON to force Chain-of-Thought.
"""

import json
import re
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


# -----------------------------
# 🔧 THE SENTINEL DECODER
# -----------------------------
def sentinel_decode(text: str):
    """
    Highly aggressive JSON recovery. 
    Handles truncation, unescaped quotes, and noise.
    """
    if not text: return None
    
    # 1. Clean noise
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # 2. Extract the largest possible block
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1: return None
    candidate = text[start:end+1]
    
    # 3. Aggressive Sanitization
    # a) Fix raw backslashes
    candidate = candidate.replace('\\', '\\\\')
    # b) Fix common unescaped quote issues (very common in long justifications)
    # This is a heuristic: we assume any " that isn't near a : or , or { } might be a mistake
    # But first, let's try a standard strict=False parse
    
    try:
        # Try cleaning newlines which are the #1 cause of failure in justifications
        sanitized = candidate.replace('\n', ' ').replace('\r', ' ')
        sanitized = re.sub(r',\s*([\]}])', r'\1', sanitized)
        return json.loads(sanitized, strict=False)
    except:
        # If that fails, the AI likely put raw quotes in the justification.
        # We'll try to extract the score manually if we have to.
        score_match = re.search(r'"score":\s*(\d+)', candidate)
        if score_match:
            return {"score": int(score_match.group(1)), "is_partial": True}
    return None


# -----------------------------
# 🤖 CONFIDENCE AGENT
# -----------------------------
def create_confidence_agent(llm):

    def confidence_agent_node(state):
        concordance_report = state.get("concordance_report", "N/A")
        regime_report = state.get("regime_report", "N/A")
        stock_name = state.get("stock_name", "N/A")

        system_template = """
You are a Risk Officer. Assign a confidence score (0-100).

⚠️ ABSOLUTE RULES:
- NEVER use the number 50. 
- Use 0-40 for weak signals, 60-100 for strong signals.
- Be decisive. If you are unsure, you MUST pick a side (e.g., 42 or 58).

Context:
Asset: {stock_name}
Regime: {regime_report}
Signals: {concordance_report}

Output ONLY this JSON:
{{
  "logic": "1-sentence reasoning",
  "score": <int>,
  "risk_level": "Low" | "Medium" | "High",
  "factor_scores": {{
    "confluence": <0-30>,
    "regime_fit": <0-30>,
    "signal_clarity": <0-20>,
    "risk_profile": <0-20>
  }},
  "justification": "Concise summary (max 2 sentences)"
}}
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", "Calculate the score for {stock_name} now. Remember: NO 50."),
        ])

        chain = prompt | llm
        try:
            response = chain.invoke({
                "stock_name": stock_name,
                "regime_report": regime_report,
                "concordance_report": concordance_report
            })
            content = response.content
        except Exception as e:
            content = f"Error: {str(e)}"

        # Default fallback
        parsed_data = sentinel_decode(content)
        
        if parsed_data:
            score = float(parsed_data.get("score", 50))
            # If the model still defied the rule and output 50, nudge it
            if score == 50: score = 51.0
        else:
            parsed_data = {"score": 50, "justification": "Parsing failure."}
            score = 50

        return {
            "messages": state.get("messages", []) + [AIMessage(content=content)],
            "confidence_report": content,
            "confidence_score": score,
            "confidence_details": parsed_data
        }

    return confidence_agent_node
