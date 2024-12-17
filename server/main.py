from flask import Flask, request, jsonify, render_template
from database import db, PriceData, AccountInfo, OpenPositions  # Import db instance and PriceData model
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import mysql.connector
import asyncio

app = Flask(__name__)


logging.basicConfig(filename="data.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
# Configure and connect to the database
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:root@localhost:3306/test'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

price_data = {
    "101821":{},
    "101822":{},
    "3540011":{},
    "3540205":{}
}
#retrieving price data 
@app.route('/api/prices', methods=["POST"])
def receive_price():
    if request.method == 'POST':
        # Handling POST requests with JSON payload
        data = request.get_json(force=True)  # Parse JSON data

        if not data or not isinstance(data, dict):
            return jsonify({"error": "No data provided or incorrect format"}), 400

        # Check for required fields
        required_fields = ["account", "symbol", "bid", "ask", "date"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400  # return for user

        #store data
        account = data["account"]
        symbol = data["symbol"]
        price_data[account][symbol] = {
            "bid": data["bid"],
            "ask": data["ask"],
            "date":data["date"]
        }

        # Update database
        update_db(data)
        logging.info(f"Received data: {data}")

        return jsonify({"message": "Data received successfully", "data": data}), 200

#create the end point 

@app.route('/api/prices/symbol', methods=["GET"])
def get_price():
    if price_data is None:
        return jsonify({"error": "No price data available yet"}), 404
    return jsonify(price_data)

#create the end point for accounts
account_data = {
    "101821":{},
    "101822": {},
    "3540011": {},
    "3540205":{}
} 
#retrieving account info
@app.route('/api/accounts', methods=["POST"])
def receive_account():
    try:
        data = request.get_json(force=True)
        #check type of data
        if not data or not isinstance(data,dict):
            return jsonify({"error": "No data provided or incorrect format "}), 400
        
        #check required fields
        required_fields = ["account", "balance","equity","margin","credit","floatpl","closepl", "date"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error" : f"Missing fields: {', '.join(missing_fields)}"}), 400
        update_account(data)
        account = data["account"]
        account_data[account] = {
            "balance" : data["balance"],
            "equity" : data["equity"],
            "margin" : data["margin"],
            "credit" : data["credit"],
            "floatpl" : data["floatpl"],
            "closepl" : data["closepl"],
            "date" : data["date"]}

        logging.info(f"Receive account data: {data}")
        return jsonify({f"message": "Account data received successully {data}"}), 200
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({f"message": "Something's wrong"}),500

@app.route('/api/accounts/data', methods=["GET"])
def get_account():
    if account_data is None:
        return jsonify({"error": "No price data available yet"}), 404
    return jsonify(account_data)

#retrieving open positions 
position_data = {
    "101821":{},
    "101822":{},
    "3540011": {},
    "3540205":{}
}
@app.route('/api/positions',methods=["POST"])
def receive_position():
    data = request.get_json(force=True)
    if not data or not isinstance(data,dict):
        return jsonify({"error": "No data provided or incorrect format "}), 400
    
    required_fields = ["account", "orderticket", "opentime","side","size","symbol","openprice","currentprice","comm","swap","floatpl"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}),400
    
    #need update data
    update_position(data)
    account = data["account"]
    ticket = data["orderticket"]
    position_data[account][ticket] = {
        "opentime":data["opentime"],
        "side" : data["side"],
        "size" : data["size"],
        "symbol": data["symbol"],
        "openprice":data["openprice"],
        "currentprice":data["currentprice"],
        "comm":data["comm"],
        "swap":data["swap"],
        "floatpl":data["floatpl"],
        "date":data["date"]
    }
    logging.info(f"Receive positions data: {data}")
    return jsonify({f"message:": "Positions data receievd successully {data}"}), 200

#create positions end point

@app.route('/api/positions/data',methods=["GET"])
def get_positions():
    if position_data is None:
        return jsonify({"error": "No position data available yet"}), 404
    return jsonify(position_data)

#update for price 
def update_db(data):
    try:
        account = data["account"]
        symbol = data["symbol"]
        new_bid = data["bid"]
        new_ask = data["ask"]
        date_str = data["date"]
        # date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        # Find existing record for the symbol
        existing_data = PriceData.query.filter_by(symbol=symbol,account = account).first()
        
        if existing_data:
            # Update the existing record
            existing_data.bid = new_bid
            existing_data.ask = new_ask
            existing_data.date = date_str  # Update timestamp to the latest
        else:
            # Create a new record for the symbol
            new_price_data = PriceData(
                account = account,
                symbol=symbol,
                bid=new_bid,
                ask=new_ask,
                date=date_str
            )
            db.session.add(new_price_data)

        db.session.commit()  # Commit changes to the database
    except Exception as e:
        logging.error(f"error: {str(e)}")
        db.session.rollback()
        raise 


def update_account(data):
    try:
        # Parse incoming data
        account = data["account"]
        balance = data["balance"]
        equity = data["equity"]
        margin = data["margin"]
        credit = data["credit"]
        floatpl = data["floatpl"]
        closepl = data["closepl"]
        date_str = data["date"]

        # Convert the incoming date to a datetime object
        incoming_date = datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")

        # Get today's start and end times
        start_of_day = datetime.combine(incoming_date.date(), datetime.min.time())
        end_of_day = datetime.combine(incoming_date.date(), datetime.max.time())
        app.logger.info(f"Processing data from {start_of_day} to {end_of_day}")

        # Check if the account already exists for today
        existing_account = (
            AccountInfo.query.filter(
                AccountInfo.account == account,
                AccountInfo.date >= start_of_day,
                AccountInfo.date <= end_of_day
            )
            .order_by(AccountInfo.date.desc())
            .first()
        )

        if existing_account:
            # Update the existing record with new data
            existing_account.balance = balance
            existing_account.equity = equity
            existing_account.margin = margin
            existing_account.credit = credit
            existing_account.floatpl = floatpl
            existing_account.closepl = closepl
            existing_account.date = incoming_date  # Update to latest time
        else:
            # Add a new record if no record exists for today
            new_account_data = AccountInfo(
                account=account,
                balance=balance,
                equity=equity,
                margin=margin,
                credit=credit,
                floatpl=floatpl,
                closepl=closepl,
                date=incoming_date
            )
            db.session.add(new_account_data)

            # After inserting the new record, delete records older than two days
            cutoff_date = incoming_date - timedelta(days=1)
            db.session.query(AccountInfo).filter(
                AccountInfo.account == account,
                AccountInfo.date < cutoff_date
            ).delete()

        # Commit the transaction
        db.session.commit()
        app.logger.info(f"Account {account} updated successfully.")

    except Exception as e:
        app.logger.error(f"Error while updating account: {str(e)}")
        db.session.rollback()
        raise

#update for open positions
def update_position(data):
    try:
        # Extract data from input
        account = data["account"]
        orderticket = data["orderticket"]
        side = data["side"]
        size = data["size"]
        symbol = data["symbol"]
        openprice = data["openprice"]
        opentime = data["opentime"]
        currentprice = data["currentprice"]
        comm = data["comm"]
        swap = data["swap"]
        floatpl = data["floatpl"]
        date_str = data["date"]

        # Convert the incoming date to a datetime object
        incoming_date = datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")

        # Get today's start and end times
        start_of_day = datetime.combine(incoming_date.date(), datetime.min.time())
        end_of_day = datetime.combine(incoming_date.date(), datetime.max.time())
        app.logger.info(f"Processing data positions from {start_of_day} to {end_of_day}")

        # Check if the account already exists for today
        existing_position = (
            OpenPositions.query.filter(
                OpenPositions.account == account,
                OpenPositions.orderticket == orderticket,
                OpenPositions.date >= start_of_day,
                OpenPositions.date <= end_of_day
            )
            .order_by(OpenPositions.date.desc())
            .first()
        )
        if existing_position:
            # Update only the fields that can change
            existing_position.swap = swap
            existing_position.floatpl = floatpl
            existing_position.currentprice = currentprice
            existing_position.date = incoming_date  # Redundant but ensures it's correctly handled
        else:
            # Insert a new record if no match is found
            new_position_data = OpenPositions(
                account=account,
                orderticket=orderticket,
                opentime=opentime,
                side=side,
                size=size,
                symbol=symbol,
                openprice=openprice,
                currentprice=currentprice,
                comm=comm,
                swap=swap,
                floatpl=floatpl,
                date=incoming_date
            )
            db.session.add(new_position_data)


            # After inserting the new record, delete records older than two days
            cutoff_date = incoming_date - timedelta(days=1)
            db.session.query(OpenPositions).filter(
                OpenPositions.account == account,
                OpenPositions.orderticket == orderticket,
                OpenPositions.date < cutoff_date
            ).delete()

        # Commit changes to the database
        db.session.commit()
    except Exception as e:
        # Rollback and log any errors
        db.session.rollback()
        logging.error(f"Error updating position: {e}")
        raise



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
