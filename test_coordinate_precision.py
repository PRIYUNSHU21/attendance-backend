#!/usr/bin/env python3
"""
Test coordinate precision impact on distance calculations
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_coordinate_precision():
    """Test how coordinate precision affects distance calculations."""
    
    print("📐 Testing Coordinate Precision Impact on Distance...")
    
    try:
        from routes.simple_attendance import calculate_distance
        
        # Base coordinates (Kolkata)
        base_lat = 22.6164736
        base_lon = 88.3785728
        
        print(f"\nBase coordinates: ({base_lat}, {base_lon})")
        
        # Test different precision levels
        precision_tests = [
            {
                "name": "Full precision (7 decimals)",
                "lat": 22.6164736,
                "lon": 88.3785728
            },
            {
                "name": "6 decimals", 
                "lat": 22.616474,
                "lon": 88.378573
            },
            {
                "name": "5 decimals",
                "lat": 22.61647,
                "lon": 88.37857
            },
            {
                "name": "4 decimals", 
                "lat": 22.6165,
                "lon": 88.3786
            },
            {
                "name": "3 decimals",
                "lat": 22.616,
                "lon": 88.379
            },
            {
                "name": "2 decimals",
                "lat": 22.62,
                "lon": 88.38
            },
            {
                "name": "1 decimal",
                "lat": 22.6,
                "lon": 88.4
            }
        ]
        
        print("\n🎯 Distance differences due to precision loss:")
        print("-" * 60)
        
        for test in precision_tests:
            distance = calculate_distance(
                base_lat, base_lon,
                test["lat"], test["lon"]
            )
            
            print(f"{test['name']:20} | Coords: ({test['lat']:10}, {test['lon']:10}) | Distance: {distance:8.2f}m")
            
            if distance > 0:
                if distance < 1:
                    impact = "✅ Minimal impact"
                elif distance < 10:
                    impact = "⚠️  Small impact" 
                elif distance < 100:
                    impact = "🔶 Moderate impact"
                else:
                    impact = "🚨 SIGNIFICANT impact"
                    
                print(f"{'':20} | {impact}")
        
        # Test realistic precision scenarios
        print(f"\n📱 Real-world precision scenarios:")
        print("-" * 60)
        
        real_world_tests = [
            {
                "name": "Mobile GPS (typical)",
                "coords": (22.6164736, 88.3785728, 22.6164712, 88.3785703)  # ~3m difference
            },
            {
                "name": "High-precision GPS", 
                "coords": (22.6164736, 88.3785728, 22.6164738, 88.3785730)  # ~20cm difference
            },
            {
                "name": "Low-precision GPS",
                "coords": (22.6164736, 88.3785728, 22.6164800, 88.3785800)  # ~10m difference  
            },
            {
                "name": "Database float precision",
                "coords": (22.616473600000002, 88.378572800000003, 22.6164736, 88.3785728)
            }
        ]
        
        for test in real_world_tests:
            lat1, lon1, lat2, lon2 = test["coords"]
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            
            print(f"{test['name']:25} | Distance: {distance:8.3f}m")
            
            if distance < 1:
                print(f"{'':25} | ✅ Sub-meter precision")
            elif distance < 5:
                print(f"{'':25} | ✅ Good precision")
            elif distance < 50:
                print(f"{'':25} | ⚠️  Acceptable for attendance")
            else:
                print(f"{'':25} | 🚨 Too imprecise for attendance")
        
        # Check if our database/response is rounding coordinates
        print(f"\n🔍 Checking for coordinate rounding in system...")
        
        test_coords = [
            22.616473612345678,  # High precision
            88.378572891011121   # High precision  
        ]
        
        print(f"Original precision: {test_coords[0]:.15f}, {test_coords[1]:.15f}")
        
        # Test float conversion (what we do in calculate_distance)
        converted = [float(coord) for coord in test_coords]
        print(f"After float():     {converted[0]:.15f}, {converted[1]:.15f}")
        
        # Check if precision is lost
        precision_loss = [
            abs(original - converted_val) 
            for original, converted_val in zip(test_coords, converted)
        ]
        
        if all(loss < 1e-15 for loss in precision_loss):
            print("✅ No precision loss in float conversion")
        else:
            print(f"⚠️  Precision loss detected: {precision_loss}")
            
    except ImportError as e:
        print(f"❌ Could not import distance function: {e}")
    
    print(f"\n📊 GPS Coordinate Precision Guide:")
    print("- 1 decimal  (~11 km accuracy)  🚨 UNUSABLE for attendance")
    print("- 2 decimals (~1.1 km accuracy) 🚨 UNUSABLE for attendance") 
    print("- 3 decimals (~110 m accuracy)  🔶 Poor for attendance")
    print("- 4 decimals (~11 m accuracy)   ⚠️  Marginal for attendance")
    print("- 5 decimals (~1.1 m accuracy)  ✅ Good for attendance")
    print("- 6 decimals (~0.11 m accuracy) ✅ Excellent for attendance")
    print("- 7+ decimals (~0.011 m accuracy) ✅ Overkill but perfect")

if __name__ == "__main__":
    test_coordinate_precision()
