import tkinter as tk 
from tkinter import ttk 

def calculate_USD(symbol,price_data,account,side):
    """
    Calculate the 'rate' to convert ccy to usd.

    Args:
        symbol : from dict account_symbol_info
        price_data (float): from API
        account: from dict account_symbol_info

    Returns:
        float: rate"""
    rate =0
    if symbol[3:6] == "USD":
        rate = 1
    if int(account) == 3540205 or int(account) == 3540011:
        if symbol[3:6] + "USD.pr" in price_data[account]:
            new_symbol = symbol[3:6] + "USD.pr"
            if side == "buy":
                rate = price_data[account][new_symbol]["bid"]
            rate = price_data[account][new_symbol]["ask"]
            # rate = (price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2
        elif "USD" + symbol[3:6] + ".pr" in price_data[account]:
            new_symbol = "USD" + symbol[3:6] + ".pr"
            if side == "buy":
                rate = 1/(price_data[account][new_symbol]["bid"])
            rate = 1/(price_data[account][new_symbol]["ask"])
            # rate = 1/((price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2)
    else:
        if symbol[3:] + "USD" in price_data[account]:
            new_symbol = symbol[3:] + "USD"
            if side == "buy":
                rate = price_data[account][new_symbol]["bid"]
            rate = price_data[account][new_symbol]["ask"]
            # rate = (price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2
        elif "USD" + symbol[3:] in price_data[account]:
            new_symbol = "USD" + symbol[3:]
            if side == "buy":
                rate = 1/(price_data[account][new_symbol]["bid"])
            rate = 1/(price_data[account][new_symbol]["ask"])
            # rate = 1/((price_data[account][new_symbol]["bid"] + price_data[account][new_symbol]["ask"])/2)
    return rate 

    #----------------------------------CACULATION FUNCTIONS-------------------------------------#
def calculate_new_price(pre_price, pip, symbol):
    """
    Calculate the 'New Price' column dynamically based on the 'Pips' input.

    Args:
        pre_price (float): The previous price.
        pip (float): The number of pips to add/subtract.
        symbol (str): The currency pair symbol (e.g., 'USDJPY').

    Returns:
        float: The new price after adding/subtracting pips.
    """
    try:
        # Ensure pre_price is a valid float
        pre_price = float(pre_price) if pre_price else 0.0
        pip = float(pip) if pip else 0.0

        # Check if symbol contains "JPY" and adjust pip calculation accordingly
        if symbol[3:6] == "JPY":
            return round(pre_price + pip / 100, 3)  # JPY pairs: pip is 1/100
        return round(pre_price + pip / 10000, 5)  # Other pairs: pip is 1/10,000
    except (ValueError, TypeError) as e:
        print(f"Error in calculate_new_price: {e}")
        return 0.0  # Return a default value if calculation fails

def calculate_pips(target_price,new_price,symbol):
    """
    Calculate the 'needed pips' to convert ccy to usd.

    Args:
        target_price : user input
        new_price (float): from calculation
        symbol: from dict account_symbol_info

    Returns:
        float: rate"""
    try:
        target_price = float(target_price) if target_price else 0.0
        new_price = float(new_price) if new_price else 0.0
        
        if target_price == '':
            return 0.0
        if symbol[3:6] == "JPY":
            return round((target_price - new_price) * 100,3 )
        return round((target_price - new_price) * 10000 , 5)
    except (ValueError, TypeError) as e:
        print(f"Error in calculate_pip: {e}")
        return 0.0  # Return a default value if calculation fa

def calculate_current_pl(market_price,vwap_price,lots,rate):
    """
        rate: is used for to change right ccy to usd
    """
    try:
        market_price = float(market_price) if market_price else 0.0
        vwap_price = float(vwap_price) if vwap_price else 0.0

        if lots < 0:
            return round((market_price - vwap_price)*lots * 100000 * rate,2)
        else:
            return round((vwap_price- market_price)*lots * 100000 * rate,2)
    except Exception as e:
        print(f"Error in calculate pl: {e}")
        return 0.0

