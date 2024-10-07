import _sqlite3
import datetime
import re
import numpy as np
import bybit
import database
import schedule
from tkinter import *
import tkinter.ttk as ttk
import tkinter as tk
from PIL import ImageTk, Image
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Scheduler(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        # schedules the program to refresh prices every sixty seconds
        schedule.every(60).seconds.do(insert_bybit_prices)

        schedule.every(60).seconds.do(insert_account_prices)

        schedule.every(60).seconds.do(insert_balance)
        self.after(1000, self.callback)

    def callback(self):
        schedule.run_pending()

        self.after(1000, self.callback)


def insert_bybit_prices():
    print('Getting latest Bybit prices')
    database.insert_symbol_prices(bybit.get_all_last_traded_price())


def insert_account_prices():
    usernames = database.get_all_usernames()
    for username in usernames:
        print('Getting trades for username ' + username[0])
        spot_trades = bybit.get_trade_history(username[0])
        database.insert_trades(spot_trades, username[0])


def insert_balance():
    usernames = database.get_all_usernames()
    for username in usernames:
        print('Getting balance for username ' + username[0])
        wallet_balance = bybit.get_wallet_balance(username[0])
        database.insert_balance_information(wallet_balance, username[0])


def balance_treeview(username):
    clear(tree3)
    b = database.get_balances(username)
    for row in b:
        row = list(row)
        row[3] = datetime.datetime.fromtimestamp(row[3] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        tree3.insert("", END, values=row)


def account_treeview(username):
    clear(tree2)
    t = database.get_trades(username)
    for row in t:
        row = list(row)
        row[5] = datetime.datetime.fromtimestamp(row[5] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        row[4] = str(round(row[4], 2))
        tree2.insert("", END, values=row)


def symbol(sort_by):
    clear(tree)
    s = database.sort_column_by("SYMBOL", sort_by)
    for row in s:
        # In order to reassign tuple it has to be list
        row = list(row)
        # Datetime accepts time in seconds so we divide by 1000
        row[2] = datetime.datetime.fromtimestamp(row[2] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        tree.insert("", END, values=row)


def date(sort_by):
    clear(tree)
    d = database.sort_column_by("TIME", sort_by)
    for row in d:
        # In order to reassign tuple it has to be list
        row = list(row)
        # Datetime accepts time in seconds so we divide by 1000
        row[2] = datetime.datetime.fromtimestamp(row[2] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        tree.insert("", END, values=row)


def clear(tree):
    for i in tree.get_children():
        tree.delete(i)


global style
global username
global dropdown
global account

screen1 = Tk()
screen2 = Tk()
screen3 = Tk()
screen4 = Tk()
screen5 = Tk()


def register_screen():
    global screen1
    global screen2
    global screen3
    global screen4
    global screen5
    screen3.withdraw()
    screen4 = tk.Toplevel(screen1)
    screen4.geometry("1280x800")
    frame4 = LabelFrame(screen4, padx=10, pady=10)
    frame4.pack(fill=BOTH, expand=1)
    screen4.title("Coindex")
    frame4.config(bg='#33393B')
    error_label = None

    def register():
        nonlocal error_label  # use the nonlocal keyword to reference the outer scope error_label variable
        conn = _sqlite3.connect('crypto.db')
        cursor = conn.cursor()

        if len(username.get()) == 0 or username.get().isdigit() or re.findall("[0-9]", username.get()):
            if not error_label:
                error_label = ttk.Label(frame4, text="That is not a valid username")
                error_label.pack()
            else:
                error_label = ttk.Label(frame4, text="That is not a valid username")
                error_label.pack()
            screen4.after(6000, error_label.destroy)
        elif len(api_key.get()) == 0 or len(secret_key.get()) == 0:  # check if api_key or secret_key are empty
            if not error_label:
                error_label = ttk.Label(frame4, text="API key and Secret key cannot be empty")
                error_label.pack()
            else:
                error_label = ttk.Label(frame4, text="API key and Secret key cannot be empty")
                error_label.pack()
            screen4.after(6000, error_label.destroy)
        else:
            if bybit.verify_keys(api_key, secret_key):
                cursor.execute("INSERT INTO ACCOUNTS VALUES (:username, :api_key, :secret_key)",
                               {
                                   'username': username.get(),
                                   'api_key': api_key.get(),
                                   'secret_key': secret_key.get()
                               })

                username.delete(0, END)
                api_key.delete(0, END)
                secret_key.delete(0, END)
                conn.commit()
                conn.close()

                account_data()
            else:
                error_label = ttk.Label(frame4, text="Keys are incorrect and cannot be added to database.")
                error_label.pack()
                screen4.after(6000, error_label.destroy)

    username_label = ttk.Label(frame4, text="Enter Username:")
    username_label.pack(pady=5)

    username = ttk.Entry(frame4, width=30)
    username.pack()

    api_key_label = ttk.Label(frame4, text="Enter API Key:")
    api_key_label.pack()

    api_key = ttk.Entry(frame4, width=30)
    api_key.pack()

    secret_key_label = ttk.Label(frame4, text="Enter Secret Key:")
    secret_key_label.pack()

    secret_key = ttk.Entry(frame4, width=30)
    secret_key.pack()

    register_button = ttk.Button(frame4, text="Register Account", command=register, width=15)
    register_button.pack()

    menu_button3 = ttk.Button(frame4, text="Menu", command=start_screen, width=30)
    menu_button3.pack(side=BOTTOM)



def account_data():
    global screen1
    global screen2
    global screen3
    global screen4
    global screen5
    global tree2  # define tree2 as a global variable
    screen1.withdraw()
    screen4.withdraw()
    screen3 = tk.Toplevel(screen1)
    screen3.geometry("1280x800")
    frame3 = LabelFrame(screen3, padx=10, pady=10)
    frame3.pack(fill=BOTH, expand=1)
    style = ttk.Style(frame3)
    screen3.title("Coindex")
    frame3.config(bg='#33393B')
    style.theme_use('awdark')

    ttk.Label(frame3, text="Select account below:").pack()

    def selected(event):
        global tree2
        if tree2:
            # if tree2 has been created before, delete its children
            tree2.delete(*tree2.get_children())
        else:
            # if tree2 has not been created yet, create it
            tree2 = ttk.Treeview(frame3)
            tree2['columns'] = ("Symbol", "Trade ID", "Order Price", "Order Quantity", "Execution Fee", "Execution Time")
            tree2.column("#0", width=0)
            tree2.column("Symbol", anchor=W, width=170)
            tree2.column("Trade ID", anchor=W, width=170)
            tree2.column("Order Price", anchor=W, width=170)
            tree2.column("Order Quantity", anchor=W, width=170)
            tree2.column("Execution Fee", anchor=W, width=170)
            tree2.column("Execution Time", anchor=W, width=170)

            tree2.heading("#0", anchor=W)
            tree2.heading("Symbol", text="Symbol", anchor=W)
            tree2.heading("Trade ID", text="Trade ID", anchor=W)
            tree2.heading("Order Price", text="Order Price", anchor=W)
            tree2.heading("Order Quantity", text="Order Quantity", anchor=W)
            tree2.heading("Execution Fee", text="Execution Fee", anchor=W)
            tree2.heading("Execution Time", text="Execution Time", anchor=W)

            tree2.pack(fill=BOTH, expand=1, side=BOTTOM)

        if event.widget.get() != "":
            account_treeview(event.widget.get())

    def query():
        global data
        conn = _sqlite3.connect('crypto.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT(USERNAME) as USERNAME FROM ACCOUNTS")
        data = []
        for row in cursor.fetchall():
            data.append(row[0])
        return data

    dropdown = ttk.Combobox(frame3, values=query())
    dropdown.bind("<<ComboboxSelected>>", selected)
    dropdown.pack(pady=5)

    tree2 = None

    def view_balance():
        account = dropdown.get()
        global screen1
        global screen2
        global screen3
        global screen4
        global screen5
        screen3.withdraw()
        screen5 = tk.Toplevel(screen1)
        screen5.geometry("1280x800")
        frame5 = LabelFrame(screen5, padx=10, pady=10)
        frame5.pack(fill=BOTH, expand=1)
        style = ttk.Style(frame5)
        screen5.title("Coindex")
        frame5.config(bg='#33393B')
        style.theme_use('awdark')

        global tree3
        tree3 = ttk.Treeview(frame5)

        tree3['columns'] = ("Coin", "Quantity", "Dollar Equity", "Time")
        tree3.column("#0", width=0)
        tree3.column("Coin", anchor=W, width=170)
        tree3.column("Quantity", anchor=W, width=170)
        tree3.column("Dollar Equity", anchor=W, width=170)
        tree3.column("Time", anchor=W, width=170)
        tree3.heading("#0", anchor=W)
        tree3.heading("Coin", text="Coin", anchor=W)
        tree3.heading("Quantity", text="Quantity", anchor=W)
        tree3.heading("Dollar Equity", text="Dollar Equity", anchor=W)
        tree3.heading("Time", text="Time", anchor=W)
        tree3.pack(side=LEFT, fill=BOTH, expand=1)

        if account != "":
            balance_treeview(account)

        # Extract the quantities of all coins from the treeview table
        items = tree3.get_children()
        rows = [(tree3.item(item)['values'][0], float(tree3.item(item)['values'][2])) for item in items]

        # Remove rows with NaN or zero dollar equity values
        rows = [(coin, equity) for (coin, equity) in rows if not (np.isnan(equity) or equity == 0)]

        # If there are no rows with non-zero dollar equity, don't show the pie chart
        if len(rows) == 0:
            tree3.destroy()
            ttk.Label(frame5, text="No Data, There is no data to show.").pack(padx=35, pady=300)
        else:
            labels = [row[0] for row in rows]
            quantities = [row[1] for row in rows]

            fig, ax = plt.subplots(figsize=(5, 5))

            ax.pie(quantities, labels=labels, autopct='%1.2f%%', textprops={'color': 'white'})
            ax.set_title('Dollar Equity', color='white')

            # Set the background color of the chart
            fig.patch.set_facecolor('#33393B')

            # Embed the chart in a tkinter canvas
            canvas = FigureCanvasTkAgg(fig, master=frame5)
            canvas.draw()

            # Add the canvas to the tkinter frame
            canvas.get_tk_widget().pack()

        menu_button3 = ttk.Button(frame5, text="Menu", command=start_screen, width=30)
        menu_button3.pack(side=BOTTOM)

    def delete_account():
        global account
        account = dropdown.get()
        database.delete_username(account)
        dropdown.set("")
        dropdown.configure(values=query())

    view_balance_button = ttk.Button(frame3, text="View Balance", width=15, command=view_balance)
    view_balance_button.pack(pady=5)
    delete_account_button = ttk.Button(frame3, text="Delete Account", width=15, command=delete_account)
    delete_account_button.pack(pady=5)
    register_account_label = ttk.Label(frame3, text="Register account here:", width=15)
    register_account_label.pack(pady=5)
    register_button = ttk.Button(frame3, text="Register", command=register_screen, width=10)
    register_button.pack(pady=5)

    menu_button2 = ttk.Button(frame3, text="Menu", command=start_screen, width=30)
    menu_button2.pack(side=BOTTOM)


def dashboard():
    global tree
    global screen1
    global screen2
    global screen3
    global screen4
    global screen5
    screen1.withdraw()
    screen2 = tk.Toplevel(screen1)
    width = 1280
    height = 800
    screen_width = screen2.winfo_screenwidth()
    screen_height = screen2.winfo_screenheight()
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    screen2.geometry('%dx%d+%d+%d' % (width, height, x, y))
    frame2 = LabelFrame(screen2, padx=10, pady=10)
    frame2.pack(fill=BOTH, expand=1)
    screen2.title("Coindex")
    frame2.config(bg='#33393B')

    tree = ttk.Treeview(frame2)

    tree['columns'] = ("Symbol", "Price", "Time")
    tree.column("#0", width=0)
    tree.column("Symbol", anchor=W, width=190)
    tree.column("Price", anchor=CENTER, width=300)
    tree.column("Time", anchor=W, width=300)

    tree.heading("#0", anchor=W)
    tree.heading("Symbol", text="Symbol", anchor=W)
    tree.heading("Price", text="Price", anchor=CENTER)
    tree.heading("Time", text="Time", anchor=W)

    tree.pack(side=TOP, fill=BOTH, expand=1)

    sort_by_date_label = ttk.Label(frame2, text="Click here to sort by Date:")
    sort_by_date_label.pack(anchor=CENTER, pady=10, padx=20, ipady=5)

    sort_date_asc_button = ttk.Button(frame2, text="Date ASC", command=lambda: date("ASC"))
    sort_date_asc_button.pack(anchor=CENTER, ipady=5, pady=5)

    sort_date_desc_button = ttk.Button(frame2, text="Date DESC", command=lambda: date("DESC"))
    sort_date_desc_button.pack(ipady=5, pady=5)

    sort_by_symbol_label = ttk.Label(frame2, text="Click here to sort by Symbol:")
    sort_by_symbol_label.pack(anchor=CENTER, pady=10, padx=20, ipady=5)

    sort_symbol_asc_button = ttk.Button(frame2, text="Symbol ASC", command=lambda: symbol("ASC"))
    sort_symbol_asc_button.pack(ipady=5, pady=5)

    sort_symbol_desc_button = ttk.Button(frame2, text="Symbol DESC", command=lambda: symbol("DESC"))
    sort_symbol_desc_button.pack(ipady=5, pady=5)

    date("DESC")

    menu_button1 = ttk.Button(frame2, text="Menu", command=start_screen, width=30)
    menu_button1.pack(side=BOTTOM)


def start_screen():
    global screen1
    global screen2
    global screen3
    global screen4
    global screen5
    screen2.withdraw()
    screen3.withdraw()
    screen4.withdraw()
    screen5.withdraw()
    screen1 = Tk()
    width = 1280
    height = 800
    screen_width = screen1.winfo_screenwidth()
    screen_height = screen1.winfo_screenheight()
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    screen1.geometry('%dx%d+%d+%d' % (width, height, x, y))
    frame1 = LabelFrame(screen1)
    frame1.pack(ipadx=1280, ipady=800)
    img = ImageTk.PhotoImage(Image.open("NewLogo3.png"), master=screen1, )
    Style = ttk.Style(frame1)
    screen1.title('Coindex')
    frame1.tk.call('source', 'awthemes/awdark.tcl')
    frame1.config(bg='#33393B')
    Style.theme_use('awdark')

    quit_button = ttk.Button(frame1, text="Quit", width=50, command=quit, style='TButton')
    quit_button.pack(pady=50, ipady=20, side=BOTTOM)
    account_data_button = ttk.Button(frame1, text="View account data", width=50, command=account_data)
    account_data_button.pack(ipady=20, side=BOTTOM)
    market_data_button = ttk.Button(frame1, text="View market data", width=50, command=dashboard)
    market_data_button.pack(pady=50, ipady=20, side=BOTTOM)
    logo = ttk.Label(frame1, image=img)
    logo.pack(side=TOP)

    scheduler = Scheduler()
    scheduler.mainloop()


start_screen()