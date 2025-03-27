from flask import Blueprint, request, jsonify
from models import db, OrderHeader, OrderDetail
from datetime import datetime, timezone
from sqlalchemy import select

api_bp = Blueprint('api', __name__)

# Order Header Routes
@api_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = OrderHeader.query.all()
    return jsonify([order.to_dict() for order in orders])

@api_bp.route('/orders/<int:orderid>', methods=['GET'])
def get_order(orderid):
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order.to_dict())

@api_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    if not data or 'ordercustomerid' not in data:
        return jsonify({'error': 'Customer ID is required'}), 400
    
    # Parse date if provided, otherwise use current date
    orderdate = datetime.now(timezone.utc)
    if 'orderdate' in data:
        try:
            orderdate = datetime.fromisoformat(data['orderdate'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    new_order = OrderHeader(
        ordercustomerid=data['ordercustomerid'],
        orderdate=orderdate
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify(new_order.to_dict()), 201

@api_bp.route('/orders/<int:orderid>', methods=['PUT'])
def update_order(orderid):
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    data = request.get_json()
    
    if 'ordercustomerid' in data:
        order.ordercustomerid = data['ordercustomerid']
    
    if 'orderdate' in data:
        try:
            order.orderdate = datetime.fromisoformat(data['orderdate'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    db.session.commit()
    return jsonify(order.to_dict())

@api_bp.route('/orders/<int:orderid>', methods=['DELETE'])
def delete_order(orderid):
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})

# Order Detail Routes
@api_bp.route('/orders/<int:orderid>/details', methods=['GET'])
def get_order_details(orderid):
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    details = db.session.execute(select(OrderDetail).filter_by(orderid=orderid)).scalars().all()
    return jsonify([detail.to_dict() for detail in details])

@api_bp.route('/orderdetails/<int:orderdetailid>', methods=['GET'])
def get_order_detail(orderdetailid):
    detail = db.session.get(OrderDetail, orderdetailid)
    if not detail:
        return jsonify({'error': 'Order detail not found'}), 404
    return jsonify(detail.to_dict())

@api_bp.route('/orders/<int:orderid>/details', methods=['POST'])
def create_order_detail(orderid):
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    data = request.get_json()
    
    required_fields = ['orderitemid', 'quantity', 'unitrate']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Calculate row total
    quantity = float(data['quantity'])
    unitrate = float(data['unitrate'])
    rowtotal = quantity * unitrate
    
    new_detail = OrderDetail(
        orderid=orderid,
        orderitemid=data['orderitemid'],
        quantity=quantity,
        unitrate=unitrate,
        rowtotal=rowtotal
    )
    
    db.session.add(new_detail)
    db.session.commit()
    
    return jsonify(new_detail.to_dict()), 201

@api_bp.route('/orderdetails/<int:orderdetailid>', methods=['PUT'])
def update_order_detail(orderdetailid):
    detail = db.session.get(OrderDetail, orderdetailid)
    if not detail:
        return jsonify({'error': 'Order detail not found'}), 404
    data = request.get_json()
    
    if 'orderitemid' in data:
        detail.orderitemid = data['orderitemid']
    
    # Update quantity and/or unit rate and recalculate row total if needed
    recalculate = False
    
    if 'quantity' in data:
        detail.quantity = data['quantity']
        recalculate = True
    
    if 'unitrate' in data:
        detail.unitrate = data['unitrate']
        recalculate = True
    
    if recalculate:
        detail.rowtotal = detail.quantity * detail.unitrate
    
    db.session.commit()
    return jsonify(detail.to_dict())

@api_bp.route('/orderdetails/<int:orderdetailid>', methods=['DELETE'])
def delete_order_detail(orderdetailid):
    detail = db.session.get(OrderDetail, orderdetailid)
    if not detail:
        return jsonify({'error': 'Order detail not found'}), 404
    db.session.delete(detail)
    db.session.commit()
    return jsonify({'message': 'Order detail deleted successfully'})
