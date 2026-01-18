
import sys
from pathlib import Path

# Add the parent directory to the Python path to allow importing web_interface
sys.path.append(str(Path(__file__).parent.absolute()))

from web_interface import WebTradingAnalyzer

def test_file_listing():
    """
    Tests the get_available_files method of the WebTradingAnalyzer class.
    """
    print("Initializing WebTradingAnalyzer...")
    analyzer = WebTradingAnalyzer()
    print(f"Data directory is: {analyzer.data_dir.resolve()}")

    asset = "btc"
    timeframe = "4h"

    print(f"Testing with asset='{asset}' and timeframe='{timeframe}'")
    files = analyzer.get_available_files(asset, timeframe)

    print("Result of get_available_files:")
    if files:
        for f in files:
            print(f)
    else:
        print("No files found.")

if __name__ == "__main__":
    test_file_listing()
