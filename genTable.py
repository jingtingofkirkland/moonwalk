#!/usr/local/bin/python3
import requests
import time
from datetime import date, datetime
import sys

class Record:
    def __init__(self, name, initial_amount, current_amount, dividen_ytd, gain_loss, is_header=False):
        self.name = name
        self.initial_amount = initial_amount
        self.current_amount = current_amount
        self.dividen_ytd = dividen_ytd
        self.gain_loss = gain_loss
        self.is_header = is_header

class Stock:
    def __init__(self, name, origin_unit_price, initial_amount, cur_unit_price=0.0, dividends=None):
        self.name = name
        self.origin_unit_price = origin_unit_price
        self.initial_amount = initial_amount
        self.cur_unit_price = cur_unit_price
        self.dividends = dividends or []

    def gain(self):
        return self.cur_unit_price / self.origin_unit_price

    def unit(self):
        return self.initial_amount / self.origin_unit_price

    def cur_value(self):
        return self.gain() * self.initial_amount

    def dividend_total(self):
        return sum(self.dividends) * self.unit()

    def gain_total(self):
        return self.cur_value() + self.dividend_total() - self.initial_amount

class GenTable:
    def __init__(self):
        self.prefix = "  "
        self.intent = "  "
        self.stocks = [
            Stock("FXAIX", 142.71, 5000.0, dividends=[0.538, 0.602]),
            Stock("FZILX", 10.5, 1500.0),
            Stock("FXNAX", 10.4, 1827.0, dividends=[0.022, 0.025]),
            Stock("BABA", 105.0, 1050.0),
            Stock("BYDDY", 62.3, 623.0, dividends=[0.331]),
        ]

    def tr_open(self):
        return f"{self.prefix}<tr>\n"

    def tr_close(self):
        return f"{self.prefix}</tr>\n"

    def td(self, content, header=False):
        if header:
            return f"{self.prefix}{self.intent}<th> {content} </th>\n"
        else:
            return f"{self.prefix}{self.intent}<td> {content} </td>\n"

    def gen(self, current_prices, date, divs):
        current_prices = current_prices or [156.84, 10.72, 10.14, 92.90, 63.14]

        for i, stock in enumerate(self.stocks):
            stock.cur_unit_price = current_prices[i]
            stock.dividends = divs[i]

        records = []
        records.append(Record("Funds", "Initial Value/Unit price", f"Current Value ({date})", "Dividend YTD", "Gain", True))

        for stock in self.stocks:
            records.append(Record(stock.name,
                                   f"${stock.initial_amount:.2f}/${stock.origin_unit_price:.2f}",
                                   f"${stock.cur_value():.2f}/${stock.cur_unit_price:.2f}",
                                   f"${stock.dividend_total():.2f}",
                                   f"${stock.gain_total():.2f}"))

        records.append(Record("Cash Out Fee", "$0", "$-300", "$0", "$-300"))
        total_current_value = sum(stock.cur_value() for stock in self.stocks) - 300
        total_dividend = sum(stock.dividend_total() for stock in self.stocks)
        total_gain = total_current_value + total_dividend - 10000 - 300
        records.append(Record("Total", "$10000", f"${total_current_value:.2f}", f"${total_dividend:.2f}", f"${total_gain:.2f}"))

        sb = []
        for record in records:
            sb.append(self.tr_open())
            sb.append(self.td(record.name, record.is_header))
            sb.append(self.td(record.initial_amount, record.is_header))
            sb.append(self.td(record.current_amount, record.is_header))
            sb.append(self.td(record.dividen_ytd, record.is_header))
            sb.append(self.td(record.gain_loss, record.is_header))
            sb.append(self.tr_close())

        result = f'<table style="width:100%">\n{ "".join(sb) }</table>'
        print(result)
def req(code, type):
    # API endpoint (replace with your endpoint)
    api_endpoint = f"https://query1.finance.yahoo.com/v7/finance/download/{code}?period1={one_day_ago}&period2={current_epoch}&interval=1d&events={type}&includeAdjustedClose=true"
    if type =='div':
        api_endpoint = f"https://query1.finance.yahoo.com/v7/finance/download/{code}?period1=1675252800&period2={current_epoch}&interval=1d&events={type}&includeAdjustedClose=true"
    #print(api_endpoint)
    custom_headers = {
        "User-Agent": ""
    }

    # Make the HTTP GET request with parameters
    response = requests.get(api_endpoint, headers= custom_headers)

    if response.status_code == 200:
        # Request was successful
        return response.text
    else:
        return None

def parse(data):
    prices_str = data.split('\n')
    # print(prices_str[-1])
    d_header = prices_str[0].split(',')
    prices = prices_str[-1].split(',')
    index = d_header.index('Close')
    close_price = prices[index]
    return close_price
def parseDiv(data):
    yearly_divs = data.split('\n')
    d_header_str = yearly_divs[0]
    divs = [float(divs.split(',')[1]) for divs in yearly_divs[1:]]
    return divs

def getPrice(code):
    data = req(code, 'history')
    return parse(data)
def getDivs(code):
    data = req(code, 'div')
    return parseDiv(data)

if __name__ == "__main__":
    current_epoch = None
    today_date = None
    if len(sys.argv) != 2:
        # Get the current epoch timestamp in seconds
        current_epoch = int(time.time())
        today_date = date.today()
    else:
        date_string = sys.argv[1]
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        current_epoch = int(parsed_date.timestamp())
        today_date = parsed_date.date()

    # Calculate the epoch timestamp for one day ago
    one_day_ago = current_epoch - 86400*7  # 86400 seconds in a day

    codes = [ 'FXAIX', 'FZILX', 'FXNAX', 'BABA', 'BYDDY']
    prices = [ float(getPrice(code)) for code in codes]
    divs = [ getDivs(code) for code in codes]
    GenTable().gen(prices, today_date, divs)
