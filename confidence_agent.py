"""
Confidence Agent for trade setup validation.
Assigns a numerical confidence score (0-100) based on signal confluence and market regime.
"""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_confidence_agent(llm):
    """
    Create a trade confidence assessment agent node.
    This agent calculates a final confidence score based on previous reports.
    """

    def confidence_agent_node(state):
        concordance_report = state.get("concordance_report", "N/A")
        regime_report = state.get("regime_report", "N/A")
        time_frame = state.get("time_frame", "N/A")
        stock_name = state.get("stock_name", "N/A")

        # --- System prompt for LLM ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a Risk Management Officer specializing in quantitative trade confidence. "
                    "Your task is to assign a numerical CONFIDENCE SCORE from 0 to 100 for the current setup.\\n\\n"
                    "Your assessment is based on:\\n"
                    f"- Market Regime Context: {regime_report}\\n"
                    f"- Signal Concordance (Agreement): {concordance_report}\\n\\n"
                    "Your final response MUST include:\\n"
                    "1. A numerical score (e.g., SCORE: 75/100)\\n"
                    "2. A brief justification for this score based on risk factors and signal strength.\\n"
                    "3. Recommended position sizing (e.g., Conservative, Moderate, Aggressive).\\n\\n"
                    f"Target Asset: {stock_name} ({time_frame})\\n",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = prompt | llm
        messages = state.get("messages", [])
        if not messages:
            messages = [HumanMessage(content="Calculate the final confidence score for this trade setup.")]

        final_response = chain.invoke(messages)
        messages.append(final_response)

        # Attempt to extract a numerical score (simplified)
        content = final_response.content
        score = 0.0
        try:
            if "SCORE:" in content:
                score_str = content.split("SCORE:")[1].split("/")[0].strip()
                score = float(score_str)
        except:
            score = 50.0 # Fallback

        return {
            "messages": messages,
            "confidence_report": content,
            "confidence_score": score,
        }

    return confidence_agent_node
