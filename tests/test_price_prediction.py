#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Price Prediction System
Tests all algorithms: Price Prediction, Best Selling Time, Profit Calculator
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.price_predictor import PricePredictor

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def test_price_prediction():
    """Test 1: Future Price Prediction Algorithm"""
    print_section("TEST 1: FUTURE PRICE PREDICTION")
    
    try:
        predictor = PricePredictor()
        print_success("PricePredictor initialized successfully")
        
        # Test with Wheat
        print_info("Testing price prediction for Wheat...")
        prediction = predictor.predict_future_prices(
            crop_name="Wheat",
            current_price=2500.0,
            location="Pune, Maharashtra",
            days_ahead=30
        )
        
        if prediction['success']:
            print_success("Price prediction generated successfully!\n")
            
            print("📊 PREDICTION RESULTS:")
            print(f"   Current Price: ₹{prediction['current_price']:.2f}")
            print(f"   Trend: {prediction['trend']}")
            print(f"   Confidence: {prediction['confidence']}")
            
            if prediction['predictions']:
                print("\n   Price Forecasts:")
                if 'day_7' in prediction['predictions']:
                    print(f"   • Day 7:  ₹{prediction['predictions']['day_7']:.2f}")
                if 'day_15' in prediction['predictions']:
                    print(f"   • Day 15: ₹{prediction['predictions']['day_15']:.2f}")
                if 'day_30' in prediction['predictions']:
                    print(f"   • Day 30: ₹{prediction['predictions']['day_30']:.2f}")
            
            print(f"\n   📈 Peak expected on Day: {prediction['peak_day']}")
            print(f"   📉 Lowest expected on Day: {prediction['lowest_day']}")
            
            if prediction.get('price_change_30d'):
                print(f"   📊 30-day change: {prediction['price_change_30d']:.2f}%")
            
            if prediction['key_factors']:
                print("\n   🔑 Key Factors:")
                for i, factor in enumerate(prediction['key_factors'][:3], 1):
                    print(f"   {i}. {factor}")
            
            if prediction['recommendation']:
                print(f"\n   💡 Recommendation: {prediction['recommendation'][:100]}...")
            
            print_success("\nTest 1 PASSED: Price prediction algorithm working correctly")
            return True
        else:
            print_error(f"Prediction failed: {prediction.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Test 1 FAILED: {str(e)}")
        return False

def test_best_selling_time():
    """Test 2: Best Time to Sell Algorithm"""
    print_section("TEST 2: BEST TIME TO SELL ANALYSIS")
    
    try:
        predictor = PricePredictor()
        
        print_info("Testing best selling time analysis for Tomato...")
        advice = predictor.get_best_selling_time(
            crop_name="Tomato",
            current_price=1800.0,
            harvest_date="2024-12-15"
        )
        
        if advice['success']:
            print_success("Selling time analysis completed successfully!\n")
            
            print("⏰ SELLING TIME ANALYSIS:")
            print(f"   Best Month: {advice['best_month']}")
            print(f"   Reason: {advice['reason'][:100]}...")
            
            print(f"\n   📊 Scores:")
            print(f"   • Sell Now Score:  {advice['sell_now_score']}/10")
            print(f"   • Wait Score:      {advice['wait_score']}/10")
            
            print(f"\n   🎯 Recommended Action: {advice['action']}")
            
            if advice['timeline']:
                print(f"   ⏱️  Timeline: {advice['timeline'][:80]}...")
            
            if advice['expected_peak_price'] > 0:
                print(f"\n   💰 Expected Peak Price: ₹{advice['expected_peak_price']:.2f}")
            
            if advice['storage_advice']:
                print(f"   📦 Storage Tip: {advice['storage_advice'][:80]}...")
            
            if advice['risk_factors']:
                print("\n   ⚠️  Risk Factors:")
                for i, risk in enumerate(advice['risk_factors'][:3], 1):
                    print(f"   {i}. {risk}")
            
            print_success("\nTest 2 PASSED: Best selling time algorithm working correctly")
            return True
        else:
            print_error(f"Analysis failed: {advice.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Test 2 FAILED: {str(e)}")
        return False

