import json
import os
import pandas as pd
from trading_graph import TradingGraph


def test_regime_agent():

    # 1. Load sample data
    csv_path = os.path.join("benchmark", "btc", "BTC_4h_1.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # 2. Prepare data slice (last 45 periods)
    df_slice = df.tail(45).copy()

    required_columns = ["Datetime", "Open", "High", "Low", "Close"]

    for col in required_columns:
        if col not in df_slice.columns:
            raise ValueError(f"Missing required column: {col}")

    df_slice_dict = {}

    for col in required_columns:
        if col == "Datetime":
            df_slice_dict[col] = (
                pd.to_datetime(df_slice[col])
                .dt.strftime("%Y-%m-%d %H:%M:%S")
                .tolist()
            )
        else:
            df_slice_dict[col] = df_slice[col].tolist()

    # 3. Check API key
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set."
        )

    # 4. Initialize TradingGraph
    graph = TradingGraph()

    # 5. Prepare initial state
    initial_state = {
        "kline_data": df_slice_dict,
        "time_frame": "4 hour",
        "stock_name": "Bitcoin",
        "messages": [],
        "analysis_results": "",
        "pattern_image": "",
        "trend_image": "",
    }

    print("Running TradingGraph (starting with Regime Agent)...")

    try:
        final_state = graph.graph.invoke(initial_state)

        print("\n=== REGIME REPORT ===")
        print(final_state.get("regime_report", "No regime report generated."))

        print("\n=== INDICATOR REPORT (to check if flow continued) ===")
        print(final_state.get("indicator_report", "No indicator report generated."))

    except Exception as e:
        print(f"Error during graph execution: {e}")


if __name__ == "__main__":
    test_regime_agent()