"""Command-line interface for Nsight AI Budgeting System data ingestion."""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

try:
    from .services.data_processor import DataProcessor
    from .database import init_db
    from .config import settings
    from .ml.expense_classifier import ExpenseClassifier
    from .ml.train_models import train_classifier, test_model_predictions
    from .ml.budget_forecaster import BudgetForecaster
    from .ml.anomaly_detector import AnomalyDetector
except ImportError:
    # For standalone execution
    from services.data_processor import DataProcessor
    from database import init_db
    from config import settings
    from ml.expense_classifier import ExpenseClassifier
    from ml.train_models import train_classifier, test_model_predictions
    from ml.budget_forecaster import BudgetForecaster
    from ml.anomaly_detector import AnomalyDetector

class BudgetingCLI:
    """Command-line interface for data operations."""
    
    def __init__(self):
        self.processor = DataProcessor()
    
    def upload_expenses(self, file_path: str) -> None:
        """Upload expenses from CSV file."""
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        if not path.suffix.lower() == '.csv':
            print(f"❌ Error: File must be a CSV file.")
            return
        
        print(f"📁 Processing expense file: {file_path}")
        print("=" * 50)
        
        # Process the file
        result = self.processor.process_expense_csv(path)
        
        # Display results
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")
        
        print(f"📊 Records processed: {result.records_processed}")
        
        if result.errors:
            print(f"\n🚨 Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  • {error}")
        
        if hasattr(self.processor, 'warnings') and self.processor.warnings:
            print(f"\n⚠️  Warnings ({len(self.processor.warnings)}):")
            for warning in self.processor.warnings:
                print(f"  • {warning}")
    
    def upload_budgets(self, file_path: str) -> None:
        """Upload budgets from CSV file."""
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        if not path.suffix.lower() == '.csv':
            print(f"❌ Error: File must be a CSV file.")
            return
        
        print(f"📁 Processing budget file: {file_path}")
        print("=" * 50)
        
        # Process the file
        result = self.processor.process_budget_csv(path)
        
        # Display results
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")
        
        print(f"📊 Records processed: {result.records_processed}")
        
        if result.errors:
            print(f"\n🚨 Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  • {error}")
    
    def show_summary(self) -> None:
        """Show data summary statistics."""
        print("📊 Data Summary")
        print("=" * 50)
        
        summary = self.processor.get_data_summary()
        
        if "error" in summary:
            print(f"❌ Error getting summary: {summary['error']}")
            return
        
        print(f"💰 Total Expenses: {summary['total_expenses']:,} records")
        print(f"💵 Total Spent: ${summary['total_spent']:,.2f}")
        print(f"🎯 Total Budgets: {summary['total_budgets']} records")
        print(f"💰 Total Allocated: ${summary['total_allocated']:,.2f}")
        
        if summary['recent_expenses']:
            print(f"\n📋 Recent Expenses:")
            for exp in summary['recent_expenses']:
                print(f"  • {exp['date']} - ${exp['amount']:,.2f} - {exp['vendor']} ({exp['department']})")
    
    def show_templates(self) -> None:
        """Show CSV template formats."""
        print("📋 CSV Template Formats")
        print("=" * 50)
        
        print("\n💰 Expenses CSV Template:")
        print("Required columns: date, amount, vendor, description, department, category")
        print("Example:")
        print("date,amount,vendor,description,department,category")
        print("2024-01-15,1250.00,AWS,Cloud hosting costs,Engineering,IT Infrastructure")
        print("2024-01-16,750.50,Google Ads,Marketing campaign,Marketing,Marketing")
        
        print("\n🎯 Budgets CSV Template:")
        print("Required columns: department, category, period_start, period_end, allocated_amount")
        print("Example:")
        print("department,category,period_start,period_end,allocated_amount")
        print("Engineering,IT Infrastructure,2024-01-01,2024-01-31,15000.00")
        print("Marketing,Marketing,2024-01-01,2024-01-31,25000.00")
        
        print("\n📝 Notes:")
        print("• Date formats supported: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY")
        print("• Amount can include $ and commas (e.g., $1,250.00)")
        print("• Category is optional for expenses (will auto-categorize)")
        print("• Department abbreviations are supported (e.g., 'Eng' → 'Engineering')")
    
    def create_sample_files(self) -> None:
        """Create sample CSV files for testing."""
        print("📁 Creating sample CSV files...")
        
        # Sample expenses
        expenses_data = [
            ["date", "amount", "vendor", "description", "department", "category"],
            ["2024-01-15", "1250.00", "AWS", "Cloud hosting costs", "Engineering", "IT Infrastructure"],
            ["2024-01-16", "750.50", "Google Ads", "Marketing campaign", "Marketing", "Marketing"],
            ["2024-01-17", "2500.00", "Dell Business", "Laptop purchase", "Engineering", "Equipment"],
            ["2024-01-18", "450.00", "Uber", "Business travel", "Sales", "Travel"],
            ["2024-01-19", "15000.00", "ADP Payroll", "Monthly payroll", "HR", "Personnel"]
        ]
        
        # Sample budgets
        budgets_data = [
            ["department", "category", "period_start", "period_end", "allocated_amount"],
            ["Engineering", "IT Infrastructure", "2024-01-01", "2024-01-31", "15000.00"],
            ["Engineering", "Equipment", "2024-01-01", "2024-01-31", "8000.00"],
            ["Marketing", "Marketing", "2024-01-01", "2024-01-31", "25000.00"],
            ["Sales", "Travel", "2024-01-01", "2024-01-31", "12000.00"],
            ["HR", "Personnel", "2024-01-01", "2024-01-31", "20000.00"]
        ]
        
        # Write sample files
        sample_dir = Path("sample_data")
        sample_dir.mkdir(exist_ok=True)
        
        # Write expenses sample
        expenses_file = sample_dir / "sample_expenses.csv"
        with open(expenses_file, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerows(expenses_data)
        
        # Write budgets sample
        budgets_file = sample_dir / "sample_budgets.csv"
        with open(budgets_file, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerows(budgets_data)
        
        print(f"✅ Created sample files:")
        print(f"  📄 {expenses_file}")
        print(f"  📄 {budgets_file}")
        print(f"\nYou can now test uploads with:")
        print(f"  python -m src.cli upload-expenses {expenses_file}")
        print(f"  python -m src.cli upload-budgets {budgets_file}")

    def train_ml_model(self, data_file: str = None, test: bool = False) -> None:
        """Train ML expense classification model."""
        if not data_file:
            data_file = "data/expenses.csv"  # Default to our synthetic data
        
        if not Path(data_file).exists():
            print(f"❌ Error: Training data file '{data_file}' not found.")
            print(f"Make sure you have expense data uploaded first.")
            return
        
        print(f"🤖 Training ML expense classification model...")
        print(f"📚 Using data from: {data_file}")
        print("=" * 50)
        
        try:
            # Train the model
            results = train_classifier(
                data_file=data_file,
                save_model=True
            )
            
            print(f"\n🎉 Model training completed successfully!")
            
            # Test if requested
            if test:
                print(f"\n🧪 Testing model predictions...")
                test_model_predictions()
        
        except Exception as e:
            print(f"❌ Training failed: {e}")
    
    def test_ml_model(self, model_path: str = None) -> None:
        """Test the trained ML model with sample predictions."""
        print("🧪 Testing ML expense classification model...")
        print("=" * 50)
        
        try:
            test_model_predictions(model_path)
        except Exception as e:
            print(f"❌ Model testing failed: {e}")
    
    def predict_expense(self, vendor: str, description: str = "") -> None:
        """Predict category for a single expense."""
        print(f"🔍 Predicting category for expense...")
        print(f"Vendor: {vendor}")
        print(f"Description: {description}")
        print("=" * 50)
        
        try:
            classifier = ExpenseClassifier()
            
            # Try to load trained model
            if not classifier.load_model():
                print("⚠️  No trained model found. Using rule-based classification.")
            
            prediction, confidence = classifier.predict_category(vendor, description)
            
            print(f"📊 Prediction Results:")
            print(f"  Category: {prediction}")
            print(f"  Confidence: {confidence:.2%}")
            
            if confidence < 0.5:
                print(f"⚠️  Low confidence prediction. Consider manual review.")
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
    
    def ml_model_info(self) -> None:
        """Show information about the trained ML model."""
        print("📊 ML Model Information")
        print("=" * 50)
        
        try:
            classifier = ExpenseClassifier()
            
            if classifier.load_model():
                info = classifier.get_model_info()
                
                print(f"Status: {info['status']}")
                print(f"Model Type: {info.get('model_type', 'Unknown')}")
                print(f"Categories: {len(info.get('categories', []))}")
                
                if 'test_accuracy' in info:
                    print(f"Test Accuracy: {info['test_accuracy']:.2%}")
                
                if 'training_samples' in info:
                    print(f"Training Samples: {info['training_samples']}")
                
                if 'classification_report' in info:
                    report = info['classification_report']
                    print(f"\n📈 Performance Summary:")
                    print(f"  Accuracy: {report.get('accuracy', 0):.2%}")
                    print(f"  Macro Avg F1: {report.get('macro avg', {}).get('f1-score', 0):.2%}")
                    print(f"  Weighted Avg F1: {report.get('weighted avg', {}).get('f1-score', 0):.2%}")
            else:
                print("❌ No trained model found.")
                print("Run 'train-ml' command to train a model first.")
        
        except Exception as e:
            print(f"❌ Error getting model info: {e}")

    def analyze_spending_trends(self, data_file: str = None) -> None:
        """Analyze historical spending patterns and trends."""
        if not data_file:
            data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Error: Data file '{data_file}' not found.")
            return
        
        print(f"📊 Analyzing spending trends from: {data_file}")
        print("=" * 50)
        
        try:
            forecaster = BudgetForecaster()
            
            # Load and analyze data
            if not forecaster.load_historical_data(data_file):
                print("❌ Failed to load historical data")
                return
            
            analysis = forecaster.analyze_spending_patterns()
            
            if 'error' in analysis:
                print(f"❌ Analysis failed: {analysis['error']}")
                return
            
            # Display results
            print("📈 Spending Analysis Results:")
            print(f"  • Total months analyzed: {analysis['total_months']}")
            print(f"  • Total spending: ${analysis['total_spending']:,.2f}")
            print(f"  • Average monthly: ${analysis['average_monthly']:,.2f}")
            print(f"  • Recent average: ${analysis['recent_average']:,.2f}")
            print(f"  • Growth rate: {analysis['growth_rate']:+.1f}%")
            print(f"  • Categories analyzed: {analysis['categories_analyzed']}")
            print(f"  • Departments analyzed: {analysis['departments_analyzed']}")
            
            # Show insights
            insights = forecaster.get_insights()
            if insights.get('insights'):
                print(f"\n💡 Key Insights ({len(insights['insights'])}):")
                for insight in insights['insights']:
                    icon = "⚠️" if insight['type'] == 'warning' else "✅" if insight['type'] == 'positive' else "ℹ️"
                    print(f"  {icon} {insight['title']}: {insight['message']}")
        
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    def forecast_spending(self, months: int = 6, data_file: str = None, save_report: bool = False) -> None:
        """Generate spending forecasts for future months."""
        if not data_file:
            data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Error: Data file '{data_file}' not found.")
            return
        
        print(f"🔮 Generating {months}-month spending forecast...")
        print("=" * 50)
        
        try:
            forecaster = BudgetForecaster()
            
            # Load and analyze data
            if not forecaster.load_historical_data(data_file):
                print("❌ Failed to load historical data")
                return
            
            forecaster.analyze_spending_patterns()
            forecast = forecaster.forecast_spending(months)
            
            if 'error' in forecast:
                print(f"❌ Forecast failed: {forecast['error']}")
                return
            
            # Display monthly forecasts
            print("📅 Monthly Forecasts:")
            total_forecast = 0
            for monthly in forecast['monthly_forecasts']:
                month = monthly['month']
                predicted = monthly['predicted_amount']
                lower = monthly['confidence_lower']
                upper = monthly['confidence_upper']
                
                print(f"  • {month}: ${predicted:,.0f} (${lower:,.0f} - ${upper:,.0f})")
                total_forecast += predicted
            
            print(f"\n💰 Total {months}-month forecast: ${total_forecast:,.0f}")
            
            # Show category forecasts
            if forecast.get('category_forecasts'):
                print(f"\n📊 Top Category Forecasts:")
                cat_sorted = sorted(forecast['category_forecasts'].items(), 
                                  key=lambda x: x[1]['total_forecast'], reverse=True)[:5]
                
                for category, cat_data in cat_sorted:
                    trend_icon = "📈" if cat_data['trend'] == 'increasing' else "📉" if cat_data['trend'] == 'decreasing' else "➡️"
                    print(f"  {trend_icon} {category}: ${cat_data['total_forecast']:,.0f} ({cat_data['trend']})")
            
            # Show department forecasts
            if forecast.get('department_forecasts'):
                print(f"\n🏢 Department Forecasts:")
                dept_sorted = sorted(forecast['department_forecasts'].items(), 
                                   key=lambda x: x[1]['total_forecast'], reverse=True)[:5]
                
                for department, dept_data in dept_sorted:
                    trend_icon = "📈" if dept_data['trend'] == 'increasing' else "📉" if dept_data['trend'] == 'decreasing' else "➡️"
                    print(f"  {trend_icon} {department}: ${dept_data['total_forecast']:,.0f} ({dept_data['trend']})")
            
            # Save report if requested
            if save_report:
                report_file = f"reports/forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                Path("reports").mkdir(exist_ok=True)
                if forecaster.export_forecast_report(report_file, forecast):
                    print(f"\n📄 Forecast report saved: {report_file}")
        
        except Exception as e:
            print(f"❌ Forecast failed: {e}")
    
    def analyze_budget_variance(self, expenses_file: str = None, budgets_file: str = None) -> None:
        """Analyze budget vs actual spending variance."""
        if not expenses_file:
            expenses_file = "data/expenses.csv"
        if not budgets_file:
            budgets_file = "data/budgets.csv"
        
        if not Path(expenses_file).exists():
            print(f"❌ Error: Expenses file '{expenses_file}' not found.")
            return
        
        if not Path(budgets_file).exists():
            print(f"❌ Error: Budgets file '{budgets_file}' not found.")
            return
        
        print("📊 Analyzing Budget vs Actual Variance")
        print("=" * 50)
        
        try:
            forecaster = BudgetForecaster()
            
            # Load historical data
            if not forecaster.load_historical_data(expenses_file):
                print("❌ Failed to load expense data")
                return
            
            # Analyze variance
            variance = forecaster.analyze_budget_variance(budgets_file)
            
            if 'error' in variance:
                print(f"❌ Variance analysis failed: {variance['error']}")
                return
            
            # Display summary
            print("💰 Budget Summary:")
            print(f"  • Total budgeted: ${variance['total_budgeted']:,.2f}")
            print(f"  • Total actual: ${variance['total_actual']:,.2f}")
            print(f"  • Total variance: ${variance['total_variance']:+,.2f}")
            print(f"  • Variance %: {variance['total_variance_percent']:+.1f}%")
            print(f"  • Over budget items: {variance['over_budget_items']}")
            print(f"  • Under budget items: {variance['under_budget_items']}")
            
            # Show largest variances
            print(f"\n📋 Largest Variances:")
            for item in variance['line_items'][:10]:  # Top 10
                status_icon = "🔴" if item['status'] == 'over_budget' else "🟢"
                print(f"  {status_icon} {item['department']} - {item['category']}: "
                      f"${item['variance']:+,.0f} ({item['variance_percent']:+.1f}%)")
        
        except Exception as e:
            print(f"❌ Variance analysis failed: {e}")

    def train_anomaly_detection(self, data_file: str = None) -> None:
        """Train anomaly detection models."""
        if not data_file:
            data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Error: Data file '{data_file}' not found.")
            return
        
        print(f"🤖 Training anomaly detection models...")
        print(f"📚 Using data from: {data_file}")
        print("=" * 50)
        
        try:
            detector = AnomalyDetector()
            
            # Load and train
            if not detector.load_historical_data(data_file):
                print("❌ Failed to load historical data")
                return
            
            results = detector.train_anomaly_models()
            
            if 'error' in results:
                print(f"❌ Training failed: {results['error']}")
                return
            
            # Display results
            print("✅ Anomaly Detection Training Complete!")
            print(f"  📊 Training samples: {results['training_samples']}")
            print(f"  🌲 Isolation forest score: {results['isolation_forest_score']:.3f}")
            print(f"  📈 Statistical baselines: {results['statistical_baseline_score']} items")
            print(f"  🔍 Pattern analysis: {results['pattern_analysis_score']} patterns")
            print(f"  🎯 Anomaly threshold: {results['anomaly_threshold']}")
        
        except Exception as e:
            print(f"❌ Training failed: {e}")
    
    def detect_anomalies(self, data_file: str = None, threshold: float = None, save_report: bool = False) -> None:
        """Detect anomalies in expense data."""
        if not data_file:
            data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Error: Data file '{data_file}' not found.")
            return
        
        print(f"🚨 Detecting anomalies in: {data_file}")
        print("=" * 50)
        
        try:
            detector = AnomalyDetector()
            
            # Set custom threshold if provided
            if threshold:
                detector.anomaly_threshold = threshold
                print(f"🎯 Using custom threshold: {threshold}")
            
            # Load and train
            if not detector.load_historical_data(data_file):
                print("❌ Failed to load historical data")
                return
            
            print("🤖 Training anomaly models...")
            training_results = detector.train_anomaly_models()
            
            if 'error' in training_results:
                print(f"❌ Training failed: {training_results['error']}")
                return
            
            # Detect anomalies
            print("🔍 Analyzing expenses for anomalies...")
            anomaly_results = detector.detect_anomalies()
            
            if 'error' in anomaly_results:
                print(f"❌ Detection failed: {anomaly_results['error']}")
                return
            
            # Display results
            print("📊 Anomaly Detection Results:")
            print(f"  💰 Total expenses analyzed: {anomaly_results['total_expenses']}")
            print(f"  🚨 Anomalies detected: {anomaly_results['anomalies_detected']}")
            print(f"  📈 Anomaly rate: {anomaly_results['anomaly_rate']:.1f}%")
            
            if anomaly_results['severity_breakdown']:
                print(f"  📋 Severity breakdown:")
                for severity, count in anomaly_results['severity_breakdown'].items():
                    print(f"     • {severity}: {count}")
            
            # Show top anomalies
            anomalies = anomaly_results.get('anomalies', [])
            if anomalies:
                print(f"\n🔴 Top Anomalies:")
                for i, anomaly in enumerate(anomalies[:5], 1):
                    severity_icon = "🔴" if anomaly['severity'] == 'High' else "🟡" if anomaly['severity'] == 'Medium' else "🟠"
                    print(f"  {i}. {severity_icon} ${anomaly['amount']:,.0f} - {anomaly['vendor']} ({anomaly['department']})")
                    print(f"      Score: {anomaly['anomaly_score']:.2f} | {anomaly['description']}")
                
                if len(anomalies) > 5:
                    print(f"      ... and {len(anomalies) - 5} more anomalies")
            
            # Get summary insights
            summary = detector.get_anomaly_summary(anomaly_results)
            if summary.get('recommendations'):
                print(f"\n💡 Recommendations:")
                for rec in summary['recommendations']:
                    print(f"  • {rec}")
            
            # Save report if requested
            if save_report:
                report_file = f"reports/anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                Path("reports").mkdir(exist_ok=True)
                if detector.export_anomaly_report(anomaly_results, report_file):
                    print(f"\n📄 Anomaly report saved: {report_file}")
        
        except Exception as e:
            print(f"❌ Anomaly detection failed: {e}")
    
    def anomaly_summary(self, data_file: str = None) -> None:
        """Show anomaly detection summary and insights."""
        if not data_file:
            data_file = "data/expenses.csv"
        
        if not Path(data_file).exists():
            print(f"❌ Error: Data file '{data_file}' not found.")
            return
        
        print(f"📊 Anomaly Detection Summary")
        print("=" * 50)
        
        try:
            detector = AnomalyDetector()
            
            # Quick training and detection
            if not detector.load_historical_data(data_file):
                print("❌ Failed to load data")
                return
            
            detector.train_anomaly_models()
            results = detector.detect_anomalies()
            summary = detector.get_anomaly_summary(results)
            
            if 'error' in summary:
                print(f"❌ Summary failed: {summary['error']}")
                return
            
            if summary.get('message'):
                print(f"✅ {summary['message']}")
                return
            
            # Display summary
            print(f"🚨 Anomaly Rate: {summary['anomaly_rate']:.1f}%")
            print(f"📊 Total Anomalies: {summary['total_anomalies']}")
            
            if summary.get('severity_breakdown'):
                print(f"\n📋 Severity Breakdown:")
                for severity, count in summary['severity_breakdown'].items():
                    print(f"  • {severity}: {count}")
            
            if summary.get('department_summary'):
                print(f"\n🏢 Department Analysis:")
                dept_sorted = sorted(summary['department_summary'].items(), 
                                   key=lambda x: x[1]['count'], reverse=True)[:5]
                
                for dept, data in dept_sorted:
                    print(f"  • {dept}: {data['count']} anomalies, ${data['total_amount']:,.0f}")
            
            if summary.get('recommendations'):
                print(f"\n💡 Key Recommendations:")
                for rec in summary['recommendations']:
                    print(f"  • {rec}")
        
        except Exception as e:
            print(f"❌ Summary failed: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nsight AI Budgeting System - Data Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli upload-expenses data/expenses.csv
  python -m src.cli upload-budgets data/budgets.csv
  python -m src.cli summary
  python -m src.cli templates
  python -m src.cli create-samples
  python -m src.cli train-ml data/expenses.csv
  python -m src.cli test-ml
  python -m src.cli predict "Microsoft Azure" "Cloud computing services"
  python -m src.cli ml-info
  python -m src.cli analyze-trends data/expenses.csv
  python -m src.cli forecast 6 --save-report
  python -m src.cli budget-variance data/expenses.csv data/budgets.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload expenses command
    upload_exp_parser = subparsers.add_parser(
        'upload-expenses', 
        help='Upload expenses from CSV file'
    )
    upload_exp_parser.add_argument(
        'file_path', 
        help='Path to CSV file containing expenses'
    )
    
    # Upload budgets command
    upload_bud_parser = subparsers.add_parser(
        'upload-budgets', 
        help='Upload budgets from CSV file'
    )
    upload_bud_parser.add_argument(
        'file_path', 
        help='Path to CSV file containing budgets'
    )
    
    # Summary command
    subparsers.add_parser(
        'summary', 
        help='Show data summary statistics'
    )
    
    # Templates command
    subparsers.add_parser(
        'templates', 
        help='Show CSV template formats'
    )
    
    # Create samples command
    subparsers.add_parser(
        'create-samples', 
        help='Create sample CSV files for testing'
    )
    
    # Init database command
    subparsers.add_parser(
        'init-db', 
        help='Initialize database tables'
    )
    
    # ML Commands
    # Train ML model command
    train_ml_parser = subparsers.add_parser(
        'train-ml', 
        help='Train ML expense classification model'
    )
    train_ml_parser.add_argument(
        'data_file', 
        nargs='?',
        default=None,
        help='Path to training data CSV file (default: data/expenses.csv)'
    )
    train_ml_parser.add_argument(
        '--test', 
        action='store_true',
        help='Test the model after training'
    )
    
    # Test ML model command
    test_ml_parser = subparsers.add_parser(
        'test-ml', 
        help='Test trained ML model with sample predictions'
    )
    test_ml_parser.add_argument(
        '--model-path', 
        help='Path to model file (optional)'
    )
    
    # Predict expense command
    predict_parser = subparsers.add_parser(
        'predict', 
        help='Predict category for a single expense'
    )
    predict_parser.add_argument(
        'vendor', 
        help='Vendor name'
    )
    predict_parser.add_argument(
        'description', 
        nargs='?',
        default='',
        help='Expense description (optional)'
    )
    
    # ML model info command
    subparsers.add_parser(
        'ml-info', 
        help='Show ML model information and performance'
    )
    
    # Budget Forecasting Commands
    # Analyze spending trends command
    trends_parser = subparsers.add_parser(
        'analyze-trends', 
        help='Analyze historical spending patterns and trends'
    )
    trends_parser.add_argument(
        'data_file', 
        nargs='?',
        default=None,
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    
    # Forecast spending command
    forecast_parser = subparsers.add_parser(
        'forecast', 
        help='Generate spending forecasts for future months'
    )
    forecast_parser.add_argument(
        'months', 
        type=int,
        nargs='?',
        default=6,
        help='Number of months to forecast (default: 6)'
    )
    forecast_parser.add_argument(
        '--data-file', 
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    forecast_parser.add_argument(
        '--save-report', 
        action='store_true',
        help='Save forecast report to JSON file'
    )
    
    # Budget variance command
    variance_parser = subparsers.add_parser(
        'budget-variance', 
        help='Analyze budget vs actual spending variance'
    )
    variance_parser.add_argument(
        'expenses_file', 
        nargs='?',
        default=None,
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    variance_parser.add_argument(
        'budgets_file', 
        nargs='?',
        default=None,
        help='Path to budgets CSV file (default: data/budgets.csv)'
    )
    
    # Anomaly Detection Commands
    # Train anomaly detection command
    train_anomaly_parser = subparsers.add_parser(
        'train-anomaly', 
        help='Train anomaly detection models'
    )
    train_anomaly_parser.add_argument(
        'data_file', 
        nargs='?',
        default=None,
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    
    # Detect anomalies command
    detect_anomaly_parser = subparsers.add_parser(
        'detect-anomalies', 
        help='Detect anomalies in expense data'
    )
    detect_anomaly_parser.add_argument(
        'data_file', 
        nargs='?',
        default=None,
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    detect_anomaly_parser.add_argument(
        '--threshold', 
        type=float,
        help='Custom anomaly threshold (0.0-1.0, default: 0.6)'
    )
    detect_anomaly_parser.add_argument(
        '--save-report', 
        action='store_true',
        help='Save anomaly report to JSON file'
    )
    
    # Anomaly summary command
    anomaly_summary_parser = subparsers.add_parser(
        'anomaly-summary', 
        help='Show anomaly detection summary and insights'
    )
    anomaly_summary_parser.add_argument(
        'data_file', 
        nargs='?',
        default=None,
        help='Path to expenses CSV file (default: data/expenses.csv)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database if needed
    if args.command != 'init-db':
        try:
            init_db()
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("Try running: python -m src.cli init-db")
            return
    
    cli = BudgetingCLI()
    
    try:
        if args.command == 'upload-expenses':
            cli.upload_expenses(args.file_path)
        elif args.command == 'upload-budgets':
            cli.upload_budgets(args.file_path)
        elif args.command == 'summary':
            cli.show_summary()
        elif args.command == 'templates':
            cli.show_templates()
        elif args.command == 'create-samples':
            cli.create_sample_files()
        elif args.command == 'init-db':
            init_db()
            print("✅ Database initialized successfully!")
        elif args.command == 'train-ml':
            cli.train_ml_model(args.data_file, args.test)
        elif args.command == 'test-ml':
            cli.test_ml_model(args.model_path)
        elif args.command == 'predict':
            cli.predict_expense(args.vendor, args.description)
        elif args.command == 'ml-info':
            cli.ml_model_info()
        elif args.command == 'analyze-trends':
            cli.analyze_spending_trends(args.data_file)
        elif args.command == 'forecast':
            cli.forecast_spending(args.months, args.data_file, args.save_report)
        elif args.command == 'budget-variance':
            cli.analyze_budget_variance(args.expenses_file, args.budgets_file)
        elif args.command == 'train-anomaly':
            cli.train_anomaly_detection(args.data_file)
        elif args.command == 'detect-anomalies':
            cli.detect_anomalies(args.data_file, args.threshold, args.save_report)
        elif args.command == 'anomaly-summary':
            cli.anomaly_summary(args.data_file)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if hasattr(cli, 'processor'):
            cli.processor.db.rollback()

if __name__ == "__main__":
    main() 