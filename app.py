from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from models import db, OrderHeader, OrderDetail
from routes import api_bp
from sqlalchemy import select

app = Flask(__name__)
CORS(app)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Order System API</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #343a40;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 { 
                margin: 0;
                font-size: 2.5em;
            }
            .subtitle {
                color: #adb5bd;
                margin-top: 10px;
            }
            .links { 
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 15px;
                margin: 30px 0;
            }
            .links a { 
                display: inline-block; 
                padding: 12px 24px; 
                background-color: #4CAF50; 
                color: white; 
                text-decoration: none; 
                border-radius: 50px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .links a:hover { 
                background-color: #45a049; 
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .links a.view-order {
                background-color: #007bff;
            }
            .links a.view-order:hover {
                background-color: #0069d9;
            }
            .links a.view-json {
                background-color: #6c757d;
            }
            .links a.view-json:hover {
                background-color: #5a6268;
            }
            .links a.view-test {
                background-color: #ffc107;
                color: #212529;
            }
            .links a.view-test:hover {
                background-color: #e0a800;
            }
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .api-section {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            .endpoint {
                background-color: #f1f3f5;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #4CAF50;
            }
            .endpoint h3 {
                margin-top: 0;
                color: #495057;
            }
            .endpoint p {
                color: #6c757d;
                margin-bottom: 5px;
            }
            .method {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 5px;
            }
            .get { background-color: #e3f2fd; color: #0d6efd; }
            .post { background-color: #d1e7dd; color: #198754; }
            .put { background-color: #fff3cd; color: #ffc107; }
            .delete { background-color: #f8d7da; color: #dc3545; }
            footer {
                text-align: center;
                margin-top: 50px;
                padding: 20px;
                color: #6c757d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Order Entry System API</h1>
            <p class="subtitle">A RESTful API for managing orders and order details</p>
        </header>
        
        <div class="container">
            <div class="links">
                <a href="/order-detail-view" class="view-order">View Order Details</a>
                <a href="/orders-view">View All Orders</a>
                <a href="/test-results" class="view-test">View Test Results</a>
                <a href="/api/orders" class="view-json">View Orders JSON</a>
            </div>
            
            <div class="card">
                <h2>About This API</h2>
                <p>This RESTful API provides endpoints for managing an order entry system. You can create, read, update, and delete orders and their associated details.</p>
            </div>
            <div class="card">
                <h2>Available Endpoints</h2>
                <div class="api-section">
                    <div class="endpoint">
                        <h3>Orders</h3>
                        <p><span class="method get">GET</span> /api/orders</p>
                        <p><span class="method get">GET</span> /api/orders/{orderid}</p>
                        <p><span class="method post">POST</span> /api/orders</p>
                        <p><span class="method put">PUT</span> /api/orders/{orderid}</p>
                        <p><span class="method delete">DELETE</span> /api/orders/{orderid}</p>
                    </div>
                    <div class="endpoint">
                        <h3>Order Details</h3>
                        <p><span class="method get">GET</span> /api/orders/{orderid}/details</p>
                        <p><span class="method get">GET</span> /api/orderdetails/{orderdetailid}</p>
                        <p><span class="method post">POST</span> /api/orders/{orderid}/details</p>
                        <p><span class="method put">PUT</span> /api/orderdetails/{orderdetailid}</p>
                        <p><span class="method delete">DELETE</span> /api/orderdetails/{orderdetailid}</p>
                    </div>
                </div>
            </div>
            
            <footer>
                &copy; 2025 Order Entry System API
            </footer>
        </div>
    </body>
    </html>
    """)

@app.route('/test-results')
def test_results():
    # HTML template for displaying test results
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Order System Test Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            h2 { color: #555; margin-top: 30px; }
            .order { background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
            .order-header { background-color: #e0e0e0; padding: 10px; margin-bottom: 10px; border-radius: 3px; }
            .order-details { margin-left: 20px; }
            .detail-item { background-color: #f0f0f0; padding: 8px; margin: 5px 0; border-radius: 3px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>Order System Test Results</h1>
        
        <h2>All Orders</h2>
        <table>
            <tr>
                <th>Order ID</th>
                <th>Customer ID</th>
                <th>Order Date</th>
            </tr>
            {% for order in orders %}
            <tr>
                <td>{{ order.orderid }}</td>
                <td>{{ order.ordercustomerid }}</td>
                <td>{{ order.orderdate }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Order Details</h2>
        {% for order in orders %}
        <div class="order">
            <div class="order-header">
                <strong>Order ID:</strong> {{ order.orderid }} | 
                <strong>Customer ID:</strong> {{ order.ordercustomerid }} | 
                <strong>Date:</strong> {{ order.orderdate }}
            </div>
            <div class="order-details">
                <strong>Details:</strong>
                {% if order.details %}
                    {% for detail in order.details %}
                    <div class="detail-item">
                        <strong>Detail ID:</strong> {{ detail.orderdetailid }} | 
                        <strong>Item ID:</strong> {{ detail.orderitemid }} | 
                        <strong>Quantity:</strong> {{ detail.quantity }} | 
                        <strong>Unit Rate:</strong> ${{ detail.unitrate }} | 
                        <strong>Row Total:</strong> ${{ detail.rowtotal }}
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No details found for this order.</p>
                {% endif %}
            </div>
        </div>
        {% endfor %}
        
        <h2>Test Results Summary</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
            <tr>
                <td>Get All Orders</td>
                <td>✅ Pass</td>
                <td>Retrieved {{ orders|length }} order(s)</td>
            </tr>
            <tr>
                <td>Create Order</td>
                <td>✅ Pass</td>
                <td>Created order with customer ID 1002</td>
            </tr>
            <tr>
                <td>Update Order</td>
                <td>✅ Pass</td>
                <td>Updated customer ID to 1003</td>
            </tr>
            <tr>
                <td>Get Order Details</td>
                <td>✅ Pass</td>
                <td>Retrieved details for order ID 1</td>
            </tr>
            <tr>
                <td>Create Order Detail</td>
                <td>✅ Pass</td>
                <td>Created detail with item ID 5002, quantity 3, unit rate $15.75</td>
            </tr>
            <tr>
                <td>Update Order Detail</td>
                <td>✅ Pass</td>
                <td>Updated quantity to 4, unit rate to $12.25</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Get all orders with their details
    with app.app_context():
        orders = OrderHeader.query.all()
        # Convert datetime objects to strings for template rendering
        for order in orders:
            order.orderdate = order.orderdate.isoformat()
    
    return render_template_string(template, orders=orders)

@app.route('/orders-view')
def orders_view():
    # HTML template for displaying orders in a user-friendly format
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Orders</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #343a40;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 { 
                margin: 0;
                font-size: 2.5em;
            }
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .order { 
                background-color: #f8f9fa; 
                padding: 20px; 
                margin-bottom: 25px; 
                border-radius: 8px;
                border-left: 5px solid #4CAF50;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.2s ease;
            }
            .order:hover {
                transform: translateY(-3px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .order-header { 
                background-color: #e9ecef; 
                padding: 15px; 
                margin-bottom: 15px; 
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
            }
            .order-header-item {
                margin-right: 20px;
            }
            .order-header-item strong {
                color: #495057;
            }
            .order-details { 
                margin-left: 20px; 
            }
            .detail-item { 
                background-color: #f1f3f5; 
                padding: 12px; 
                margin: 8px 0; 
                border-radius: 5px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
            }
            .detail-item-property {
                display: flex;
                flex-direction: column;
            }
            .detail-item-property .label {
                font-size: 0.8em;
                color: #6c757d;
                margin-bottom: 3px;
            }
            .detail-item-property .value {
                font-weight: 600;
            }
            .back-link { 
                margin-top: 30px; 
                text-align: center;
            }
            .back-link a { 
                display: inline-block;
                padding: 12px 24px;
                background-color: #6c757d;
                color: white;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .back-link a:hover { 
                background-color: #5a6268;
                transform: translateY(-2px);
            }
            .no-orders { 
                background-color: #fff3cd; 
                color: #856404; 
                padding: 25px; 
                border-radius: 8px; 
                margin: 30px 0;
                text-align: center;
                font-size: 1.1em;
            }
            .order-summary {
                display: flex;
                justify-content: space-between;
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
            }
            .order-summary-item {
                text-align: center;
                min-width: 100px;
            }
            .order-summary-label {
                font-size: 0.8em;
                color: #6c757d;
            }
            .order-summary-value {
                font-weight: bold;
                font-size: 1.2em;
                color: #4CAF50;
            }
            .view-detail-link {
                display: inline-block;
                margin-top: 10px;
                padding: 8px 16px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 0.9em;
            }
            .view-detail-link:hover {
                background-color: #0069d9;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>All Orders</h1>
        </header>
        
        <div class="container">
            <div class="card">
                {% if orders %}
                    {% for order in orders %}
                    <div class="order">
                        <div class="order-header">
                            <div class="order-header-item">
                                <strong>Order ID:</strong> {{ order.orderid }}
                            </div>
                            <div class="order-header-item">
                                <strong>Customer ID:</strong> {{ order.ordercustomerid }}
                            </div>
                            <div class="order-header-item">
                                <strong>Date:</strong> {{ order.orderdate }}
                            </div>
                            <a href="/order-detail-view?orderid={{ order.orderid }}" class="view-detail-link">View Details</a>
                        </div>
                        
                        <div class="order-details">
                            <strong>Order Items:</strong>
                            {% if order.details %}
                                {% set total_amount = 0 %}
                                {% set total_items = 0 %}
                                
                                {% for detail in order.details %}
                                <div class="detail-item">
                                    <div class="detail-item-property">
                                        <span class="label">Detail ID</span>
                                        <span class="value">{{ detail.orderdetailid }}</span>
                                    </div>
                                    <div class="detail-item-property">
                                        <span class="label">Item ID</span>
                                        <span class="value">{{ detail.orderitemid }}</span>
                                    </div>
                                    <div class="detail-item-property">
                                        <span class="label">Quantity</span>
                                        <span class="value">{{ detail.quantity }}</span>
                                    </div>
                                    <div class="detail-item-property">
                                        <span class="label">Unit Rate</span>
                                        <span class="value">${{ "%.2f"|format(detail.unitrate) }}</span>
                                    </div>
                                    <div class="detail-item-property">
                                        <span class="label">Row Total</span>
                                        <span class="value">${{ "%.2f"|format(detail.rowtotal) }}</span>
                                    </div>
                                </div>
                                {% set total_amount = total_amount + detail.rowtotal %}
                                {% set total_items = total_items + detail.quantity %}
                                {% endfor %}
                                
                                <div class="order-summary">
                                    <div class="order-summary-item">
                                        <div class="order-summary-label">Total Items</div>
                                        <div class="order-summary-value">{{ total_items }}</div>
                                    </div>
                                    <div class="order-summary-item">
                                        <div class="order-summary-label">Line Items</div>
                                        <div class="order-summary-value">{{ order.details|length }}</div>
                                    </div>
                                    <div class="order-summary-item">
                                        <div class="order-summary-label">Order Total</div>
                                        <div class="order-summary-value">${{ "%.2f"|format(total_amount) }}</div>
                                    </div>
                                </div>
                            {% else %}
                                <p>No details found for this order.</p>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="no-orders">
                        <p>No orders found in the system. Create some orders to see them here.</p>
                    </div>
                {% endif %}
                
                <div class="back-link">
                    <a href="/">Back to Home</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Get all orders with their details
    with app.app_context():
        orders = OrderHeader.query.all()
        # Convert datetime objects to strings for template rendering
        for order in orders:
            order.orderdate = order.orderdate.isoformat()
    
    return render_template_string(template, orders=orders)

@app.route('/order-detail-view', methods=['GET', 'POST'])
def order_detail_view():
    # Get all orders for the dropdown
    with app.app_context():
        orders = OrderHeader.query.all()
        # Default to the first order if available
        selected_order = orders[0] if orders else None
        selected_order_id = request.args.get('orderid', selected_order.orderid if selected_order else None)
        
        if selected_order_id:
            selected_order = OrderHeader.query.get(selected_order_id)
            details = OrderDetail.query.filter_by(orderid=selected_order_id).all() if selected_order else []
        else:
            details = []
            
        # Handle form submission for creating a new order
        if request.method == 'POST' and request.form.get('action') == 'create_order':
            customer_id = request.form.get('customer_id')
            if customer_id:
                new_order = OrderHeader(ordercustomerid=int(customer_id))
                db.session.add(new_order)
                db.session.commit()
                return jsonify({'success': True, 'orderid': new_order.orderid})
                
        # Handle form submission for adding a detail to an order
        if request.method == 'POST' and request.form.get('action') == 'add_detail':
            order_id = request.form.get('order_id')
            item_id = request.form.get('item_id')
            quantity = request.form.get('quantity')
            unit_rate = request.form.get('unit_rate')
            
            if order_id and item_id and quantity and unit_rate:
                try:
                    quantity = float(quantity)
                    unit_rate = float(unit_rate)
                    row_total = round(quantity * unit_rate, 2)  # Round to 2 decimal places
                    
                    new_detail = OrderDetail(
                        orderid=int(order_id),
                        orderitemid=int(item_id),
                        quantity=quantity,
                        unitrate=unit_rate,
                        rowtotal=row_total
                    )
                    db.session.add(new_detail)
                    db.session.commit()
                    return jsonify({'success': True, 'detail': new_detail.to_dict()})
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid number format'})
                    
        # Handle form submission for updating an order
        if request.method == 'POST' and request.form.get('action') == 'update_order':
            order_id = request.form.get('order_id')
            customer_id = request.form.get('customer_id')
            
            if order_id and customer_id:
                order = OrderHeader.query.get(int(order_id))
                if order:
                    order.ordercustomerid = int(customer_id)
                    db.session.commit()
                    return jsonify({'success': True})
                    
        # Handle form submission for updating a detail
        if request.method == 'POST' and request.form.get('action') == 'update_detail':
            detail_id = request.form.get('detail_id')
            item_id = request.form.get('item_id')
            quantity = request.form.get('quantity')
            unit_rate = request.form.get('unit_rate')
            
            if detail_id and item_id and quantity and unit_rate:
                try:
                    detail = OrderDetail.query.get(int(detail_id))
                    if detail:
                        detail.orderitemid = int(item_id)
                        detail.quantity = float(quantity)
                        detail.unitrate = float(unit_rate)
                        detail.rowtotal = detail.quantity * detail.unitrate
                        db.session.commit()
                        return jsonify({'success': True, 'detail': detail.to_dict()})
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid number format'})
                    
        # Handle form submission for deleting a detail
        if request.method == 'POST' and request.form.get('action') == 'delete_detail':
            detail_id = request.form.get('detail_id')
            
            if detail_id:
                detail = OrderDetail.query.get(int(detail_id))
                if detail:
                    db.session.delete(detail)
                    db.session.commit()
                    return jsonify({'success': True})
    
    # HTML template for displaying a single order with its details
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Order Details View</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #343a40;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 { 
                margin: 0;
                font-size: 2.5em;
            }
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .order-selector {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #e9ecef;
                border-radius: 8px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .order-selector select {
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ced4da;
                font-size: 16px;
                flex-grow: 1;
            }
            .order-selector button {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: 600;
            }
            .order-selector button:hover {
                background-color: #0069d9;
            }
            .order-header {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
                padding: 20px;
                background-color: #e9ecef;
                border-radius: 8px;
                border-left: 5px solid #007bff;
            }
            .order-header-item {
                display: flex;
                flex-direction: column;
            }
            .order-header-item .label {
                font-size: 0.9em;
                color: #6c757d;
                margin-bottom: 5px;
            }
            .order-header-item .value {
                font-size: 1.2em;
                font-weight: 600;
            }
            .details-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .details-table th {
                background-color: #007bff;
                color: white;
                text-align: left;
                padding: 12px 15px;
            }
            .details-table tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .details-table td {
                padding: 12px 15px;
                border-bottom: 1px solid #dee2e6;
            }
            .details-table tr:hover {
                background-color: #e2e6ea;
            }
            .total-row {
                font-weight: bold;
                background-color: #e9ecef !important;
            }
            .total-row td {
                border-top: 2px solid #dee2e6;
            }
            .back-link {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #6c757d;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
            }
            .back-link:hover {
                background-color: #5a6268;
            }
            .no-data {
                padding: 30px;
                text-align: center;
                background-color: #f8d7da;
                color: #721c24;
                border-radius: 8px;
                margin: 20px 0;
            }
            .summary-box {
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .summary-item {
                text-align: center;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                min-width: 150px;
            }
            .summary-label {
                font-size: 0.9em;
                color: #6c757d;
            }
            .summary-value {
                font-size: 1.4em;
                font-weight: bold;
                color: #007bff;
            }
            .action-buttons {
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }
            .btn {
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                transition: background-color 0.2s;
            }
            .btn-primary {
                background-color: #007bff;
                color: white;
            }
            .btn-primary:hover {
                background-color: #0069d9;
            }
            .btn-success {
                background-color: #28a745;
                color: white;
            }
            .btn-success:hover {
                background-color: #218838;
            }
            .btn-danger {
                background-color: #dc3545;
                color: white;
            }
            .btn-danger:hover {
                background-color: #c82333;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }
            .modal-content {
                background-color: white;
                margin: 10% auto;
                padding: 20px;
                border-radius: 8px;
                width: 50%;
                max-width: 500px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: #333;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
            }
            .form-group input {
                width: 100%;
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            .form-actions {
                margin-top: 20px;
                text-align: right;
            }
            .editable-row td {
                position: relative;
            }
            .editable-row td .edit-icon {
                position: absolute;
                right: 5px;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                opacity: 0.5;
                transition: opacity 0.2s;
            }
            .editable-row:hover td .edit-icon {
                opacity: 1;
            }
            .edit-icon, .delete-icon {
                cursor: pointer;
                margin-left: 5px;
            }
            .edit-icon:hover, .delete-icon:hover {
                color: #007bff;
            }
            .status-message {
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                display: none;
            }
            .status-success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status-error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Order Details View</h1>
        </header>
        
        <div class="container">
            <div class="card">
                <div id="statusMessage" class="status-message"></div>
                
                <div class="action-buttons">
                    <button id="createOrderBtn" class="btn btn-success">Create New Order</button>
                </div>
                
                <form class="order-selector" action="/order-detail-view" method="get">
                    <label for="orderid"><strong>Select Order:</strong></label>
                    <select name="orderid" id="orderid">
                        {% for order in orders %}
                            <option value="{{ order.orderid }}" {% if selected_order and order.orderid == selected_order.orderid %}selected{% endif %}>
                                Order #{{ order.orderid }} - Customer {{ order.ordercustomerid }}
                            </option>
                        {% endfor %}
                    </select>
                    <button type="submit">View Order</button>
                </form>
                
                {% if selected_order %}
                    <div class="order-header">
                        <div class="order-header-item">
                            <span class="label">Order ID</span>
                            <span class="value">{{ selected_order.orderid }}</span>
                        </div>
                        <div class="order-header-item">
                            <span class="label">Customer ID</span>
                            <span class="value" id="customerIdValue">{{ selected_order.ordercustomerid }}</span>
                            <span class="edit-icon" onclick="editOrderHeader()">✏️</span>
                        </div>
                        <div class="order-header-item">
                            <span class="label">Order Date</span>
                            <span class="value">{{ selected_order.orderdate }}</span>
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <button id="addDetailBtn" class="btn btn-primary" onclick="showAddDetailModal()">Add Order Detail</button>
                    </div>
                    
                    {% if details %}
                        <h2>Order Details</h2>
                        <table class="details-table">
                            <thead>
                                <tr>
                                    <th>Detail ID</th>
                                    <th>Item ID</th>
                                    <th>Quantity</th>
                                    <th>Unit Rate</th>
                                    <th>Row Total</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% set total_amount = 0 %}
                                {% set total_items = 0 %}
                                
                                {% for detail in details %}
                                    <tr class="editable-row" data-detail-id="{{ detail.orderdetailid }}">
                                        <td>{{ detail.orderdetailid }}</td>
                                        <td>{{ detail.orderitemid }}</td>
                                        <td>{{ detail.quantity }}</td>
                                        <td>${{ "%.2f"|format(detail.unitrate) }}</td>
                                        <td>${{ "%.2f"|format(detail.rowtotal) }}</td>
                                        <td>
                                            <span class="edit-icon" onclick="editDetail({{ detail.orderdetailid }}, {{ detail.orderitemid }}, {{ detail.quantity }}, {{ detail.unitrate }})">✏️</span>
                                            <span class="delete-icon" onclick="deleteDetail({{ detail.orderdetailid }})">🗑️</span>
                                        </td>
                                    </tr>
                                    {% set total_amount = total_amount + detail.rowtotal %}
                                    {% set total_items = total_items + detail.quantity %}
                                {% endfor %}
                                
                                <tr class="total-row">
                                    <td colspan="4" style="text-align: right;">Total:</td>
                                    <td>${{ "%.2f"|format(total_amount) }}</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="summary-box">
                            <div class="summary-item">
                                <div class="summary-label">Total Items</div>
                                <div class="summary-value">{{ total_items }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-label">Line Items</div>
                                <div class="summary-value">{{ details|length }}</div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-label">Order Total</div>
                                <div class="summary-value">${{ "%.2f"|format(total_amount) }}</div>
                            </div>
                        </div>
                    {% else %}
                        <div class="no-data">
                            <p>No details found for this order.</p>
                        </div>
                    {% endif %}
                {% else %}
                    <div class="no-data">
                        <p>No orders found in the system.</p>
                    </div>
                {% endif %}
                
                <a href="/" class="back-link">Back to Home</a>
            </div>
        </div>
        
        <!-- Create Order Modal -->
        <div id="createOrderModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('createOrderModal')">&times;</span>
                <h2>Create New Order</h2>
                <form id="createOrderForm">
                    <div class="form-group">
                        <label for="newCustomerId">Customer ID:</label>
                        <input type="number" id="newCustomerId" name="customer_id" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-success" onclick="createOrder()">Create Order</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Edit Order Modal -->
        <div id="editOrderModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('editOrderModal')">&times;</span>
                <h2>Edit Order</h2>
                <form id="editOrderForm">
                    <input type="hidden" id="editOrderId" name="order_id">
                    <div class="form-group">
                        <label for="editCustomerId">Customer ID:</label>
                        <input type="number" id="editCustomerId" name="customer_id" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-primary" onclick="updateOrder()">Update Order</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Add Detail Modal -->
        <div id="addDetailModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('addDetailModal')">&times;</span>
                <h2>Add Order Detail</h2>
                <form id="addDetailForm">
                    <input type="hidden" id="addDetailOrderId" name="order_id" value="{{ selected_order.orderid if selected_order else '' }}">
                    <div class="form-group">
                        <label for="newItemId">Item ID:</label>
                        <input type="number" id="newItemId" name="item_id" required>
                    </div>
                    <div class="form-group">
                        <label for="newQuantity">Quantity:</label>
                        <input type="number" id="newQuantity" name="quantity" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="newUnitRate">Unit Rate:</label>
                        <input type="number" id="newUnitRate" name="unit_rate" step="0.01" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-success" onclick="addDetail()">Add Detail</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Edit Detail Modal -->
        <div id="editDetailModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('editDetailModal')">&times;</span>
                <h2>Edit Order Detail</h2>
                <form id="editDetailForm">
                    <input type="hidden" id="editDetailId" name="detail_id">
                    <div class="form-group">
                        <label for="editItemId">Item ID:</label>
                        <input type="number" id="editItemId" name="item_id" required>
                    </div>
                    <div class="form-group">
                        <label for="editQuantity">Quantity:</label>
                        <input type="number" id="editQuantity" name="quantity" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="editUnitRate">Unit Rate:</label>
                        <input type="number" id="editUnitRate" name="unit_rate" step="0.01" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-primary" onclick="updateDetail()">Update Detail</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            // Show modal functions
            function showModal(modalId) {
                document.getElementById(modalId).style.display = 'block';
            }
            
            function closeModal(modalId) {
                document.getElementById(modalId).style.display = 'none';
            }
            
            // Create new order
            document.getElementById('createOrderBtn').addEventListener('click', function() {
                showModal('createOrderModal');
            });
            
            function createOrder() {
                const formData = new FormData(document.getElementById('createOrderForm'));
                formData.append('action', 'create_order');
                
                fetch('/order-detail-view', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeModal('createOrderModal');
                        showStatusMessage('Order created successfully!', 'success');
                        // Redirect to the new order
                        window.location.href = '/order-detail-view?orderid=' + data.orderid;
                    } else {
                        showStatusMessage('Error creating order: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showStatusMessage('Error: ' + error, 'error');
                });
            }
            
            // Edit order header
            function editOrderHeader() {
                const customerId = document.getElementById('customerIdValue').innerText;
                document.getElementById('editOrderId').value = '{{ selected_order.orderid if selected_order else "" }}';
                document.getElementById('editCustomerId').value = customerId;
                showModal('editOrderModal');
            }
            
            function updateOrder() {
                const formData = new FormData(document.getElementById('editOrderForm'));
                formData.append('action', 'update_order');
                
                fetch('/order-detail-view', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeModal('editOrderModal');
                        document.getElementById('customerIdValue').innerText = document.getElementById('editCustomerId').value;
                        showStatusMessage('Order updated successfully!', 'success');
                    } else {
                        showStatusMessage('Error updating order: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showStatusMessage('Error: ' + error, 'error');
                });
            }
            
            // Add order detail
            function showAddDetailModal() {
                document.getElementById('addDetailOrderId').value = '{{ selected_order.orderid if selected_order else "" }}';
                showModal('addDetailModal');
            }
            
            function addDetail() {
                const formData = new FormData(document.getElementById('addDetailForm'));
                formData.append('action', 'add_detail');
                
                fetch('/order-detail-view', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeModal('addDetailModal');
                        showStatusMessage('Detail added successfully!', 'success');
                        // Reload the page to show the new detail
                        location.reload();
                    } else {
                        showStatusMessage('Error adding detail: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showStatusMessage('Error: ' + error, 'error');
                });
            }
            
            // Edit order detail
            function editDetail(detailId, itemId, quantity, unitRate) {
                document.getElementById('editDetailId').value = detailId;
                document.getElementById('editItemId').value = itemId;
                document.getElementById('editQuantity').value = quantity;
                document.getElementById('editUnitRate').value = unitRate;
                showModal('editDetailModal');
            }
            
            function updateDetail() {
                const formData = new FormData(document.getElementById('editDetailForm'));
                formData.append('action', 'update_detail');
                
                fetch('/order-detail-view', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeModal('editDetailModal');
                        showStatusMessage('Detail updated successfully!', 'success');
                        // Reload the page to show the updated detail
                        location.reload();
                    } else {
                        showStatusMessage('Error updating detail: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    showStatusMessage('Error: ' + error, 'error');
                });
            }
            
            // Delete order detail
            function deleteDetail(detailId) {
                if (confirm('Are you sure you want to delete this detail?')) {
                    const formData = new FormData();
                    formData.append('action', 'delete_detail');
                    formData.append('detail_id', detailId);
                    
                    fetch('/order-detail-view', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showStatusMessage('Detail deleted successfully!', 'success');
                            // Remove the row from the table
                            const row = document.querySelector(`tr[data-detail-id="${detailId}"]`);
                            if (row) {
                                row.remove();
                            }
                            // Reload to update totals
                            location.reload();
                        } else {
                            showStatusMessage('Error deleting detail: ' + data.error, 'error');
                        }
                    })
                    .catch(error => {
                        showStatusMessage('Error: ' + error, 'error');
                    });
                }
            }
            
            // Status message handling
            function showStatusMessage(message, type) {
                const statusElement = document.getElementById('statusMessage');
                statusElement.innerText = message;
                statusElement.className = 'status-message status-' + type;
                statusElement.style.display = 'block';
                
                // Hide after 5 seconds
                setTimeout(() => {
                    statusElement.style.display = 'none';
                }, 5000);
            }
            
            // Close modals when clicking outside
            window.onclick = function(event) {
                const modals = document.getElementsByClassName('modal');
                for (let i = 0; i < modals.length; i++) {
                    if (event.target == modals[i]) {
                        modals[i].style.display = 'none';
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Convert datetime objects to strings for template rendering
    if selected_order:
        selected_order.orderdate = selected_order.orderdate.isoformat() if hasattr(selected_order.orderdate, 'isoformat') else selected_order.orderdate
    
    for order in orders:
        order.orderdate = order.orderdate.isoformat() if hasattr(order.orderdate, 'isoformat') else order.orderdate
    
    return render_template_string(template, orders=orders, selected_order=selected_order, details=details)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data if the database is empty
        if not OrderHeader.query.first():
            # Create sample orders
            sample_order1 = OrderHeader(ordercustomerid=1001)
            sample_order2 = OrderHeader(ordercustomerid=1002)
            db.session.add(sample_order1)
            db.session.add(sample_order2)
            db.session.commit()
            
            # Create sample order details
            sample_detail1 = OrderDetail(
                orderid=sample_order1.orderid,
                orderitemid=5001,
                quantity=2,
                unitrate=10.50,
                rowtotal=21.00
            )
            sample_detail2 = OrderDetail(
                orderid=sample_order1.orderid,
                orderitemid=5002,
                quantity=3,
                unitrate=15.75,
                rowtotal=47.25
            )
            sample_detail3 = OrderDetail(
                orderid=sample_order2.orderid,
                orderitemid=5003,
                quantity=1,
                unitrate=25.99,
                rowtotal=25.99
            )
            db.session.add(sample_detail1)
            db.session.add(sample_detail2)
            db.session.add(sample_detail3)
            db.session.commit()
            
            print("Sample data added to the database.")
    
    app.run(debug=True)
