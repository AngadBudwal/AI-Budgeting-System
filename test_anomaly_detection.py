"""Test script for anomaly detection system."""

import json
from pathlib import Path
from datetime import datetime

print("🚨 Nsight AI Anomaly Detection System Test")
print("=" * 50)

def test_anomaly_detection():
    """Test the anomaly detection system."""
    
    # Test 1: Train Anomaly Detection
    print("\n📋 Test 1: Training Anomaly Detection Models")
    print("-" * 40)
    
    try:
        from src.ml.anomaly_detector import AnomalyDetector
        
        data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Data file not found: {data_file}")
            print("🔄 Creating synthetic data first...")
            
            # Generate synthetic data if needed
            import subprocess
            result = subprocess.run(['python', '-m', 'src.data_generation.synthetic_data'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Failed to generate synthetic data")
                return False
            print("✅ Synthetic data generated")
        
        detector = AnomalyDetector()
        
        # Load historical data
        if not detector.load_historical_data(data_file):
            print("❌ Failed to load historical data")
            return False
        
        # Train models
        training_results = detector.train_anomaly_models()
        
        if 'error' in training_results:
            print(f"❌ Training failed: {training_results['error']}")
            return False
        
        print("✅ Anomaly detection training completed!")
        print(f"  📊 Training samples: {training_results['training_samples']}")
        print(f"  🌲 Isolation forest score: {training_results['isolation_forest_score']:.3f}")
        print(f"  📈 Statistical baselines: {training_results['statistical_baseline_score']}")
        print(f"  🔍 Pattern analysis: {training_results['pattern_analysis_score']} patterns")
        print(f"  🎯 Anomaly threshold: {training_results['anomaly_threshold']}")
        
        # Test 2: Detect Anomalies
        print("\n📋 Test 2: Anomaly Detection Analysis")
        print("-" * 40)
        
        anomaly_results = detector.detect_anomalies()
        
        if 'error' in anomaly_results:
            print(f"❌ Detection failed: {anomaly_results['error']}")
            return False
        
        print("✅ Anomaly detection completed!")
        print(f"  💰 Total expenses analyzed: {anomaly_results['total_expenses']}")
        print(f"  🚨 Anomalies detected: {anomaly_results['anomalies_detected']}")
        print(f"  📈 Anomaly rate: {anomaly_results['anomaly_rate']:.1f}%")
        
        if anomaly_results['severity_breakdown']:
            print(f"  📋 Severity breakdown:")
            for severity, count in anomaly_results['severity_breakdown'].items():
                print(f"     • {severity}: {count}")
        
        # Test 3: Show Top Anomalies
        anomalies = anomaly_results.get('anomalies', [])
        if anomalies:
            print(f"\n🔴 Top Anomalies Found:")
            for i, anomaly in enumerate(anomalies[:5], 1):
                severity_icon = "🔴" if anomaly['severity'] == 'High' else "🟡" if anomaly['severity'] == 'Medium' else "🟠"
                print(f"  {i}. {severity_icon} ${anomaly['amount']:,.0f} - {anomaly['vendor']} ({anomaly['department']})")
                print(f"      Date: {anomaly['date']} | Score: {anomaly['anomaly_score']:.2f}")
                print(f"      Reasons: {', '.join(anomaly['reasons'])}")
            
            if len(anomalies) > 5:
                print(f"      ... and {len(anomalies) - 5} more anomalies")
        else:
            print("✅ No anomalies detected - spending patterns appear normal")
        
        # Test 4: Anomaly Summary
        print("\n📋 Test 3: Anomaly Summary & Insights")
        print("-" * 40)
        
        summary = detector.get_anomaly_summary(anomaly_results)
        
        if 'error' in summary:
            print(f"❌ Summary failed: {summary['error']}")
            return False
        
        if summary.get('message'):
            print(f"✅ {summary['message']}")
        else:
            print(f"🚨 Anomaly Rate: {summary['anomaly_rate']:.1f}%")
            print(f"📊 Total Anomalies: {summary['total_anomalies']}")
            
            if summary.get('department_summary'):
                print(f"\n🏢 Department Analysis:")
                dept_sorted = sorted(summary['department_summary'].items(), 
                                   key=lambda x: x[1]['count'], reverse=True)[:3]
                
                for dept, data in dept_sorted:
                    print(f"  • {dept}: {data['count']} anomalies, ${data['total_amount']:,.0f}, avg score: {data['avg_anomaly_score']:.2f}")
            
            if summary.get('recommendations'):
                print(f"\n💡 Key Recommendations:")
                for rec in summary['recommendations']:
                    print(f"  • {rec}")
        
        # Test 5: Export Report
        print("\n📋 Test 4: Export Anomaly Report")
        print("-" * 40)
        
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = f"reports/anomaly_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if detector.export_anomaly_report(anomaly_results, report_file):
            print(f"✅ Anomaly report exported: {report_file}")
            
            # Verify report file
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            print(f"  📄 Report contains: {len(report_data)} sections")
            print(f"  📊 File size: {Path(report_file).stat().st_size} bytes")
        else:
            print("❌ Failed to export report")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_commands():
    """Test CLI commands for anomaly detection."""
    print("\n📋 Test 5: CLI Command Testing")
    print("-" * 40)
    
    import subprocess
    
    commands = [
        ['python', '-m', 'src.cli', 'train-anomaly'],
        ['python', '-m', 'src.cli', 'detect-anomalies'],
        ['python', '-m', 'src.cli', 'anomaly-summary'],
    ]
    
    for cmd in commands:
        try:
            print(f"  🔄 Testing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"  ✅ Command successful")
                # Show first few lines of output
                lines = result.stdout.strip().split('\n')[:3]
                for line in lines:
                    if line.strip():
                        print(f"    {line}")
            else:
                print(f"  ❌ Command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Command timed out")
            return False
        except Exception as e:
            print(f"  ❌ Error running command: {e}")
            return False
    
    return True

def show_usage_examples():
    """Show usage examples for anomaly detection."""
    print("\n📋 Usage Examples")
    print("=" * 50)
    
    print("🚨 Anomaly Detection Commands:")
    print()
    print("1. Train anomaly detection models:")
    print("   py -m src.cli train-anomaly")
    print("   py -m src.cli train-anomaly data/expenses.csv")
    print()
    print("2. Detect anomalies in spending:")
    print("   py -m src.cli detect-anomalies")
    print("   py -m src.cli detect-anomalies --threshold 0.7")
    print("   py -m src.cli detect-anomalies --save-report")
    print()
    print("3. Show anomaly summary:")
    print("   py -m src.cli anomaly-summary")
    print("   py -m src.cli anomaly-summary data/custom_expenses.csv")
    print()
    print("🎯 Anomaly threshold:")
    print("  • 0.5-0.6: Sensitive (more anomalies detected)")
    print("  • 0.6-0.7: Balanced (default)")
    print("  • 0.7-0.8: Conservative (fewer false positives)")
    print()
    print("📊 Anomaly scoring:")
    print("  • High (≥0.8): Immediate review required")
    print("  • Medium (0.7-0.8): Review recommended")
    print("  • Low (0.6-0.7): Monitor for patterns")

if __name__ == "__main__":
    try:
        # Run all tests
        success = True
        
        success &= test_anomaly_detection()
        success &= test_cli_commands()
        
        show_usage_examples()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All Anomaly Detection Tests PASSED!")
            print("✅ Anomaly detection system is ready for production use")
            print()
            print("🚀 Next Steps:")
            print("  • Train models: py -m src.cli train-anomaly")
            print("  • Detect anomalies: py -m src.cli detect-anomalies")
            print("  • Set up automated monitoring")
            print("  • Configure alert thresholds")
        else:
            print("❌ Some tests FAILED - check output above")
            print("🔧 Please review the error messages and try again")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc() 