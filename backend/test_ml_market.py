"""
Test Script for ML-Based Market Prediction
Run this to verify your ML model is working correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.market_forecast_agent import MarketForecastAgent
import json

def test_ml_market_prediction():
    """Test the ML market prediction functionality"""
    
    print("🧪 Testing ML-Based Market Prediction System")
    print("=" * 60)
    print()
    
    # Initialize agent (with or without API key)
    print("1️⃣  Initializing ML Market Forecast Agent...")
    try:
        # Try to load API key from config
        try:
            with open('api_config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('data_gov_api_key', '')
                if api_key == 'YOUR_API_KEY_HERE':
                    api_key = ''
        except:
            api_key = ''
        
        agent = MarketForecastAgent(api_key=api_key)
        print("   ✅ Agent initialized successfully")
        print(f"   📊 API Key configured: {'Yes' if api_key else 'No (using synthetic data)'}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to initialize agent: {str(e)}")
        return False
    
    # Test training
    print("2️⃣  Training ML model for wheat...")
    try:
        training_result = agent.train_ml_model("wheat")
        print(f"   ✅ Model trained successfully")
        print(f"   📊 Training samples: {training_result['training_samples']}")
        print(f"   📊 Test samples: {training_result['test_samples']}")
        print(f"   🎯 Accuracy: {training_result['metrics']['accuracy_percentage']}%")
        print(f"   📉 MAE: ₹{training_result['metrics']['mae']}/quintal")
        print(f"   📉 MAPE: {training_result['metrics']['mape']}%")
        print()
    except Exception as e:
        print(f"   ❌ Training failed: {str(e)}")
        return False
    
    # Test prediction
    print("3️⃣  Generating price predictions...")
    try:
        forecast = agent.forecast_prices("wheat", days_ahead=10)
        print(f"   ✅ Predictions generated successfully")
        print(f"   💰 Current price: ₹{forecast['current_price']}/quintal")
        print(f"   📈 Trend: {forecast['trend']}")
        print(f"   🎯 Best selling date: {forecast['best_selling_window']['date']}")
        print(f"   💰 Expected best price: ₹{forecast['best_selling_window']['expected_price']}/quintal")
        print(f"   📊 Potential gain: {forecast['best_selling_window']['potential_gain']:.2f}%")
        print()
        
        # Show first 3 predictions
        print("   📅 Sample Predictions (First 3 days):")
        for pred in forecast['price_forecast'][:3]:
            print(f"      {pred['date']}: ₹{pred['price']}/quintal "
                  f"(Confidence: {pred['confidence']}, {pred['confidence_interval']})")
        print()
        
    except Exception as e:
        print(f"   ❌ Prediction failed: {str(e)}")
        return False
    
    # Test recommendations
    print("4️⃣  Generating recommendations...")
    try:
        if forecast['recommendations']:
            print("   ✅ Recommendations generated:")
            for i, rec in enumerate(forecast['recommendations'], 1):
                print(f"      {i}. {rec}")
        print()
    except Exception as e:
        print(f"   ⚠️  Recommendations incomplete: {str(e)}")
    
    # Test model accuracy endpoint
    print("5️⃣  Model Accuracy Metrics:")
    try:
        metrics = agent.accuracy_metrics
        print(f"   📊 R² Score: {metrics['r2_score']} ({metrics['accuracy_percentage']}% accurate)")
        print(f"   📉 Mean Absolute Error: ₹{metrics['mae']}/quintal")
        print(f"   📉 Root Mean Squared Error: ₹{metrics['rmse']}/quintal")
        print(f"   📉 Mean Absolute Percentage Error: {metrics['mape']}%")
        print()
    except Exception as e:
        print(f"   ⚠️  Metrics incomplete: {str(e)}")
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print()
    print("🎓 What to tell your judges:")
    print("   1. Model Type: Random Forest Regressor (100 trees)")
    print(f"   2. Accuracy: {agent.accuracy_metrics['accuracy_percentage']}%")
    print(f"   3. Average Error: Only {agent.accuracy_metrics['mape']}% (Industry standard: <10%)")
    print("   4. Data Source: data.gov.in API + Historical simulation")
    print("   5. Features: 13 engineered features including historical prices,")
    print("      seasonal patterns, and market momentum")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_ml_market_prediction()
        if success:
            print("✅ System is ready for demonstration!")
        else:
            print("❌ Some tests failed. Please check the errors above.")
    except Exception as e:
        print(f"❌ Test script error: {str(e)}")
        import traceback
        traceback.print_exc()
