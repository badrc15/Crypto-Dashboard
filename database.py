import _sqlite3


class User:
    def __init__(self, username, api_key, secret_key):
        self.username = username
        self.api_key = api_key
        self.secret_key = secret_key

conn = _sqlite3.connect('crypto.db')
cursor = conn.cursor()
print("Database connected successfully")

#add if not exists otherwise error occurs when restarting application because table exists already
conn.execute('''CREATE TABLE IF NOT EXISTS PRICES
         (SYMBOL    TEXT   NOT NULL,
         PRICE     FLOAT    NOT NULL,
         TIME       TIME    NOT NULL,
         PRIMARY KEY (SYMBOL, TIME))''')
print("Prices table created successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS ACCOUNTS
         (USERNAME    TEXT   NOT NULL   PRIMARY KEY,
         API_KEY     TEXT    NOT NULL,
         SECRET_KEY       TEXT    NOT NULL)''')
print("Accounts table created successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS TRADES
         (USERNAME      TEXT   NOT NULL,
         SYMBOL    TEXT   NOT NULL,
         TRADE_ID    TEXT    NOT NULL,
         ORDER_PRICE    FLOAT    NOT NULL,
         ORDER_QTY    FLOAT    NOT NULL,
         EXEC_FEE    FLOAT    NOT NULL,
         EXECUTION_TIME       TIME    NOT NULL,
         PRIMARY KEY (USERNAME, SYMBOL, TRADE_ID))''')
print("Trades table created successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS BALANCES
        (USERNAME   TEXT    NOT NULL,
        COIN  TEXT    NOT NULL,
        QUANTITY  FLOAT NOT NULL,
        DOLLAR_EQUITY   FLOAT   NOT NULL,
        TIME    TIME    NOT NULL,
        PRIMARY KEY(USERNAME, COIN, TIME))''')
print("Balance table created successfully")

global time

def insert_trades(spot_trades, username):
    username = str(username)
    for i in spot_trades:
        order_price = str(i.order_price)
        execution_time = str(i.execution_time)
        cursor.execute("INSERT OR IGNORE INTO TRADES (USERNAME, SYMBOL, TRADE_ID, ORDER_PRICE, ORDER_QTY, EXEC_FEE, EXECUTION_TIME) "
                       "VALUES ('" + username + "', '" + i.symbol + "', '" + i.trade_id + "', '" + order_price + "', '" + i.order_qty + "', '" + i.exec_fee + "', '" + execution_time + "')")
        print("Total", cursor.rowcount, "Records successfully inserted into TRADES table")
        conn.commit()

def get_trades(username):
    cursor.execute("SELECT SYMBOL, TRADE_ID, ORDER_PRICE, ORDER_QTY, EXEC_FEE, EXECUTION_TIME FROM TRADES WHERE USERNAME =" + "'" + username + "'")
    return cursor.fetchall()

def insert_balance_information(wallet_balance, username):
    username = str(username)

    for z in wallet_balance:
        quantity = float(z.quantity)
        dollar_equity = float(z.dollar_equity)
        time = str(z.time)
        cursor.execute("INSERT OR IGNORE INTO BALANCES (USERNAME, COIN, QUANTITY, DOLLAR_EQUITY, TIME) "
                       "VALUES (?, ?, ?, ?, ?)", (username, z.coin, quantity, dollar_equity, time))
        print("Total", cursor.rowcount, "Records successfully inserted into BALANCES table")
        conn.commit()

def get_balances(username):
    username = str(username)
    cursor.execute("SELECT COIN, QUANTITY, DOLLAR_EQUITY, TIME FROM BALANCES WHERE USERNAME = " + "'" + username + "'" + " AND TIME = (SELECT MAX(TIME) FROM BALANCES WHERE USERNAME = " + "'" + username + "'" + ")")
    return cursor.fetchall()


def insert_symbol_prices(symbol_prices):
    for i in symbol_prices:
        price = str(i.price)
        time = str(i.time)
        cursor.execute("INSERT INTO PRICES (SYMBOL, PRICE, TIME) VALUES (" + "'" + i.symbol + "'" + "," + price + "," + time + ")")
        print("Total", cursor.rowcount, "Records successfully inserted into PRICES table")
        conn.commit()

def select_symbol_prices():
    cursor.execute("SELECT * FROM PRICES ORDER BY TIME DESC")
    return cursor.fetchall()

def select_price():
    cursor.execute("SELECT PRICE FROM PRICES ORDER BY TIME DESC")
    return cursor.fetchall()

def select_most_recent_price(coin):
    USDT_symbol = coin + "USDT"
    cursor.execute("SELECT PRICE FROM PRICES WHERE SYMBOL IN (" "'" + USDT_symbol + "'" ") AND TIME = (SELECT MAX(TIME) FROM PRICES)")
    return cursor.fetchall()

def sort_column_by(columnName, direction):
    cursor.execute("SELECT * FROM PRICES ORDER BY " + columnName + " " + direction + ";")
    return cursor.fetchall()

def get_user(username):
    username = str(username)
    cursor.execute("SELECT USERNAME, API_KEY, SECRET_KEY FROM ACCOUNTS WHERE USERNAME = " + "'" + username + "'")
    first_row = cursor.fetchone()
    return User(first_row[0], first_row[1], first_row[2])

def get_all_usernames():
    cursor.execute("SELECT DISTINCT USERNAME FROM ACCOUNTS WHERE API_KEY != \"\" AND SECRET_KEY != \"\";")
    return cursor.fetchall()

def delete_username(username):
    cursor.execute("DELETE FROM ACCOUNTS WHERE USERNAME = " + "'" + username + "'" + ";")
    conn.commit()








