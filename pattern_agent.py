import copy
import json
import time

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai import RateLimitError


def invoke_tool_with_retry(tool_fn, tool_args, retries=3, wait_sec=4):
    """
    Invoke a tool function with retries if the result is missing an image.
    """
    for attempt in range(retries):
        result = tool_fn.invoke(tool_args)
        img_b64 = result.get("pattern_image")
        if img_b64:
            return result
        print(
            f"Tool returned no image, retrying in {wait_sec}s (attempt {attempt + 1}/{retries})..."
        )
        time.sleep(wait_sec)
    raise RuntimeError("Tool failed to generate image after multiple retries")


def create_pattern_agent(tool_llm, graph_llm, toolkit):
    """
    Create a pattern recognition agent node for candlestick pattern analysis.
    The agent uses precomputed images from state or falls back to tool generation.
    """

    def pattern_agent_node(state):
        # --- Tool and pattern definitions ---
        tools = [toolkit.generate_kline_image]
        time_frame = state["time_frame"]
        pattern_text = """
        Please refer to the following common candlestick patterns:
        1. Bull Flag: Sharp rise followed by narrow consolidation.
        2. Bear Flag: Sharp drop followed by narrow consolidation.
        3. Double Bottom/Top: Two similar lows/highs.
        4. Head and Shoulders: Three peaks/troughs with a higher/lower middle.
        5. Triangles (Ascending/Descending/Symmetrical): Converging support/resistance.
        6. Wedges (Falling/Rising): Converging lines with a directional slope.
        """

        # --- Check for precomputed image in state ---
        pattern_image_b64 = state.get("pattern_image")

        # --- Retry wrapper for LLM invocation ---
        def invoke_with_retry(call_fn, *args, retries=3, wait_sec=8):
            for attempt in range(retries):
                try:
                    return call_fn(*args)
                except RateLimitError:
                    print(
                        f"Rate limit hit, retrying in {wait_sec}s (attempt {attempt + 1}/{retries})..."
                    )
                    time.sleep(wait_sec)
                except Exception as e:
                    print(
                        f"Other error: {e}, retrying in {wait_sec}s (attempt {attempt + 1}/{retries})..."
                    )
                    time.sleep(wait_sec)
            raise RuntimeError("Max retries exceeded")

        messages = state.get("messages", [])

        # --- If no precomputed image, fall back to tool generation ---
        if not pattern_image_b64:
            print(
                "No precomputed pattern image found in state, generating with tool..."
            )

            # --- System prompt setup for tool generation ---
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a trading pattern recognition assistant tasked with identifying classical high-frequency trading patterns. "
                        "You have access to tool: generate_kline_image. "
                        "Use it by providing appropriate arguments like `kline_data`\\n\\n"
                        "Once the chart is generated, compare it to classical pattern descriptions and determine if any known pattern is present.",
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            ).partial(kline_data=json.dumps(state["kline_data"], indent=2))

            # Only bind tools if provider is NOT ollama (or if we really need to)
            # But here we already checked if pattern_image_b64 is missing.
            # If it's missing AND it's ollama, we might have an issue, 
            # but web_interface now ensures it's always there.
            chain = tool_llm.bind_tools(tools)

            # --- Step 1: First LLM call to determine tool usage ---
            ai_response = invoke_with_retry(chain.invoke, {"messages": messages})
            messages.append(ai_response)


            # --- Step 2: Handle tool call (generate_kline_image) ---
            if hasattr(ai_response, "tool_calls"):
                for call in ai_response.tool_calls:
                    tool_name = call["name"]
                    tool_args = call["args"]
                    # Always provide kline_data
                    tool_args["kline_data"] = copy.deepcopy(state["kline_data"])
                    tool_fn = next(t for t in tools if t.name == tool_name)
                    tool_result = invoke_tool_with_retry(tool_fn, tool_args)
                    pattern_image_b64 = tool_result.get("pattern_image")
                    messages.append(
                        ToolMessage(
                            tool_call_id=call["id"], content=json.dumps(tool_result)
                        )
                    )
        else:
            print("Using precomputed pattern image from state")

        # --- Step 3: Vision analysis with image (precomputed or generated) ---
        if pattern_image_b64:
            # Add numerical context to help the vision model stay grounded
            precalc = state.get("precalculated_indicators", {})
            
            # --- Extract numerical data for prompt ---
            rsi_latest = "N/A"
            macd_latest = "N/A"
            if precalc:
                # Extract the last value from the precalculated lists
                # Handle both dict-wrapped and direct list cases
                rsi_data = precalc.get('rsi', {})
                rsi_list = rsi_data.get('rsi', []) if isinstance(rsi_data, dict) else rsi_data
                if rsi_list and len(rsi_list) > 0:
                    rsi_latest = rsi_list[-1]
                
                macd_data = precalc.get('macd', {})
                macd_list = macd_data.get('macd', []) if isinstance(macd_data, dict) else []
                if macd_list and len(macd_list) > 0:
                    macd_latest = macd_list[-1]

            numerical_context = (
                f"Numerical Context for Verification:\n"
                f"- Latest RSI: {rsi_latest}\n"
                f"- Latest MACD: {macd_latest}\n"
                f"- Market Condition: {state.get('regime_report', 'N/A')[:300]}...\n"
            )

            image_prompt = [
                {
                    "type": "text",
                    "text": (
                        f"This is a {time_frame} candlestick chart for {state.get('stock_name', 'the asset')}.\n\n"
                        f"{numerical_context}\n"
                        f"{pattern_text}\n\n"
                        "ANALYSIS TASK:\n"
                        "1. Look at the visual structure in the image.\n"
                        "2. Cross-reference it with the Numerical Context provided above.\n"
                        "3. Determine if the chart matches any classic patterns (e.g., Bull Flag, Double Bottom, etc.).\n"
                        "4. Provide a HIGHLY SPECIFIC description of what you see in this specific image. Avoid generic responses."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{pattern_image_b64}"},
                },
            ]

            # Create messages - ensure HumanMessage has valid content
            # For Anthropic, SystemMessage is extracted separately, but messages array must have at least one message
            human_msg = HumanMessage(content=image_prompt)
            
            # Verify HumanMessage content is valid
            if not human_msg.content:
                raise ValueError("HumanMessage content is empty")
            if isinstance(human_msg.content, list) and len(human_msg.content) == 0:
                raise ValueError("HumanMessage content list is empty")
            
            messages = [
                SystemMessage(
                    content="You are a trading pattern recognition assistant tasked with analyzing candlestick charts."
                ),
                human_msg,
            ]
            
            try:
                final_response = invoke_with_retry(
                    graph_llm.invoke,
                    messages,
                )
            except Exception as e:
                error_str = str(e)
                # Handle Anthropic's "at least one message is required" error
                # This can happen when SystemMessage extraction leaves empty messages array
                if "at least one message" in error_str.lower():
                    # Retry with only HumanMessage (SystemMessage will be lost but Anthropic should work)
                    print("Retrying with HumanMessage only due to Anthropic message conversion issue...")
                    final_response = invoke_with_retry(
                        graph_llm.invoke,
                        [human_msg],
                    )
                else:
                    raise
        else:
            # If no image was generated, fall back to reasoning with messages
            final_response = invoke_with_retry(chain.invoke, {"messages": messages})

        return {
            "messages": messages + [final_response],
            "pattern_report": final_response.content,
        }

    return pattern_agent_node
