from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class OrderHeader(db.Model):
    __tablename__ = 'order_headers'
    
    orderid = db.Column(db.Integer, primary_key=True)
    orderdate = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ordercustomerid = db.Column(db.Integer, nullable=False)
    details = db.relationship('OrderDetail', backref='header', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'orderid': self.orderid,
            'orderdate': self.orderdate.isoformat(),
            'ordercustomerid': self.ordercustomerid
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an OrderHeader from a dictionary"""
        if 'orderdate' in data and isinstance(data['orderdate'], str):
            try:
                orderdate = datetime.fromisoformat(data['orderdate'])
            except ValueError:
                orderdate = datetime.now(timezone.utc)
        else:
            orderdate = datetime.now(timezone.utc)
            
        return cls(
            orderid=data.get('orderid'),
            ordercustomerid=data.get('ordercustomerid'),
            orderdate=orderdate
        )

class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    
    orderdetailid = db.Column(db.Integer, primary_key=True)
    orderid = db.Column(db.Integer, db.ForeignKey('order_headers.orderid'), nullable=False)
    orderitemid = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unitrate = db.Column(db.Float, nullable=False)
    rowtotal = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'orderdetailid': self.orderdetailid,
            'orderid': self.orderid,
            'orderitemid': self.orderitemid,
            'quantity': self.quantity,
            'unitrate': self.unitrate,
            'rowtotal': self.rowtotal
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create an OrderDetail from a dictionary"""
        quantity = float(data.get('quantity', 0))
        unitrate = float(data.get('unitrate', 0))
        rowtotal = quantity * unitrate
        
        return cls(
            orderdetailid=data.get('orderdetailid'),
            orderid=data.get('orderid'),
            orderitemid=data.get('orderitemid'),
            quantity=quantity,
            unitrate=unitrate,
            rowtotal=rowtotal
        )
