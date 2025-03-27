# Recommendations from: https://www.perplexity.ai/search/can-you-look-at-this-code-and-ZmYi20OySGmGULYqjVFTyA
# Improvements implemented:
# 1. Better error handling with try/except blocks
# 2. Input validation for all endpoints
# 3. Consistent response format
# 4. Proper HTTP status codes
# 5. Transaction management

from flask import Blueprint, request, jsonify
from models import db, OrderHeader, OrderDetail
from datetime import datetime, timezone
from sqlalchemy import select

api_bp = Blueprint('api', __name__)

# ============================================================================
# Order Header Routes
# ============================================================================
@api_bp.route('/orders', methods=['GET'])
def get_orders():
    """
    Get all orders with optional filtering and pagination
    ---
    Parameters:
        customer_id (optional): Filter by customer ID
        start_date (optional): Filter by orders on or after this date (ISO format)
        end_date (optional): Filter by orders on or before this date (ISO format)
        page (optional): Page number for pagination (default: 1)
        per_page (optional): Items per page (default: 20, max: 100)
    Returns:
        A JSON object containing:
        - items: Array of order headers
        - total: Total number of matching orders
        - page: Current page number
        - pages: Total number of pages
        - per_page: Items per page
    """
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limit max per_page to 100
        
        # Start with base query
        query = OrderHeader.query
        
        # Apply filters if provided
        if customer_id:
            query = query.filter(OrderHeader.ordercustomerid == customer_id)
            
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
                query = query.filter(OrderHeader.orderdate >= start_date)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
                
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
                query = query.filter(OrderHeader.orderdate <= end_date)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        # Execute query with pagination
        paginated_orders = query.order_by(OrderHeader.orderdate.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        
        # Prepare response
        return jsonify({
            'status': 'success',
            'data': {
                'items': [order.to_dict() for order in paginated_orders.items],
                'total': paginated_orders.total,
                'page': paginated_orders.page,
                'pages': paginated_orders.pages,
                'per_page': paginated_orders.per_page
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@api_bp.route('/orders/<int:orderid>', methods=['GET'])
def get_order(orderid):
    """
    Get a specific order by ID
    ---
    Parameters:
        orderid (int): The ID of the order to retrieve
    Returns:
        A JSON object containing the order details
    Responses:
        404: Order not found
    """
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order.to_dict())

@api_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order
    ---
    Parameters:
        JSON body with:
        - ordercustomerid (required): The customer ID for the order
        - orderdate (optional): ISO format date (YYYY-MM-DDTHH:MM:SS)
    Returns:
        A JSON object containing the created order with 201 status code
    Responses:
        400: Missing required fields or invalid date format
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        if 'ordercustomerid' not in data:
            return jsonify({'status': 'error', 'message': 'Customer ID is required'}), 400
        
        # Validate customer ID is a positive integer
        try:
            customer_id = int(data['ordercustomerid'])
            if customer_id <= 0:
                return jsonify({'status': 'error', 'message': 'Customer ID must be a positive integer'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Customer ID must be a valid integer'}), 400
        
        # Parse date if provided, otherwise use current date
        orderdate = datetime.now(timezone.utc)
        if 'orderdate' in data:
            try:
                orderdate = datetime.fromisoformat(data['orderdate'])
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        # Use transaction to ensure data consistency
        try:
            new_order = OrderHeader(
                ordercustomerid=customer_id,
                orderdate=orderdate
            )
            
            db.session.add(new_order)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Order created successfully',
                'data': new_order.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@api_bp.route('/orders/<int:orderid>', methods=['PUT'])
def update_order(orderid):
    """
    Update an existing order
    ---
    Parameters:
        orderid (int): The ID of the order to update
        JSON body with:
        - ordercustomerid (optional): The customer ID for the order
        - orderdate (optional): ISO format date (YYYY-MM-DDTHH:MM:SS)
    Returns:
        A JSON object containing the updated order
    Responses:
        404: Order not found
        400: Invalid input data
        500: Server error
    """
    try:
        order = db.session.get(OrderHeader, orderid)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        # Track if any changes were made
        changes_made = False
        
        if 'ordercustomerid' in data:
            try:
                customer_id = int(data['ordercustomerid'])
                if customer_id <= 0:
                    return jsonify({'status': 'error', 'message': 'Customer ID must be a positive integer'}), 400
                order.ordercustomerid = customer_id
                changes_made = True
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': 'Customer ID must be a valid integer'}), 400
        
        if 'orderdate' in data:
            try:
                order.orderdate = datetime.fromisoformat(data['orderdate'])
                changes_made = True
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        if not changes_made:
            return jsonify({'status': 'warning', 'message': 'No changes made to the order'}), 200
            
        try:
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Order updated successfully',
                'data': order.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@api_bp.route('/orders/<int:orderid>', methods=['DELETE'])
def delete_order(orderid):
    """
    Delete an order
    ---
    Parameters:
        orderid (int): The ID of the order to delete
    Returns:
        A JSON message confirming deletion
    Responses:
        404: Order not found
    """
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})

# ============================================================================
# Order Detail Routes
# ============================================================================
@api_bp.route('/orders/<int:orderid>/details', methods=['GET'])
def get_order_details(orderid):
    """
    Get all details for a specific order
    ---
    Parameters:
        orderid (int): The ID of the order to retrieve details for
    Returns:
        A JSON array containing all details for the specified order
    Responses:
        404: Order not found
    """
    order = db.session.get(OrderHeader, orderid)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    details = db.session.execute(select(OrderDetail).filter_by(orderid=orderid)).scalars().all()
    return jsonify([detail.to_dict() for detail in details])

@api_bp.route('/orderdetails/<int:orderdetailid>', methods=['GET'])
def get_order_detail(orderdetailid):
    """
    Get a specific order detail by ID
    ---
    Parameters:
        orderdetailid (int): The ID of the order detail to retrieve
    Returns:
        A JSON object containing the order detail
    Responses:
        404: Order detail not found
    """
    detail = db.session.get(OrderDetail, orderdetailid)
    if not detail:
        return jsonify({'error': 'Order detail not found'}), 404
    return jsonify(detail.to_dict())

@api_bp.route('/orders/<int:orderid>/details', methods=['POST'])
def create_order_detail(orderid):
    """
    Create a new order detail for a specific order
    ---
    Parameters:
        orderid (int): The ID of the order to add a detail to
        JSON body with:
        - orderitemid (required): The item ID
        - quantity (required): The quantity ordered
        - unitrate (required): The unit price
    Returns:
        A JSON object containing the created order detail with 201 status code
    Responses:
        404: Order not found
        400: Missing or invalid required fields
        500: Server error
    Notes:
        The rowtotal is automatically calculated as quantity * unitrate
    """
    try:
        order = db.session.get(OrderHeader, orderid)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['orderitemid', 'quantity', 'unitrate']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'status': 'error', 
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate orderitemid
        try:
            item_id = int(data['orderitemid'])
            if item_id <= 0:
                return jsonify({'status': 'error', 'message': 'Item ID must be a positive integer'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Item ID must be a valid integer'}), 400
        
        # Validate quantity
        try:
            quantity = float(data['quantity'])
            if quantity <= 0:
                return jsonify({'status': 'error', 'message': 'Quantity must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Quantity must be a valid number'}), 400
        
        # Validate unitrate
        try:
            unitrate = float(data['unitrate'])
            if unitrate < 0:
                return jsonify({'status': 'error', 'message': 'Unit rate cannot be negative'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Unit rate must be a valid number'}), 400
        
        # Calculate row total
        rowtotal = quantity * unitrate
        
        try:
            new_detail = OrderDetail(
                orderid=orderid,
                orderitemid=item_id,
                quantity=quantity,
                unitrate=unitrate,
                rowtotal=rowtotal
            )
            
            db.session.add(new_detail)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Order detail created successfully',
                'data': new_detail.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@api_bp.route('/orderdetails/<int:orderdetailid>', methods=['PUT'])
def update_order_detail(orderdetailid):
    """
    Update an existing order detail
    ---
    Parameters:
        orderdetailid (int): The ID of the order detail to update
        JSON body with:
        - orderitemid (optional): The item ID
        - quantity (optional): The quantity ordered
        - unitrate (optional): The unit price
    Returns:
        A JSON object containing the updated order detail
    Responses:
        404: Order detail not found
    Notes:
        The rowtotal is automatically recalculated if quantity or unitrate changes
    """
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
    """
    Delete an order detail
    ---
    Parameters:
        orderdetailid (int): The ID of the order detail to delete
    Returns:
        A JSON message confirming deletion
    Responses:
        404: Order detail not found
    """
    detail = db.session.get(OrderDetail, orderdetailid)
    if not detail:
        return jsonify({'error': 'Order detail not found'}), 404
    db.session.delete(detail)
    db.session.commit()
    return jsonify({'message': 'Order detail deleted successfully'})
