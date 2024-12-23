import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
import queue
import mysql.connector 
from datetime import datetime
from queue import Empty
import json


# Global queues for each tab's data
q_price = queue.Queue()
q_account = queue.Queue()
q_position = queue.Queue()
q_price_sum = queue.Queue()
q_account_sum = queue.Queue()
q_position_sum = queue.Queue() 

# Function to fetch data from the API
def fetch_price_data():
    url = "http://43.131.12.68:80/api/prices/symbol"
    try:
        response = requests.get(url)
        data = response.json()  # Assuming the data returned is JSON
        q_price.put(data)  # Put the fetched data into the queue
    except Exception as e:
        # Put an error message in the queue as a dictionary
        error_message = {"error": f"Error fetching price data: {e}"}
        q_price.put(error_message)

# Thread-safe data fetching function that runs in the background for price data
def fetch_price_data_in_thread():
    while True:
        fetch_price_data()  # Fetch data from the URL
        time.sleep(1)  # Fetch new data every second

def fetch_account_data():
    url = "http://43.131.12.68:80/api/accounts/data"
    try:
        response = requests.get(url)
        data = response.json()
        q_account.put(data)
    except Exception as e:
        error_message = {"error": f"Error fetching account data: {e}"}
        q_account.put(error_message)

# Thread-safe data fetching function that runs in the background for account data
def fetch_account_data_in_thread():
    while True:
        fetch_account_data()
        time.sleep(1)

def fetch_position_data():
    url = "http://43.131.12.68:80/api/positions/data"
    try:
        response = requests.get(url)
        data = response.json()
        q_position.put(data)
    except Exception as e:
        error_message = {"error": f"Error fetching position data: {e}"}
        q_position.put(error_message)

# Thread-safe data fetching function that runs in the background for account data
def fetch_position_data_in_thread():
    while True:
        fetch_position_data()
        time.sleep(1)

def fetch_sum_data():
    price_url= "http://43.131.12.68:80/api/prices/symbol"
    position_url = "http://43.131.12.68:80/api/positions/data"
    acc_url = "http://43.131.12.68:80/api/accounts/data"

    try:
        response_price = requests.get(price_url)
        response_pos = requests.get(position_url)
        response_acc = requests.get(acc_url)
        data_price = response_price.json()  
        data_pos = response_pos.json()
        data_acc = response_acc.json()

        q_price_sum.put(data_price) 
        q_account_sum.put(data_acc)
        q_position_sum.put(data_pos)

    except Exception as e:
        q_price_sum.put(f"Error fetching price data: {e}")
        q_account_sum.put(f"Error fetching account data: {e}")
        q_position_sum.put(f"Error fetching position data: {e}")

def fetch_sum_data_in_thread():
    while True:
        fetch_sum_data()
        time.sleep(1)

# Connect to database to query data 
# with open("D:\Hoang_report\database\data\dashboard\config.json", "r") as config_file:
#     config = json.load(config_file)

def connect_db_fetch_data(query):
    try:
        conn = mysql.connector.connect(
            host="43.131.12.68",
            user="root1",
            password="root",
            database="test"
        )
        print("Connect successful")
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data
    except Exception as e:
        print(f"Error: {e}")

