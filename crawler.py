import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("discountingcashflows_api_key")

def get_data(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return json.loads(response.text)

def get_transcript(ticker, quarter, year):
    url = f"https://discountingcashflows.com/api/transcript/{ticker}/{quarter}/{year}/"
    transcript = get_data(url)
    if transcript:
        with open(f'Finance/data/transcript/{ticker}_{year}_{quarter}.json', 'w') as f:
            json.dump(transcript[0], f, ensure_ascii=False)

def get_income_statement(ticker):
    url = f"https://discountingcashflows.com/api/income-statement/?ticker={ticker}&period=quarterly&key={api_key}&currency=USD"
    income_statement = get_data(url)
    if income_statement:
        with open(f'Finance/data/income-statement/{ticker}.json', 'w') as f:
            json.dump(income_statement, f, ensure_ascii=False)

def get_balance_sheet_statement(ticker):
    url = f"https://discountingcashflows.com/api/balance-sheet-statement/?ticker={ticker}&period=quarterly&key={api_key}&currency=USD"
    balance_sheet_statement = get_data(url)
    if balance_sheet_statement:
        with open(f'Finance/data/balance-sheet-statement/{ticker}.json', 'w') as f:
            json.dump(balance_sheet_statement, f, ensure_ascii=False)

def get_cash_flow_statement(ticker):
    url = f"https://discountingcashflows.com/api/cash-flow-statement/?ticker={ticker}&period=quarterly&key={api_key}&currency=USD"
    cash_flow_statement = get_data(url)
    if cash_flow_statement:
        with open(f'Finance/data/cash-flow-statement/{ticker}.json', 'w') as f:
            json.dump(cash_flow_statement, f, ensure_ascii=False)

def get_all_data(ticker):
    get_income_statement(ticker)
    get_balance_sheet_statement(ticker)
    get_cash_flow_statement(ticker)

if __name__ == "__main__":
    tickers = ["INTC", "SSNLF", "TSM", "UMC", "GFS"]
    for ticker in tickers:
        get_all_data(ticker)