def calculate_cover_lots(cur_pl,pre_pl,rate):
    """
    Convert difference to lots
    Args:
        cur_pl : from calculation
        pre_pl (float): from calculation
        rate: right ccy + "USD"

    Returns:
        float: lots
    """
    different = cur_pl - pre_pl
    return round(different/(rate*100000),2)

class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind("<Double-1>", self.on_double_click)
        self._entry = None  # Keep track of the entry widget
        self.edited_values = {}  # A dictionary to store edited values for persistence

    def on_double_click(self, event):
        if self._entry is not None:
            self._entry.destroy()

        region_clicked = self.identify_region(event.x, event.y)
        if region_clicked not in ('tree', 'cell'):
            return

        column = self.identify_column(event.x)
        column_index = int(column[1:]) - 1

        allowed_cols = [4, 6, 13]
        if column_index not in allowed_cols:
            return

        selected_id = self.focus()
        if selected_id == "":
            return

        # Store the current values immediately
        selected_values = self.item(selected_id)
        self._current_values = list(selected_values.get('values', []))

        try:
            if column == "#0":
                selected_text = selected_values.get('text', '')
            else:
                values = self._current_values
                while len(values) <= column_index:
                    values.append('')
                selected_text = values[column_index]
        except IndexError:
            selected_text = ''

        column_box = self.bbox(selected_id, column)

        # Create entry widget
        self._entry = ttk.Entry(self)
        self._entry.editing_column_index = column_index
        self._entry.editing_item_id = selected_id
        self._entry.current_values = self._current_values.copy()

        # Configure entry
        self._entry.insert(0, selected_text if selected_text is not None else "")
        self._entry.select_range(0, tk.END)

        # Bind events
        self._entry.bind('<Return>', self.on_enter_pressed)
        self._entry.bind('<Escape>', self.on_focus_out)
        self._entry.bind('<FocusOut>', self.on_focus_out)

        # Place the entry
        self._entry.place(x=column_box[0],
                          y=column_box[1],
                          w=column_box[2],
                          h=column_box[3])

        self._entry.focus_set()

    def on_enter_pressed(self, event):
        try:
            new_text = event.widget.get()
            selected_id = event.widget.editing_item_id
            column_index = event.widget.editing_column_index
            current_values = event.widget.current_values

            while len(current_values) <= column_index:
                current_values.append('')

            current_values[column_index] = new_text if new_text != "" else None
            self.item(selected_id, values=current_values)

            # Save the updated value for persistence
            self.edited_values[(selected_id, column_index)] = new_text
        except Exception as e:
            print(f"Error during update: {str(e)}")
        finally:
            if self._entry:
                self._entry.destroy()
                self._entry = None

    def on_focus_out(self, event):
        if self._entry:
            self._entry.destroy()
            self._entry = None



    def refresh_treeview(self, api_data, price_data):
        """Refresh the Treeview with new API data while appending 10 rows per currency pair for each account."""
        self.delete(*self.get_children())  # Clear the treeview

        for account, symbols in api_data.items():
            for symbol, info in symbols.items():
                if info['side'] == "buy":
                    pair = float(info.get("total_size", ""))
                pair = float(info.get("total_size", "")) * -1
                mar_price = float(info.get("market_price", 0))
                curr_pl = float(info.get("total_floatpl", 0))
                # curr_pl = float(info.get("total_floatpl", 0)) + float(info.get("comm_swap",0))
                yes_pl = float(info.get("yesterday_pl", 0))
                diff = round(curr_pl - yes_pl, 2)
                vwap_price = float(info.get("vwap_price",0))
                rate = calculate_USD(symbol,price_data,account,info['side'])
                cover_lots = calculate_cover_lots(curr_pl,yes_pl,rate)
                
                # Generate a unique identifier for the row
                item_id = f"{account}-{symbol}"

                # Combine API data with user edits
                values = [
                    account,  # Account
                    symbol,  # Pair
                    "",  # Day
                    pair,  # Volume
                    self.edited_values.get((item_id, 4), ""),  # Target Price
                    "",  # Need Pips
                    self.edited_values.get((item_id, 6), ""),  # Pips
                    mar_price,  # Market Price
                    yes_pl,  # Yesterday PL
                    curr_pl,  # Current PL
                    diff,  # Difference
                    cover_lots,
                    "",  # Placeholder columns
                ]

                # Insert or update the parent row
                if item_id in self.get_children():
                    self.item(item_id, values=values, tags=("accsym",))
                else:
                    self.insert("", "end", iid=item_id, values=values,tags=("accsym",))

                # Insert child rows for each day
                for day in range(1, 11):
                    day_item_id = f"{item_id}-day{day}"

                    # Fetch the previous day's market price
                    if day == 1:
                        pre_mar = mar_price
                        pre_yl_temp = curr_pl
                        rate_usd = rate
                    else:
                        day_item_id_1 = f"{item_id}-day{day-1}"
                        try:
                            pre_mar = float(self.item(day_item_id_1, "values")[7])  # Column 8 for Market Price
                            pre_yl_temp = float(self.item(day_item_id_1, "values")[9])
                            
                        except (KeyError, IndexError, ValueError):
                            pre_mar = mar_price  # Fallback to initial market price
                            pre_yl_temp = curr_pl

                    # Calculate new price
                    try:
                        need_pips = self.edited_values.get((day_item_id, 6), 0)
                        new_price = calculate_new_price(pre_mar, need_pips, symbol)
                        target_price = self.edited_values.get((day_item_id, 4), 0)
                        pips = calculate_pips(target_price,new_price,symbol)
                        pre_yl = pre_yl_temp
                        if new_price == pre_mar:
                            new_pl = pre_yl_temp
                        else:
                            new_pl = calculate_current_pl(new_price,vwap_price,pair,rate_usd)
                        
                        print(f"Symbol {symbol} has rate usd {rate_usd} and new price {new_price} with lots: {pair}")
                    except Exception as e:
                        new_price = ""  # Default to empty if calculation fails
                        pips = ""
                        pre_yl_temp = ""
                        pre_yl = ""
                        new_pl = ""

                        print(f"Error calculating new price for {day_item_id}: {e}")
                        print(f"Error calculating new pip for {day_item_id}: {e}")

                    cover_lots_1 = calculate_cover_lots(new_pl,pre_yl,rate_usd)
                    # Define day row values
                    day_values = [
                        "",  # Account
                        "",  # Pair
                        day,  # Day
                        "",  # Volume
                        self.edited_values.get((day_item_id, 4), ""),  # Target Price
                        pips,  # Need Pips
                        need_pips,  # Pips
                        new_price,  # New Price
                        pre_yl,
                        new_pl,
                        round(new_pl-pre_yl,2),
                        cover_lots_1,
                        "",  # Placeholder columns
                    ]

                    # Insert or update the day row
                    if day_item_id in self.get_children():
                        self.item(day_item_id, values=day_values)
                    else:
                        self.insert("", "end", iid=day_item_id, values=day_values)


                


    #----------------------------------UPDATE EACH ROWS-----------------------------------------#

if __name__ == '__main__':
    root = tk.Tk()
    column_names = ('vehicle_name', 'year', 'color')
    treeview_vehicles = TreeviewEdit(root, columns = column_names)
   
    
    treeview_vehicles.heading('#0', text = "Vehicle Type")
    treeview_vehicles.heading('vehicle_name', text = "Vehicle Name")
    treeview_vehicles.heading('year', text = "Year")
    treeview_vehicles.heading('color', text='Color')

    #define the main row
    sedan_row = treeview_vehicles.insert(parent='',index=tk.END,text = 'Sedan')

    #insert the subrow for main row 
    treeview_vehicles.insert(parent=sedan_row, index=tk.END, values=('Nissan', '2010', 'Silver'))
    treeview_vehicles.insert(parent=sedan_row, index=tk.END, values=('Toyota', '2012', 'Blue'))

    treeview_vehicles.pack(fill = tk.BOTH, expand=True)

    root.mainloop()