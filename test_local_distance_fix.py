#!/usr/bin/env python3
"""
Test the distance calculation fix locally
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_local_distance_calculation():
    """Test the fixed distance calculation function locally."""
    
    print("🧪 Testing Local Distance Calculation Fix...")
    
    try:
        from routes.simple_attendance import calculate_distance
        from decimal import Decimal
        
        print("\n✅ Successfully imported calculate_distance function")
        
        # Test cases that would cause the original error
        test_cases = [
            {
                "name": "Float + Decimal (original error case)",
                "coords": (22.6164736, 88.3785728, Decimal('22.6164736'), Decimal('88.3785728')),
                "expected_distance": 0.0
            },
            {
                "name": "String + Float", 
                "coords": ("22.6164736", "88.3785728", 22.6164736, 88.3785728),
                "expected_distance": 0.0
            },
            {
                "name": "Decimal + Float",
                "coords": (Decimal('22.6164736'), Decimal('88.3785728'), 22.6164736, 88.3785728),
                "expected_distance": 0.0
            },
            {
                "name": "Mixed types (real world scenario)",
                "coords": ("22.6164736", 88.3785728, Decimal('22.7'), Decimal('88.4')),
                "expected_distance": 15000  # Approximately 15km
            },
            {
                "name": "All floats (should always work)",
                "coords": (22.6164736, 88.3785728, 22.7, 88.4),
                "expected_distance": 15000
            }
        ]
        
        print(f"\nTesting {len(test_cases)} type conversion scenarios...")
        
        for i, test_case in enumerate(test_cases, 1):
            lat1, lon1, lat2, lon2 = test_case["coords"]
            print(f"\n{i}. {test_case['name']}:")
            print(f"   Input types: {type(lat1).__name__}, {type(lon1).__name__}, {type(lat2).__name__}, {type(lon2).__name__}")
            print(f"   Values: ({lat1}, {lon1}) -> ({lat2}, {lon2})")
            
            try:
                distance = calculate_distance(lat1, lon1, lat2, lon2)
                print(f"   ✅ SUCCESS: Distance = {distance:.2f} meters")
                
                # Validate distance is reasonable
                if test_case["expected_distance"] == 0.0 and distance < 1.0:
                    print(f"   ✅ Distance validation passed (expected ~0m)")
                elif test_case["expected_distance"] > 0 and 10000 < distance < 20000:
                    print(f"   ✅ Distance validation passed (expected ~15km)")
                else:
                    print(f"   ⚠️  Distance seems unusual for test case")
                    
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                print(f"   🚨 This indicates the type conversion fix didn't work!")
        
        # Test invalid inputs
        print(f"\n🛡️ Testing error handling with invalid inputs...")
        
        invalid_cases = [
            ("invalid", 88.3785728, 22.6164736, 88.3785728),
            (22.6164736, "invalid", 22.6164736, 88.3785728),
            (None, 88.3785728, 22.6164736, 88.3785728),
            (22.6164736, 88.3785728, [], 88.3785728),
        ]
        
        for i, (lat1, lon1, lat2, lon2) in enumerate(invalid_cases, 1):
            try:
                distance = calculate_distance(lat1, lon1, lat2, lon2)
                print(f"   ⚠️  Test {i}: Unexpected success with invalid input")
            except ValueError as e:
                print(f"   ✅ Test {i}: Properly caught ValueError: {e}")
            except Exception as e:
                print(f"   ⚠️  Test {i}: Caught different error: {e}")
    
    except ImportError as e:
        print(f"❌ Could not import calculate_distance: {e}")
        return False
    
    print("\n🎯 Local Distance Calculation Test Complete!")
    return True

if __name__ == "__main__":
    test_local_distance_calculation()
