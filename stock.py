import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yfinance as yf

# requests.get("https://www.sec.gov/files/company_tickers.json")
with open("company_tickers.json", "r") as f:
    ticker_data = json.load(f)

ticker_data = {
    ticker_data[str(i)]["ticker"]: ticker_data[str(i)]["title"] for i in range(len(ticker_data))
}
tickers = list(ticker_data.keys())#[:100]

"""
# Multi-Threaded approach
def fetch_stock_data(ticker_set):
    stock_data = []
    data = yf.download(ticker_set, period="1d")
    for ticker in ticker_set:
        try:
            stock_data.append(
                {
                    "ticker": ticker,
                    "title": ticker_data[ticker],
                    "current_price": data["Close"][ticker].iloc[-1],
                    "week_52_high": data["High"][ticker].max(),
                    "week_52_low": data["Low"][ticker].min(),
                    "percent_change": (
                        ((data["Close"][ticker].iloc[-1]) - (data["High"][ticker].max()))
                        / (data["High"][ticker].max())
                    )
                    * 100,
                }
            )
        except (KeyError, IndexError):
            stock_data.append(
                {
                    "ticker": ticker,
                    "title": ticker_data[ticker],
                    "current_price": None,
                    "week_52_high": None,
                    "week_52_low": None,
                    "percent_change": None,
                    "error": f"No data for ticker {ticker}",
                }
            )
    return stock_data


# Initialize ThreadPoolExecutor with 10 threads
stock_information = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = []
    i = 0
    while i < len(tickers):
        cur_set_of_tickers = tickers[i : i + 100]
        futures.append(executor.submit(fetch_stock_data, cur_set_of_tickers))
        i += 100

    # Collect the results
    for future in as_completed(futures):
        result = future.result()
        stock_information.extend(result)

"""

# Single threaded approach
stock_information = []
i = 0
while i < len(tickers):
    cur_set_of_tickers = tickers[i : i + 100]
    data = yf.download(cur_set_of_tickers, period="1d")
    i += 100
    # Accessing the current price, 52-week high and low
    for ticker in cur_set_of_tickers:
        try:
            stock_information.append(
                {
                    "ticker": ticker,
                    "title": ticker_data[ticker],
                    "current_price": round(float(data["Close"][ticker].iloc[-1]), 2),
                    "week_52_high": round(float(data["High"][ticker].max()), 2),
                    "week_52_low": round(float(data["Low"][ticker].min()), 2),
                    "percent_change": (
                        round(
                            float(
                                ((data["Close"][ticker].iloc[-1]) - (data["High"][ticker].max()))
                                / (data["High"][ticker].max())
                            )
                            * 100,
                            2,
                        )
                    ),
                }
            )
        except (KeyError, IndexError):
            stock_information.append(
                {
                    "ticker": ticker,
                    "title": ticker_data[ticker],
                    "current_price": None,
                    "week_52_high": None,
                    "week_52_low": None,
                    "percent_change": None,
                    "error": f"No data for ticker {ticker}",
                }
            )

# Output the fetched stock information
stock_information = sorted(
    stock_information,
    key=lambda d: (d["percent_change"] if d["percent_change"] is not None else 0),
)
with open("stock_information.json", "w") as file:
    json.dump(stock_information, file, indent=4)
