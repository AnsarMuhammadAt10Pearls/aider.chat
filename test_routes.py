import unittest
import json
import sys
from datetime import datetime
from app import app
from models import db, OrderHeader, OrderDetail
from routes import api_bp

class InteractiveTestResult(unittest.TextTestResult):
    """Custom test result class that pauses after each test"""
    
    def addSuccess(self, test):
        super().addSuccess(test)
        print("\n✅ Test passed!")
        if not self.dots:
            self.stream.writeln(self.separator1)
            self.stream.writeln(f"Test: {test.id()}")
            self.stream.writeln(self.separator2)
        self._wait_for_user_input()
    
    def addError(self, test, err):
        super().addError(test, err)
        print("\n❌ Test error!")
        if not self.dots:
            self.stream.writeln(self.separator1)
            self.stream.writeln(f"Test: {test.id()}")
            self.stream.writeln(self.separator2)
        self._wait_for_user_input()
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        print("\n❌ Test failed!")
        if not self.dots:
            self.stream.writeln(self.separator1)
            self.stream.writeln(f"Test: {test.id()}")
            self.stream.writeln(self.separator2)
        self._wait_for_user_input()
    
    def _wait_for_user_input(self):
        input("\nPress Enter to continue to the next test...")

class InteractiveTestRunner(unittest.TextTestRunner):
    """Custom test runner that uses the interactive test result class"""
    
    def __init__(self, **kwargs):
        kwargs['resultclass'] = InteractiveTestResult
        super().__init__(**kwargs)

