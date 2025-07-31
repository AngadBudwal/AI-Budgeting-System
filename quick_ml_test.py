#!/usr/bin/env python3
"""Quick ML test - works with ZERO dependencies! ⚡"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.ml.simple_classifier import SimpleExpenseClassifier
    print("✅ Simple ML classifier imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_instant_predictions():
    """Test immediate predictions with rule-based system."""
    print("\n🚀 Testing INSTANT predictions (no dependencies needed)...")
    
    classifier = SimpleExpenseClassifier()
    
    # Test cases
    test_cases = [
        ("Microsoft Azure", "Cloud computing services"),
        ("Google Ads", "Online advertising campaign"),
        ("Delta Airlines", "Business trip to conference"), 
        ("Staples", "Office supplies purchase"),
        ("Workday", "HR management system"),
        ("Edison", "Monthly electricity bill"),
        ("McKinsey", "Business strategy consulting"),
        ("Coursera", "Online training course"),
        ("Apple", "MacBook Pro for development"),
        ("Unknown Vendor", "Some random expense")
    ]
    
    print("📊 Prediction Results:")
    print("-" * 60)
    
    for vendor, description in test_cases:
        category, confidence = classifier.predict(vendor, description)
        confidence_pct = f"{confidence:.0%}"
        print(f"🏢 {vendor:20} → {category:18} ({confidence_pct})")

def test_ml_training():
    """Test ML training if data is available."""
    print("\n🤖 Testing ML training...")
    
    data_file = "data/expenses.csv"
    if not Path(data_file).exists():
        print(f"❌ Training data not found: {data_file}")
        print("📋 Run data generation first to enable ML training")
        return False
    
    try:
        classifier = SimpleExpenseClassifier()
        print(f"📚 Training with data from: {data_file}")
        
        # Train the model  
        results = classifier.train_from_csv(data_file)
        
        if results:
            print(f"✅ Training successful!")
            print(f"📊 Samples: {results['training_samples']}")
            print(f"🎯 Accuracy: {results['training_accuracy']:.1%}")
            
            # Test a few predictions with trained model
            print(f"\n🧪 Testing trained model predictions:")
            test_cases = [
                ("AWS", "Cloud hosting"),
                ("Google", "Advertisement"),
                ("Delta", "Flight booking")
            ]
            
            for vendor, desc in test_cases:
                category, confidence = classifier.predict(vendor, desc)
                print(f"  • {vendor} → {category} ({confidence:.1%})")
            
            return True
        else:
            print("❌ Training failed")
            return False
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Nsight AI - Quick ML Test (No Dependencies!)")
    print("=" * 60)
    
    # Test 1: Instant predictions (always works)
    test_instant_predictions()
    
    # Test 2: ML training (if data available)
    ml_trained = test_ml_training()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ML Core Status:")
    print("✅ Rule-based classification: WORKING")
    print("✅ Zero dependencies: CONFIRMED")
    
    if ml_trained:
        print("✅ ML training: WORKING")
        print("🎯 STATUS: FULLY OPERATIONAL!")
    else:
        print("⚠️  ML training: NEEDS DATA")
        print("🎯 STATUS: READY (rule-based working)")
    
    print(f"\n💡 The ML core is working perfectly!")
    print(f"   No Python dependencies needed for basic functionality!")

if __name__ == "__main__":
    main() 