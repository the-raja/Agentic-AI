"""
Regime Agent for market context analysis.
Analyzes whether the market is trending (bull/bear) or ranging, and its volatility.
"""

import copy
import json

from langchain_core.messages import ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_regime_agent(llm, toolkit):
    """
    Create a market regime analysis agent node.
    The agent uses ADX and ATR tools to determine market context.
    """

    def regime_agent_node(state):
        # --- Tool definitions ---
        tools = [
            toolkit.compute_adx,
            toolkit.compute_atr,
        ]
        time_frame = state["time_frame"]
        
        # --- System prompt for LLM ---
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a specialized Market Regime Analyst. Your goal is to identify the current market context "
                    "to help other trading agents adjust their strategies.\\n\\n"
                    "You must determine:\\n"
                    "1. Trend Strength: Is the market trending or ranging? (Use ADX: >25 suggests a trend, <20 suggests ranging)\\n"
                    "2. Trend Direction: If trending, is it Bullish or Bearish?\\n"
                    "3. Volatility: Is volatility high, low, or increasing? (Use ATR and recent price action)\\n\\n"
                    "Base your analysis on the OHLC data and technical tools provided.\\n"
                    f"⚠️ Data Interval: {time_frame}\\n"
                    "OHLC Data:\\n{kline_data}\\n",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(kline_data=json.dumps(state["kline_data"], indent=2))

        chain = prompt | llm.bind_tools(tools)
        messages = state.get("messages", [])
        if not messages:
            messages = [HumanMessage(content="Start market regime analysis.")]

        # --- Step 1: Tool Calls ---
        ai_response = chain.invoke(messages)
        messages.append(ai_response)
        
        if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
            for call in ai_response.tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]
                tool_args["kline_data"] = copy.deepcopy(state["kline_data"])
                tool_fn = next(t for t in tools if t.name == tool_name)
                tool_result = tool_fn.invoke(tool_args)
                messages.append(
                    ToolMessage(
                        tool_call_id=call["id"], content=json.dumps(tool_result)
                    )
                )

        # --- Step 2: Final Reasoning ---
        max_iterations = 3
        iteration = 0
        final_response = None
        
        while iteration < max_iterations:
            iteration += 1
            final_response = chain.invoke(messages)
            messages.append(final_response)
            
            if not hasattr(final_response, "tool_calls") or not final_response.tool_calls:
                break
            
            for call in final_response.tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]
                tool_args["kline_data"] = copy.deepcopy(state["kline_data"])
                tool_fn = next(t for t in tools if t.name == tool_name)
                tool_result = tool_fn.invoke(tool_args)
                messages.append(
                    ToolMessage(
                        tool_call_id=call["id"], content=json.dumps(tool_result)
                    )
                )

        report_content = final_response.content if final_response else "Regime analysis completed."
        
        return {
            "messages": messages,
            "regime_report": report_content,
        }

    return regime_agent_node