#function to calculate 
def calculate_USD(symbol,price_data,account):
    rate =0
    if symbol[:3] == "USD":
        rate = 1
    elif symbol[:3] + "USD" in price_data[account]:
        new_symbol = symbol[:3] + "USD"
        rate = (price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2
    elif "USD" + symbol[:3] in price_data[account]:
        new_symbol = "USD" + symbol[:3]
        rate = 1/((price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2)
    return rate 

def calculate_rightccy(symbol,price_data,account):
    rate = 0
    if symbol[3:6] == "USD":
        rate = 1
    elif symbol[3:6] + "USD" in price_data[account]:
        new_symbol = symbol[3:6] + "USD"
        rate = 1/((price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2)
    elif "USD" + symbol[3:6] in price_data[account]:
        new_symbol =  "USD" + symbol[3:6]
        rate = ((price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2)
    return rate

def calculate_NOP(size,side,price):
    return size*-1*price * 100000 if side == "buy" else size*price*100000

def calculate_capital(size,price):
    return abs(size*100000*price)

def calculate_vwap(side,size,capital,commswap):
    if (side == "buy" and commswap < 0) or (side == "sell" and commswap < 0):
        vwap = (capital - commswap) / abs(size*100000) 
    else:
        vwap = (capital + commswap) / abs(size*100000)
    return vwap


# Global variable for cached pre_data
cached_pre_data = None
last_fetch_date = None

def prev_data():
    """Fetch previous data from the database only once per day."""
    global cached_pre_data, last_fetch_date

    current_date = datetime.now().date()
    if cached_pre_data is None or last_fetch_date != current_date:
        print("Fetching previous data from database...")
        query = "select * from account_info where date < curdate();"
        data = connect_db_fetch_data(query)
        
        # Populate cached_pre_data
        cached_pre_data = {}
        if data is None:
            data = {}

        for acc in data:
            cached_pre_data[acc[0]] = {
                "balance": acc[1],
                "equity": acc[2],
                "margin": acc[3],
                "credit": acc[4],
                "floatpl": acc[5],
                "closepl": acc[6],
                "timestamp": acc[7]
            }

        # Update the last fetch date
        last_fetch_date = current_date

    return cached_pre_data

cached_pre_pos = None
last_fetch_date_pos = None

def prev_pos():
    """Fetch previous positions data from the database only once per day."""
    global cached_pre_pos, last_fetch_date_pos  # Correct global statement

    current_date = datetime.now().date()  # Standardized variable name
    if cached_pre_pos is None or last_fetch_date_pos != current_date:
        print("Fetching previous positions data from database...")
        query = "select * from open_positions where date < curdate();"
        data = connect_db_fetch_data(query)
        
        # Initialize cached_pre_pos
        cached_pre_pos = {}
        if data is None:
            data = [("3540011", None,None,None,None,None,None,0,0,0,None ),
                    ("3540205", None,None,None,None,None,None,0,0,0,None ),
                    ("101821", None,None,None,None,None,None,0,0,0,None ),
                    ("101822", None,None,None,None,None,None,0,0,0,None )]

        # Process the data and populate cached_pre_pos
        for acc in data:
            acc_id = acc[0]      # Account ID
            sym = acc[5]         # Symbol
            comm, swap, floatpl = acc[-4], acc[-3], acc[-2]  # Commission, swap, and floatPL

            # Ensure account exists in cached data
            if acc_id not in cached_pre_pos:
                cached_pre_pos[acc_id] = {}

            # Ensure symbol exists under the account
            if sym not in cached_pre_pos[acc_id]:
                cached_pre_pos[acc_id][sym] = {
                    "comm": 0,
                    "swap": 0,
                    "floatpl": 0,
                    "totalpl": 0
                }

            # Accumulate values
            cached_pre_pos[acc_id][sym]["comm"] += comm
            cached_pre_pos[acc_id][sym]["swap"] += swap
            cached_pre_pos[acc_id][sym]["floatpl"] += floatpl
            cached_pre_pos[acc_id][sym]["totalpl"] += comm + swap + floatpl

        # Update the last fetch date
        last_fetch_date_pos = current_date

    return cached_pre_pos


# Function to update the Treeview from the price queue
def update_treeview(tree):
    if not q_price.empty():
        try:
            data = q_price.get_nowait()
        # print(f"Received data: {data}")  # Debug print
        except Empty:
            data = {} 

        if isinstance(data, dict) and "error" in data:
            # Display the error message and exit the function early
            print(f"Error: {data['error']}")
            return

        # Clear existing rows
        for row in tree.get_children():
            tree.delete(row)

        # Prepare a list of rows to insert
        rows = []
        for account_id, symbols in data.items():
            if not isinstance(symbols, dict):
                continue

            for symbol, price_data in symbols.items():
                if not isinstance(price_data, dict):
                    continue  # Skip if price_data is not a dictionary
                row = [
                    account_id,
                    symbol,
                    price_data.get("bid", "N/A"),
                    price_data.get("ask", "N/A"),
                    price_data.get("date", "N/A")
                ]
                rows.append(row)

        # Insert rows all at once for better performance
        for row in rows:
            tree.insert('', 'end', values=row)


    # Schedule the function to run again after 1000 ms (1 second)
    tree.after(1000, update_treeview, tree)

def update_account(tree):
    pre_data = prev_data()  # Fetch cached previous data

    # Ensure pre_data is a dictionary
    if not isinstance(pre_data, dict):
        print(f"Invalid pre_data type: {type(pre_data)}. Skipping update...")
        return

    if not q_account.empty():
        try:
            data = q_account.get_nowait()
        except Empty:
            data = {}

        if not isinstance(data, dict):
            print(f"Invalid data type: {type(data)}. Skipping...")
            return

        # Clear existing rows
        for row in tree.get_children():
            tree.delete(row)

        # Prepare a list of rows to insert
        rows = []
        for account_id, account_data in data.items():
            if not isinstance(account_data, dict):  # Skip invalid account data
                continue

            account_id = int(account_id)  # Ensure type consistency with pre_data

            if account_id not in pre_data:
                print(f"Account ID {account_id} not found in pre_data. Skipping...")
                continue

            # Calculate closepl (difference between balance and previous balance)
            closepl = account_data.get("balance", 0) - pre_data[account_id].get("balance", 0)
            
            # Prepare the row
            row = [
                account_id,
                f'{account_data.get("balance", 0):,}',
                f'{account_data.get("equity", 0):,}',
                f'{account_data.get("margin", 0):,}',
                f'{account_data.get("credit", 0):,}',
                f'{account_data.get("closepl", 0):,}',
                f'{closepl:,}',
                account_data.get("date", "N/A"),  # Add the "Date" field
            ]
            rows.append(row)

        # Insert rows into the Treeview
        for row in rows:
            tree.insert('', 'end', values=row)

    # Schedule the function to run again after 1000 ms (1 second)
    tree.after(1000, update_account, tree)

# Function to update position data in the Treeview
def update_position(tree):
    if not q_position.empty():
        try:
            data = q_position.get_nowait()
        except Empty:
            data = {}
        
        if not isinstance(data, dict):
            data = {}

        # Clear existing rows
        for row in tree.get_children():
            tree.delete(row)

        # Prepare a list of rows to insert
        rows = []
        for account_id, tickets in data.items():
            if not isinstance(tickets, dict):
                continue

            for ticket, ticket_data in tickets.items():
                if not isinstance(ticket_data, dict):
                    continue  # Skip if price_data is not a dictionary
                row = [
                    account_id,
                    ticket,
                    ticket_data.get("opentime", "N/A"),
                    ticket_data.get("symbol", "N/A"),
                    ticket_data.get("side", "N/A"),
                    ticket_data.get("size", "N/A"),
                    ticket_data.get("openprice", "N/A"),
                    ticket_data.get("currentprice", "N/A"),
                    f'{ticket_data.get("comm", 0):,}',
                    f'{ticket_data.get("swap", 0):,}',
                    f'{ticket_data.get("floatpl", 0):,}',
                    ticket_data.get("date", "N/A")
                ]
                rows.append(row)

        # Insert rows all at once for better performance
        for row in rows:
            tree.insert('', 'end', values=row)

    # Schedule the function to run again after 1000 ms (1 second)
    tree.after(1000, update_position, tree)

def update_sum(tree1,tree2): 
    pre_data = prev_data()
    pre_pos = prev_pos()
    if not q_price_sum.empty() or not q_account_sum.empty() or not q_position_sum.empty():
        try:
            res_account = q_account_sum.get_nowait()
        except Empty:
            res_account = {}
        try:
            res_position = q_position_sum.get_nowait()
        except Empty:
            res_position = {}
        try:
            price_data = q_price_sum.get_nowait()
        except Empty:
            price_data = {}


        if not isinstance(res_account, dict):
            res_account = {}
        if not isinstance(res_position, dict):
            res_position = {}
        if not isinstance(price_data, dict):
            res_position = {}
        # print("Received data")

        for item in tree1.get_children(): 
            tree1.delete(item) 
        for item in tree2.get_children():
            tree2.delete(item)
    
   
        #table 1
        for acc, info in res_account.items():
            if not info:
                continue

            if int(acc) not in pre_data:
                print(f"Account ID {acc} not found in pre_data. Skipping...")
                continue
            
            closepl = info.get("balance", 0) - pre_data[int(acc)]["balance"]
            # closepl = info.get("balance", 0)

            # Safely get account values

            balance = info.get("balance", 0)
            floatpl = info.get("closepl", 0)
            # closepl = info.get("closepl", 0)
            equity = info.get("equity", 0)
            margin = info.get("margin", 1)  
            credit = info.get("credit", 0)
            
            # Calculate margin level
            margin_level = (equity / margin) * 100 if margin else 0

            # Calculate NOP (Net Open Position) for the account
            nop = 0
            if acc in res_position:
                for ticket, position_info in res_position[acc].items():
                    size = float(position_info["size"])
                    side = position_info["side"]
                    symbol = position_info["symbol"]
                    rate = calculate_USD(symbol, price_data, acc)
                    # print(symbol,rate)
                    nop += calculate_NOP(size, side, rate)
                    

            # Insert account row iid=f"{acc}_account", 
            tree1.insert('', 'end', values=[
                acc, f"{balance:,}", f"{floatpl:,}", f"{closepl:,}", f"{equity:,}", f"{margin:,}", f"{round(margin_level, 2)}%", f"{abs(round(nop, 2)):,}", f"{credit:,}"
            ])


        #table2
        account_symbol_info = {}
        capital = 0

        for acc, tickets in res_position.items():
            if acc not in account_symbol_info:
                account_symbol_info[acc] = {}

            for ticket, ticket_info in tickets.items():
                symbol = ticket_info["symbol"]
                size = float(ticket_info["size"])  # Convert size to float
                floatpl = ticket_info["floatpl"]
                market = ticket_info["currentprice"]
                openprice = ticket_info["openprice"]
                comm_swap = ticket_info["comm"] + ticket_info["swap"]
                side = ticket_info["side"]
                capital = calculate_capital(size,openprice)
                rate = calculate_rightccy(symbol,price_data,acc)
                yes_pl = pre_pos[int(acc)][symbol]['totalpl']
                

                # Initialize the symbol if not already in the account's dictionary
                if symbol not in account_symbol_info[acc]:
                    account_symbol_info[acc][symbol] = {
                        'total_size': 0.0,
                        'total_floatpl': 0.0,
                        'yesterday_pl':0.0,
                        'market_price': market,
                        'side':side,
                        'capital':0.0,
                        'comm_swap':0.0,
                        'rateccy':rate
                    }

                # Sum the size and floatpl, and keep the market price for the symbol
                account_symbol_info[acc][symbol]['total_size'] += size
                account_symbol_info[acc][symbol]['total_floatpl'] += floatpl
                account_symbol_info[acc][symbol]['market_price'] = market  # Market price updates to the last value
                account_symbol_info[acc][symbol]['capital'] += capital
                account_symbol_info[acc][symbol]['comm_swap'] += comm_swap
                account_symbol_info[acc][symbol]['rateccy'] = rate 
                account_symbol_info[acc][symbol]['side'] = side
                account_symbol_info[acc][symbol]['yesterday_pl'] = yes_pl
                # print(f"Acc {acc} has capital: {account_symbol_info[acc][symbol]['capital']} and rate is {account_symbol_info[acc][symbol]['rateccy']} for symbol: {symbol}")

        # Print the result to verify
        for acc, symbols in account_symbol_info.items():
            # print(f"Account {acc}:")
            for symbol, info in symbols.items():
                total_size = info['total_size']
                total_floatpl = info['total_floatpl'] + info['comm_swap']
                market_price = info['market_price']
                side = info['side']
                vwap_price = calculate_vwap(info["side"],total_size,info["capital"],info['comm_swap'])
                yesterday_pl = info['yesterday_pl']
                
                tree2.insert('', 'end', values=[
                acc, symbol,total_size,side,f"{round(total_floatpl,2):,}",f"{round(yesterday_pl,2):,}",market_price,f"{round(vwap_price,5):,}"
            ])
                # print(vwap_price)
        
    tree1.after(1000,update_sum,tree1,tree2)


# Create the Treeview widget for Market Price
def create_table(parent, cols, style):
    tree = ttk.Treeview(parent, columns=cols, show="headings", style=style)
    for col in cols:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)
    return tree

# Create the Treeview widget for Account Information
def create_table_account(parent, cols,style):
    tree = ttk.Treeview(parent, columns=cols, show="headings", style=style)
    for col in cols:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)
    return tree

# Create the Treeview widget for Position Information 
def create_table_positions(parent, cols,style):
    tree = ttk.Treeview(parent, columns=cols, show="headings",style=style)
    for col in cols:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)
    return tree

# Create the Treeview widget for Total Information
def create_table_sum(parent,cols1, cols2,cols3, style):
    # Create the Treeview widget
    tree1 = ttk.Treeview(parent, columns=cols1, show="headings", style=style)
    tree2 = ttk.Treeview(parent, columns=cols2, show="headings",style=style)
    tree3 = ttk.Treeview(parent, columns=cols3, show="headings",style=style)
    for col in cols1:
        tree1.heading(col, text=col, anchor="center")
        tree1.column(col, anchor="center")
    
    for col in cols2:
        tree2.heading(col, text=col, anchor="center")
        tree2.column(col, anchor="center")
    
    for col in cols3:
        tree3.heading(col, text=col, anchor="center")
        tree3.column(col, anchor="center")
    
    tree1.pack(fill="both",expand=True)
    tree2.pack(fill="both",expand=True)
    tree3.pack(fill="both",expand=True)
    return tree1,tree2,tree3


# GUI setup and main loop
def startgui():
    root = tk.Tk()
    root.title("Test")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    style = ttk.Style()
    style.theme_use('default')

    # style.configure('TNotebook.Tab', background="green3")
    style.map("TNotebook.Tab", background=[("selected", "green3")])
    style.configure("Treeview", font=("Arial", 12))  # Content font
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Header font
    
    # Custom style for Treeview in the "Summary" tab
    style.configure("Summary.Treeview", font=("Arial", 20),rowheight=40)  # Content font for Summary
    style.configure("Summary.Treeview.Heading", font=("Arial", 20, "bold"),rowheight=40)  # Header font for Summary


    # Tab 1: Currency price
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Market Price")
    cols1 = ("Account", "Symbol", "Bid", "Ask", "Date")
    tree1 = create_table(tab1, cols1,"Treeview")

    # Tab 2: Account information
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Account Information")
    cols2 = ("Account", "Balance", "Equity", "Margin", "Credit", "Total Floatpl", "ClosePL", "Date")
    tree2 = create_table_account(tab2, cols2,"Treeview")

    #tab 3: Open positions
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3,text="Open Positions")
    cols3 =("Account", "Order ticket", "Open time", "Symbol", "Side", "Size", "Open price", "Current price", "Comm", "Swap", "Floatpl", "Date")
    tree3 = create_table_positions(tab3,cols3,"Treeview")

    #tab 4: Total 
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4,text="Summary")
    cols4_1 = ("Account", "Balance", "Total Floatpl", "Closepl", "Equity", "Margin", "Margin Level", "NOP")
    cols4_2 = ("Account", "Symbol", "Size","Type", "Float PL","Yesterday PL","Market price", "Vwap price")
    cols4_3 = ("Account", "Symbol", "Day", "Size", "Target Price", "Pips", "Input pips", "New market", "Yesterday PL", "Current PL", "Different", "Lots", "Margin levels")
    tree41,tree42,tree43 = create_table_sum(tab4,cols4_1,cols4_2,cols4_3,style="Summary.Treeview")

    # Start the background threads to fetch data
    threading.Thread(target=fetch_price_data_in_thread, daemon=True).start()
    threading.Thread(target=fetch_account_data_in_thread, daemon=True).start()
    threading.Thread(target=fetch_position_data_in_thread, daemon=True).start()
    threading.Thread(target=fetch_sum_data_in_thread,daemon=True).start()

    # Start the update functions for the treeview
    update_treeview(tree1)
    update_account(tree2)
    update_position(tree3)
    update_sum(tree41,tree42)

    # calculate_closepl()

    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    startgui()
