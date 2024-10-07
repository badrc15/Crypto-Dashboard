import requests
import time
import hmac
import hashlib
import database

bybit_test_url = 'https://api-testnet.bybit.com'

httpClient = requests.Session()


class SymbolPrice:
    def __init__(self, symbol, price, time):
        self.symbol = symbol
        self.price = price
        self.time = time


class Trade:
    def __init__(self, symbol, trade_id, order_price, order_qty, exec_fee, execution_time):
        self.symbol = symbol
        self.trade_id = trade_id
        self.order_price = order_price
        self.order_qty = order_qty
        self.exec_fee = exec_fee
        self.execution_time = execution_time


class Wallet:
    def __init__(self, coin, quantity, dollar_equity, time):
        self.coin = coin
        self.quantity = quantity
        self.dollar_equity = dollar_equity
        self.time = time


class Key:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key


def verify_keys(api_key, secret_key):
    try:
        keys = []
        recv_window = str(5000)
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = hmacSignature("", secret_key, api_key, time_stamp, recv_window)
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        response = requests.get(bybit_test_url + '/spot/v3/private/account', headers=headers)
        response_json = response.json()
        retCode = response_json['retCode']
        if retCode == 10003:
            return False
        else:
            key = Key(api_key, secret_key)
            keys.append(key)
        return keys
    except Exception as e:
        print(e)
        return False






def get_wallet_balance(username):
    user = database.get_user(username)
    api_key = user.api_key
    secret_key = user.secret_key
    wallet_balance = []
    sign_type = str(2)
    recv_window = str(5000)

    time_stamp = str(int(time.time() * 10 ** 3))
    signature = hmacSignature("", secret_key, time_stamp, api_key, recv_window)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': sign_type,
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    response = requests.get(bybit_test_url + '/spot/v3/private/account', headers=headers)
    response_json = response.json()
    result = response_json['result']
    balances = result['balances']
    if balances:
        for balance in balances:
            coin = balance['coin']
            coin_total = float(balance['total'])
            if coin != "USDT":
                dollar_equity = database.select_most_recent_price(coin)[0][0] * coin_total
                wallet = Wallet(coin, coin_total, dollar_equity, time_stamp)
                wallet_balance.append(wallet)
            else:
                dollar_equity = balance['total']
                wallet = Wallet(coin, coin_total, dollar_equity, time_stamp)
                wallet_balance.append(wallet)
        return wallet_balance


def get_all_last_traded_price():
    symbol_prices = []

    response = requests.get(bybit_test_url + '/spot/v3/public/quote/ticker/price')
    response_json = response.json()
    result = response_json['result']
    list = result['list']
    time = response_json['time']
    for i in list:
        price = float(i['price'])
        if price > 0:
            s = SymbolPrice(i['symbol'], price, time)
            symbol_prices.append(s)
    print("Received all prices from bybit")
    return symbol_prices


def get_trade_history(username):
    user = database.get_user(username)
    api_key = user.api_key
    secret_key = user.secret_key
    spot_trades = []
    # Start time has to be at most 180 days ago
    start_time = str(int((time.time() * 10 ** 3) - 180 * 24 * 60 * 60 * 1000))
    end_time = str(int(time.time() * 10 ** 3))
    sign_type = str(2)
    recv_window = str(5000)
    while True:
        query_string = 'startTime='+str(start_time)+'&endTime='+str(end_time)
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = hmacSignature(query_string, secret_key, time_stamp, api_key, recv_window)
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': sign_type,
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        response = httpClient.request("GET", bybit_test_url + '/spot/v3/private/my-trades?' + query_string, headers=headers)
        response_json = response.json()
        result = response_json['result']
        list = result['list']
        for n in list:
            trade = Trade(n['symbol'], n['tradeId'], n['orderPrice'], n['orderQty'], n['execFee'], n['executionTime'])
            spot_trades.append(trade)
            start_time = max(start_time, n['executionTime'])
        if start_time >= end_time or len(list) < 50:
            break
    return spot_trades


def hmacSignature(payload, secret_key, time_stamp, api_key, recv_window):
    param_string = str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_string.encode("utf-8"),hashlib.sha256)
    return hash.hexdigest()
