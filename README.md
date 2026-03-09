# QuantAgent: Multi-Agent Quantitative Trading System

QuantAgent is a sophisticated quantitative trading analysis platform that leverages the power of Large Language Models (LLMs) and LangGraph to perform multi-dimensional market analysis. By orchestrating specialized agents, QuantAgent provides comprehensive insights into technical indicators, chart patterns, and market trends to deliver actionable trading decisions.

## 🚀 Features

- **Multi-Agent Orchestration**: Built with **LangGraph**, the system utilizes a collaborative workflow of specialized agents:
  - **Indicator Agent**: Calculates and interprets key technical indicators (RSI, MACD, Bollinger Bands, etc.) using TA-Lib.
  - **Pattern Agent**: Identifies and analyzes classic chart patterns (Head and Shoulders, Bull Flags, etc.) using visual and data-driven methods.
  - **Trend Agent**: Evaluates market momentum and structural trends across multiple timeframes.
  - **Decision Agent**: Synthesizes analysis from all agents to provide a final trade recommendation (LONG, SHORT, or NEUTRAL) with risk/reward metrics.
- **Flexible LLM Integration**: Supports leading AI providers:
  - **OpenAI** (GPT-4o, GPT-4o-mini)
  - **Anthropic** (Claude 3.5 Sonnet, Claude 3 Haiku)
  - **Qwen** (Qwen Max, Qwen VL Plus)
- **Live & Historical Data**: 
  - Real-time data fetching via **Yahoo Finance**.
  - Local CSV benchmark support for backtesting and analysis of specific historical periods.
- **Interactive Web Interface**: A modern, Flask-based dashboard for:
  - Configuring LLM providers and API keys.
  - Selecting assets (Crypto, Stocks, Forex, Indices).
  - Visualizing K-line charts and trend graphs.
  - Reviewing detailed agent reports and final decisions.

## 🛠 Tech Stack

- **Backend**: Python, Flask
- **AI/LLM**: LangChain, LangGraph, OpenAI API, Anthropic API, DashScope (Qwen)
- **Data Analysis**: Pandas, NumPy, TA-Lib, yfinance
- **Visualization**: Matplotlib, mplfinance, Plotly

## 📋 Prerequisites

- Python 3.9+
- [TA-Lib](https://github.com/mrjbq7/ta-lib) (Technical Analysis Library)
- API Key(s) for OpenAI, Anthropic, or Qwen.

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/QuantAgent-allagents.git
   cd QuantAgent-allagents
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: TA-Lib might require manual installation depending on your operating system.*

3. **Set up API Keys**:
   You can set these as environment variables or configure them directly in the web interface settings.
   ```bash
   export OPENAI_API_KEY='your-key-here'
   # OR
   export ANTHROPIC_API_KEY='your-key-here'
   # OR
   export DASHSCOPE_API_KEY='your-key-here'
   ```

## 🚀 Usage

1. **Start the web interface**:
   ```bash
   python web_interface.py
   ```

2. **Access the dashboard**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

3. **Run an Analysis**:
   - Select your preferred **LLM Provider** in the settings.
   - Choose an **Asset** (e.g., BTC, SPX, AAPL).
   - Select the **Data Source** (Live or Local).
   - Click **Run Analysis** to initiate the multi-agent workflow.

## 📂 Project Structure

- `web_interface.py`: Main Flask application and API endpoints.
- `trading_graph.py`: Core orchestrator using LangGraph.
- `*_agent.py`: Implementation of individual specialized agents.
- `graph_setup.py`: Definition of the LangGraph state machine and nodes.
- `benchmark/`: Directory containing local CSV data for various assets.
- `templates/`: HTML templates for the web UI.
- `static_util.py` & `graph_util.py`: Utility functions for data processing and image generation.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Disclaimer: QuantAgent is an analytical tool and does not constitute financial advice. Trading involves significant risk.*