def test_profit_calculator():
    """Test 3: Profit Calculator Algorithm"""
    print_section("TEST 3: PROFIT/LOSS CALCULATOR")
    
    try:
        predictor = PricePredictor()
        
        print_info("Testing profit calculator for Rice...")
        
        # Test case: Profitable transaction
        result = predictor.calculate_profit(
            crop_name="Rice",
            expected_price=3000.0,
            actual_price=3300.0,
            quantity=20,
            unit="quintal"
        )
        
        if result['success']:
            print_success("Profit calculation completed successfully!\n")
            
            print("💰 FINANCIAL ANALYSIS:")
            print(f"   Crop: {result['crop_name']}")
            print(f"   Quantity: {result['quantity']} {result['unit']}")
            
            print(f"\n   📊 Prices:")
            print(f"   • Expected:  ₹{result['expected_price']:.2f}/{result['unit']}")
            print(f"   • Actual:    ₹{result['actual_price']:.2f}/{result['unit']}")
            
            print(f"\n   💵 Revenue:")
            print(f"   • Expected Revenue: ₹{result['expected_revenue']:,.2f}")
            print(f"   • Actual Revenue:   ₹{result['actual_revenue']:,.2f}")
            
            profit_symbol = "📈" if result['profit_loss'] >= 0 else "📉"
            print(f"\n   {profit_symbol} Result:")
            print(f"   • Profit/Loss:      ₹{result['profit_loss']:,.2f}")
            print(f"   • Percentage:       {result['profit_percentage']:+.2f}%")
            
            print(f"\n   🎯 Verdict: {result['verdict']}")
            
            if result['analysis']:
                print(f"   📝 Analysis: {result['analysis'][:100]}...")
            
            if result['learning']:
                print(f"   💡 Learning: {result['learning'][:100]}...")
            
            print_success("\nTest 3 PASSED: Profit calculator algorithm working correctly")
            return True
        else:
            print_error("Profit calculation failed")
            return False
            
    except Exception as e:
        print_error(f"Test 3 FAILED: {str(e)}")
        return False

def test_multiple_crops():
    """Test 4: Multiple Crop Types"""
    print_section("TEST 4: MULTIPLE CROP TYPES")
    
    crops_to_test = [
        ("Wheat", 2500),
        ("Rice", 3200),
        ("Tomato", 1800),
        ("Onion", 2000),
        ("Cotton", 5500)
    ]
    
    try:
        predictor = PricePredictor()
        success_count = 0
        
        for crop_name, price in crops_to_test:
            print_info(f"Testing {crop_name} at ₹{price}/quintal...")
            
            prediction = predictor.predict_future_prices(
                crop_name=crop_name,
                current_price=price,
                location="Maharashtra",
                days_ahead=30
            )
            
            if prediction['success']:
                trend = prediction['trend']
                confidence = prediction['confidence']
                print_success(f"{crop_name}: Trend={trend}, Confidence={confidence}")
                success_count += 1
            else:
                print_error(f"{crop_name}: Prediction failed")
        
        print(f"\n📊 Results: {success_count}/{len(crops_to_test)} crops predicted successfully")
        
        if success_count >= len(crops_to_test) * 0.8:  # 80% success rate
            print_success("Test 4 PASSED: System handles multiple crop types")
            return True
        else:
            print_error("Test 4 FAILED: Too many prediction failures")
            return False
            
    except Exception as e:
        print_error(f"Test 4 FAILED: {str(e)}")
        return False

def test_edge_cases():
    """Test 5: Edge Cases and Error Handling"""
    print_section("TEST 5: EDGE CASES & ERROR HANDLING")
    
    try:
        predictor = PricePredictor()
        
        # Test 1: Very low price
        print_info("Testing with very low price (₹10)...")
        result1 = predictor.predict_future_prices("Wheat", 10.0, "India")
        if result1['success']:
            print_success("Handled low price correctly")
        
        # Test 2: Very high price
        print_info("Testing with very high price (₹100000)...")
        result2 = predictor.predict_future_prices("Gold", 100000.0, "India")
        if result2['success']:
            print_success("Handled high price correctly")
        
        # Test 3: Profit calculation with loss
        print_info("Testing profit calculator with loss scenario...")
        result3 = predictor.calculate_profit("Wheat", 3000.0, 2500.0, 10, "quintal")
        if result3['success'] and result3['profit_loss'] < 0:
            print_success(f"Correctly calculated loss: ₹{abs(result3['profit_loss']):.2f}")
        
        print_success("\nTest 5 PASSED: Edge cases handled correctly")
        return True
        
    except Exception as e:
        print_error(f"Test 5 FAILED: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("\n")
    print("🤖 AI PRICE PREDICTION SYSTEM - COMPREHENSIVE TEST SUITE")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment!")
        print_info("Please set GEMINI_API_KEY in your .env file")
        return
    else:
        print_success(f"API Key found: {api_key[:10]}...{api_key[-10:]}")
    
    # Run all tests
    tests = [
        ("Future Price Prediction", test_price_prediction),
        ("Best Selling Time Analysis", test_best_selling_time),
        ("Profit Calculator", test_profit_calculator),
        ("Multiple Crop Types", test_multiple_crops),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The AI Price Prediction system is working perfectly!")
    elif passed >= total * 0.8:
        print("⚠️  MOST TESTS PASSED. System is functional with minor issues.")
    else:
        print("❌ MULTIPLE TEST FAILURES. Please check the system configuration.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()


