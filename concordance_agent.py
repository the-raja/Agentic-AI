"""
Concordance Agent for signal confluence analysis.
Cross-checks reports from Regime, Indicator, Pattern, and Trend agents to find alignment.
"""

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_concordance_agent(llm):
    """
    Create a signal concordance agent node.
    This agent synthesizes results from all analyst agents to find confluence.
    """

    def concordance_agent_node(state):
        regime_report = state.get("regime_report", "N/A")
        indicator_report = state.get("indicator_report", "N/A")
        pattern_report = state.get("pattern_report", "N/A")
        trend_report = state.get("trend_report", "N/A")
        time_frame = state.get("time_frame", "N/A")
        stock_name = state.get("stock_name", "N/A")

        # --- System prompt for LLM ---
        system_msg = (
            "You are a Senior Trading Strategist specializing in Signal Confluence (Concordance). "
            "Your task is to review reports from multiple specialized analysts and determine if their signals "
            "are in alignment (Concordance) or in conflict.\n\n"
            "Analysts provided the following reports:\n"
            "1. MARKET REGIME: {regime_report}\n"
            "2. TECHNICAL INDICATORS: {indicator_report}\n"
            "3. PATTERN RECOGNITION: {pattern_report}\n"
            "4. TREND ANALYSIS: {trend_report}\n\n"
            "Your assessment must cover:\n"
            "- Alignment: Are the signals (Regime, Indicators, Patterns, Trend) pointing in the same direction?\n"
            "- Conflicts: Identify any contradictory signals (e.g., Bullish Pattern vs. Bearish Regime).\n"
            "- Strength of Confluence: Rate the overall agreement (e.g., Weak, Moderate, Strong).\n"
            "- Key Drivers: What are the primary factors driving the current consensus or lack thereof?\n\n"
            "Target Asset: {stock_name} ({time_frame})\n"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_msg),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(
            regime_report=regime_report,
            indicator_report=indicator_report,
            pattern_report=pattern_report,
            trend_report=trend_report,
            stock_name=stock_name,
            time_frame=time_frame
        )

        chain = prompt | llm
        messages = state.get("messages", [])
        if not messages:
            messages = [HumanMessage(content="Synthesize all analyst reports for signal concordance.")]

        # Concordance Agent is a reasoning agent, no tools needed for now
        final_response = chain.invoke({"messages": messages})
        messages.append(final_response)

        return {
            "messages": messages,
            "concordance_report": final_response.content,
        }

    return concordance_agent_node
