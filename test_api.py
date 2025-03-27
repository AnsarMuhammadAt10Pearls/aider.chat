import unittest
import json
import os
from datetime import datetime, timezone
from app import app, db
from models import OrderHeader, OrderDetail
from sqlalchemy import select

class OrderAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_order_system.db'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test data
            test_order = OrderHeader(ordercustomerid=1001)
            db.session.add(test_order)
            db.session.commit()
            
            test_detail = OrderDetail(
                orderid=test_order.orderid,
                orderitemid=5001,
                quantity=2,
                unitrate=10.50,
                rowtotal=21.00
            )
            db.session.add(test_detail)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists('test_order_system.db'):
            os.remove('test_order_system.db')
    
    # Order Header Tests
    def test_get_all_orders(self):
        response = self.app.get('/api/orders')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['ordercustomerid'], 1001)
        print(f"\nTest: test_get_all_orders")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected data length: 1, Actual: {len(data)}")
        print(f"  Expected customer ID: 1001, Actual: {data[0]['ordercustomerid']}")
    
    def test_get_order(self):
        response = self.app.get('/api/orders/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['orderid'], 1)
        self.assertEqual(data['ordercustomerid'], 1001)
        print(f"\nTest: test_get_order")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected order ID: 1, Actual: {data['orderid']}")
        print(f"  Expected customer ID: 1001, Actual: {data['ordercustomerid']}")
    
    def test_create_order(self):
        order_data = {
            'ordercustomerid': 1002,
            'orderdate': datetime.now(timezone.utc).isoformat()
        }
        response = self.app.post(
            '/api/orders',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['ordercustomerid'], 1002)
        print(f"\nTest: test_create_order")
        print(f"  Expected status code: 201, Actual: {response.status_code}")
        print(f"  Expected customer ID: 1002, Actual: {data['ordercustomerid']}")
    
    def test_update_order(self):
        update_data = {
            'ordercustomerid': 1003
        }
        response = self.app.put(
            '/api/orders/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['ordercustomerid'], 1003)
        print(f"\nTest: test_update_order")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected updated customer ID: 1003, Actual: {data['ordercustomerid']}")
    
    # Order Detail Tests
    def test_get_order_details(self):
        response = self.app.get('/api/orders/1/details')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['orderitemid'], 5001)
        #self.assertEqual(data[0]['orderitemid'], 500100)
        print(f"\nTest: test_get_order_details")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected details count: 1, Actual: {len(data)}")
        print(f"  Expected item ID: 5001, Actual: {data[0]['orderitemid']}")
    
    def test_get_order_detail(self):
        response = self.app.get('/api/orderdetails/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['orderdetailid'], 1)
        self.assertEqual(data['quantity'], 2)
        self.assertEqual(data['unitrate'], 10.5)
        print(f"\nTest: test_get_order_detail")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected detail ID: 1, Actual: {data['orderdetailid']}")
        print(f"  Expected quantity: 2, Actual: {data['quantity']}")
        print(f"  Expected unit rate: 10.5, Actual: {data['unitrate']}")
    
    def test_create_order_detail(self):
        detail_data = {
            'orderitemid': 5002,
            'quantity': 3,
            'unitrate': 15.75
        }
        response = self.app.post(
            '/api/orders/1/details',
            data=json.dumps(detail_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['orderitemid'], 5002)
        self.assertEqual(data['quantity'], 3)
        self.assertEqual(data['unitrate'], 15.75)
        self.assertEqual(data['rowtotal'], 47.25)  # 3 * 15.75
        print(f"\nTest: test_create_order_detail")
        print(f"  Expected status code: 201, Actual: {response.status_code}")
        print(f"  Expected item ID: 5002, Actual: {data['orderitemid']}")
        print(f"  Expected quantity: 3, Actual: {data['quantity']}")
        print(f"  Expected unit rate: 15.75, Actual: {data['unitrate']}")
        print(f"  Expected row total: 47.25, Actual: {data['rowtotal']}")
    
    def test_update_order_detail(self):
        update_data = {
            'quantity': 4,
            'unitrate': 12.25
        }
        response = self.app.put(
            '/api/orderdetails/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 4)
        self.assertEqual(data['unitrate'], 12.25)
        self.assertEqual(data['rowtotal'], 49.0)  # 4 * 12.25
        print(f"\nTest: test_update_order_detail")
        print(f"  Expected status code: 200, Actual: {response.status_code}")
        print(f"  Expected quantity: 4, Actual: {data['quantity']}")
        print(f"  Expected unit rate: 12.25, Actual: {data['unitrate']}")
        print(f"  Expected row total: 49.0, Actual: {data['rowtotal']}")

if __name__ == '__main__':
    unittest.main()
