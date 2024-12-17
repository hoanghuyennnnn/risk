from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PriceData(db.Model):
    __tablename__ = 'price_data'
    # id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(10),nullable = False, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False,primary_key=True)
    bid = db.Column(db.Float, nullable=False)
    ask = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
    
    def __repr__(self):
        return f'<PriceData {self.symbol} - Bid: {self.bid}, Ask: {self.ask}, Account: {self.account}>'


class AccountInfo(db.Model):
    __tablename__ = "account_info"
    # id = db.Column(db.Integer, primary_key = True,autoincrement=True)
    account = db.Column(db.Integer,nullable = False, primary_key=True)
    balance= db.Column(db.Double, nullable=False)
    equity = db.Column(db.Double, nullable=False)
    margin = db.Column(db.Double, nullable=False)
    credit = db.Column(db.Double, nullable=False)
    floatpl = db.Column(db.Double, nullable=False)
    closepl = db.Column(db.Double, nullable=False)
    date = db.Column(db.DateTime, nullable=False, primary_key=True)


    def __repr__(self):
        return f'<Account: {self.account} - balance: {self.balance}, equity: {self.equity}, margin: {self.margin}>'


class OpenPositions(db.Model):
    __tablename__ = "open_positions"
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-increment primary key
    account = db.Column(db.Integer, nullable=False)
    orderticket = db.Column(db.Integer, nullable=False,primary_key=True)
    opentime = db.Column(db.DateTime, nullable=False)
    side = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Float, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    openprice = db.Column(db.Float, nullable=False)
    currentprice = db.Column(db.Float, nullable=False)
    comm = db.Column(db.Float, nullable=False)
    swap = db.Column(db.Float, nullable=False)
    floatpl = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False,primary_key=True)

    def __repr__(self):
        return f'<Account: {self.account}, Ticket: {self.orderticket}, FloatPL: {self.floatpl}>'