class OrderAPITestCase(unittest.TestCase):
    """Test case for the Order API endpoints"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a new Flask app for testing to avoid blueprint conflicts
        from flask import Flask
        from models import db
        
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize the database with the test app
        db.init_app(test_app)
        
        # Register the API blueprint with a unique name for testing
        test_app.register_blueprint(api_bp, url_prefix='')
        
        self.app = test_app.test_client()
        self.app_context = test_app.app_context()
        self.app_context.push()
        
        with app.app_context():
            db.create_all()
            
        # Create test data
        db.create_all()
        
        test_order = OrderHeader(
            ordercustomerid=1001,
            orderdate=datetime.now()
        )
        db.session.add(test_order)
        db.session.commit()
        
        # Add order details
        test_detail = OrderDetail(
            orderid=test_order.orderid,
            orderitemid=101,
            quantity=5,
            unitrate=10.0,
            rowtotal=50.0
        )
        db.session.add(test_detail)
        db.session.commit()
        
        self.test_order_id = test_order.orderid
        self.test_detail_id = test_detail.orderdetailid
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()  # Explicitly close all connections in the pool
        self.app_context.pop()
    
    # ============================================================================
    # Order Header Tests
    # ============================================================================
    
    def test_get_all_orders(self):
        """Test retrieving all orders"""
        response = self.app.get('/orders')
        
        print("\nTesting GET /orders")
        print(f"Response Status Code: {response.status_code}")
        print(f"Expected Status Code: 200")
        
        data = json.loads(response.data.decode('utf-8'))
        print(f"\nResponse Data: {json.dumps(data, indent=2)}")
        
        print("\nChecking response format...")
        print(f"Status field exists: {'status' in data}")
        print(f"Status value: {data.get('status')}")
        print(f"Expected status: success")
        
        print("\nChecking data content...")
        items = data.get('data', {}).get('items', [])
        print(f"Number of items: {len(items)}")
        print(f"Expected number: 1")
        
        if items:
            print(f"First item customer ID: {items[0].get('ordercustomerid')}")
            print(f"Expected customer ID: 1001")
        
        # Perform assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data']['items'], list)
        self.assertEqual(len(data['data']['items']), 1)
        self.assertEqual(data['data']['items'][0]['ordercustomerid'], 1001)
    
    def test_get_order(self):
        """Test retrieving a specific order"""
        print(f"\nTesting GET /orders/{self.test_order_id}")
        response = self.app.get(f'/orders/{self.test_order_id}')
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Expected Status Code: 200")
        
        data = json.loads(response.data.decode('utf-8'))
        print(f"\nResponse Data: {json.dumps(data, indent=2)}")
        
        print("\nChecking response format...")
        print(f"Status field exists: {'status' in data}")
        print(f"Status value: {data.get('status')}")
        print(f"Expected status: success")
        
        print("\nChecking data content...")
        print(f"Customer ID: {data.get('data', {}).get('ordercustomerid')}")
        print(f"Expected customer ID: 1001")
        
        # Perform assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['ordercustomerid'], 1001)
        
        # Test non-existent order
        print("\nTesting GET /orders/9999 (non-existent order)")
        response = self.app.get('/orders/9999')
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Expected Status Code: 404")
        
        data = json.loads(response.data.decode('utf-8'))
        print(f"\nResponse Data: {json.dumps(data, indent=2)}")
        
        self.assertEqual(response.status_code, 404)
    
    def test_create_order(self):
        """Test creating a new order"""
        order_data = {
            'ordercustomerid': 1002,
            'orderdate': datetime.now().isoformat()
        }
        response = self.app.post(
            '/orders',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['ordercustomerid'], 1002)
        
        # Test missing required field
        response = self.app.post(
            '/orders',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid date format
        order_data = {
            'ordercustomerid': 1003,
            'orderdate': 'invalid-date'
        }
        response = self.app.post(
            '/orders',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_update_order(self):
        """Test updating an existing order"""
        update_data = {
            'ordercustomerid': 1005
        }
        response = self.app.put(
            f'/orders/{self.test_order_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['ordercustomerid'], 1005)
        
        # Test non-existent order
        response = self.app.put(
            '/orders/9999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # Test invalid date format
        update_data = {
            'orderdate': 'invalid-date'
        }
        response = self.app.put(
            f'/orders/{self.test_order_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_delete_order(self):
        """Test deleting an order"""
        # Create an order to delete
        order_data = {
            'ordercustomerid': 1006
        }
        create_response = self.app.post(
            '/orders',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        new_order_id = json.loads(create_response.data.decode('utf-8'))['data']['orderid']
        
        # Delete the order
        response = self.app.delete(f'/orders/{new_order_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's gone
        get_response = self.app.get(f'/orders/{new_order_id}')
        self.assertEqual(get_response.status_code, 404)
        
        # Test deleting non-existent order
        response = self.app.delete('/orders/9999')
        self.assertEqual(response.status_code, 404)
    
    # ============================================================================
    # Order Detail Tests
    # ============================================================================
    
    def test_get_order_details(self):
        """Test retrieving all details for an order"""
        response = self.app.get(f'/orders/{self.test_order_id}/details')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['orderitemid'], 101)
        
        # Test non-existent order
        response = self.app.get('/orders/9999/details')
        self.assertEqual(response.status_code, 404)
    
    def test_get_order_detail(self):
        """Test retrieving a specific order detail"""
        response = self.app.get(f'/orderdetails/{self.test_detail_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['orderitemid'], 101)
        self.assertEqual(data['data']['quantity'], 5)
        self.assertEqual(data['data']['unitrate'], 10.0)
        self.assertEqual(data['data']['rowtotal'], 50.0)
        
        # Test non-existent detail
        response = self.app.get('/orderdetails/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_create_order_detail(self):
        """Test creating a new order detail"""
        detail_data = {
            'orderitemid': 102,
            'quantity': 3,
            'unitrate': 15.0
        }
        response = self.app.post(
            f'/orders/{self.test_order_id}/details',
            data=json.dumps(detail_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['orderitemid'], 102)
        self.assertEqual(data['data']['quantity'], 3)
        self.assertEqual(data['data']['unitrate'], 15.0)
        self.assertEqual(data['data']['rowtotal'], 45.0)  # 3 * 15.0
        
        # Test missing required fields
        response = self.app.post(
            f'/orders/{self.test_order_id}/details',
            data=json.dumps({'orderitemid': 103}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Test non-existent order
        response = self.app.post(
            '/orders/9999/details',
            data=json.dumps(detail_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_order_detail(self):
        """Test updating an existing order detail"""
        update_data = {
            'quantity': 10,
            'unitrate': 12.5
        }
        response = self.app.put(
            f'/orderdetails/{self.test_detail_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['quantity'], 10)
        self.assertEqual(data['data']['unitrate'], 12.5)
        self.assertEqual(data['data']['rowtotal'], 125.0)  # 10 * 12.5
        
        # Test updating just the item ID
        update_data = {
            'orderitemid': 105
        }
        response = self.app.put(
            f'/orderdetails/{self.test_detail_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['orderitemid'], 105)
        # Row total should remain unchanged
        self.assertEqual(data['data']['rowtotal'], 125.0)
        
        # Test non-existent detail
        response = self.app.put(
            '/orderdetails/9999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_order_detail(self):
        """Test deleting an order detail"""
        # Create a detail to delete
        detail_data = {
            'orderitemid': 106,
            'quantity': 2,
            'unitrate': 20.0
        }
        create_response = self.app.post(
            f'/orders/{self.test_order_id}/details',
            data=json.dumps(detail_data),
            content_type='application/json'
        )
        new_detail_id = json.loads(create_response.data.decode('utf-8'))['data']['orderdetailid']
        
        # Delete the detail
        response = self.app.delete(f'/orderdetails/{new_detail_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's gone
        get_response = self.app.get(f'/orderdetails/{new_detail_id}')
        self.assertEqual(get_response.status_code, 404)
        
        # Test deleting non-existent detail
        response = self.app.delete('/orderdetails/9999')
        self.assertEqual(response.status_code, 404)

    def test_response_format_consistency(self):
        """Test that all API endpoints return a consistent response format"""
        # Test GET endpoints
        endpoints = [
            f'/orders',
            f'/orders/{self.test_order_id}',
            f'/orders/{self.test_order_id}/details',
            f'/orderdetails/{self.test_detail_id}'
        ]
        
        for endpoint in endpoints:
            response = self.app.get(endpoint)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            self.assertIn('status', data)
            self.assertEqual(data['status'], 'success')
            self.assertIn('data', data)

if __name__ == '__main__':
    # Create a test suite with all tests
    suite = unittest.TestLoader().loadTestsFromTestCase(OrderAPITestCase)
    
    # Run the tests with the interactive runner
    InteractiveTestRunner(verbosity=2).run(suite)
