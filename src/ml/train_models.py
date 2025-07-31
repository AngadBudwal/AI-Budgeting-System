"""Training script for ML expense classification models."""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

try:
    from .expense_classifier import ExpenseClassifier
    from ..config import settings
except ImportError:
    # For standalone execution
    import sys
    sys.path.append('..')
    from expense_classifier import ExpenseClassifier
    from config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_classifier(data_file: str, save_model: bool = True, model_path: str = None) -> dict:
    """Train the expense classifier and return results."""
    
    logger.info("🤖 Starting ML model training...")
    
    # Create classifier
    classifier = ExpenseClassifier()
    
    # Prepare training data
    logger.info(f"📚 Loading training data from {data_file}")
    features, labels = classifier.prepare_training_data(data_file)
    
    if len(features) == 0:
        raise ValueError("No valid training data found!")
    
    # Display data statistics
    unique_categories = set(labels)
    logger.info(f"📊 Training data statistics:")
    logger.info(f"   - Total samples: {len(features)}")
    logger.info(f"   - Unique categories: {len(unique_categories)}")
    
    # Count samples per category
    category_counts = {}
    for label in labels:
        category_counts[label] = category_counts.get(label, 0) + 1
    
    logger.info("   - Category distribution:")
    for category, count in sorted(category_counts.items()):
        percentage = (count / len(labels)) * 100
        logger.info(f"     • {category}: {count} samples ({percentage:.1f}%)")
    
    # Train models
    logger.info("🏋️ Training ML models...")
    model_scores = classifier.train_models(features, labels)
    
    # Display training results
    if model_scores:
        logger.info("✅ Training completed! Model performance:")
        for model_name, scores in model_scores.items():
            cv_mean = scores['cv_mean']
            cv_std = scores['cv_std']
            test_score = scores['test_score']
            logger.info(f"   • {model_name}:")
            logger.info(f"     - Cross-validation: {cv_mean:.3f} (±{cv_std:.3f})")
            logger.info(f"     - Test accuracy: {test_score:.3f}")
        
        logger.info(f"🏆 Best model: {classifier.best_model_name}")
        logger.info(f"🎯 Final accuracy: {classifier.model_metrics['test_accuracy']:.3f}")
    
    # Save model
    if save_model:
        try:
            # Ensure models directory exists
            models_dir = Path(settings.models_dir)
            models_dir.mkdir(exist_ok=True)
            
            saved_path = classifier.save_model(model_path)
            logger.info(f"💾 Model saved to: {saved_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    # Save training report
    try:
        report = {
            "training_completed_at": datetime.now().isoformat(),
            "data_file": str(data_file),
            "training_samples": len(features),
            "categories": list(unique_categories),
            "category_distribution": category_counts,
            "model_performance": model_scores,
            "best_model": classifier.best_model_name if hasattr(classifier, 'best_model_name') else None,
            "final_accuracy": classifier.model_metrics.get('test_accuracy', 0)
        }
        
        report_path = Path(settings.models_dir) / "training_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Training report saved to: {report_path}")
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to save training report: {e}")
    
    return classifier.model_metrics

def test_model_predictions(model_path: str = None, test_cases: list = None):
    """Test the trained model with sample predictions."""
    
    logger.info("🧪 Testing model predictions...")
    
    # Load model
    classifier = ExpenseClassifier()
    if not classifier.load_model(model_path):
        logger.error("❌ Failed to load model for testing")
        return
    
    # Default test cases
    if not test_cases:
        test_cases = [
            {"vendor": "Microsoft Azure", "description": "Cloud computing services"},
            {"vendor": "Google Ads", "description": "Online advertising campaign"},
            {"vendor": "Delta Airlines", "description": "Business trip to conference"},
            {"vendor": "Staples", "description": "Office supplies and equipment"},
            {"vendor": "Workday", "description": "HR management system"},
            {"vendor": "Edison", "description": "Monthly electricity bill"},
            {"vendor": "McKinsey", "description": "Business strategy consulting"},
            {"vendor": "Coursera", "description": "Online training course"},
            {"vendor": "Apple", "description": "MacBook Pro for development"},
            {"vendor": "Unknown Vendor", "description": "Some random expense"}
        ]
    
    logger.info("🔍 Sample predictions:")
    
    for i, test_case in enumerate(test_cases, 1):
        vendor = test_case['vendor']
        description = test_case.get('description', '')
        
        prediction, confidence = classifier.predict_category(vendor, description)
        
        logger.info(f"   {i}. {vendor} - {description}")
        logger.info(f"      → Predicted: {prediction} (confidence: {confidence:.2f})")

def main():
    """Main function for command line interface."""
    
    parser = argparse.ArgumentParser(description='Train ML expense classification models')
    parser.add_argument('data_file', help='Path to training data CSV file')
    parser.add_argument('--no-save', action='store_true', help='Skip saving the trained model')
    parser.add_argument('--model-path', help='Custom path to save the model')
    parser.add_argument('--test', action='store_true', help='Test the model after training')
    parser.add_argument('--load-test', help='Load existing model and test it')
    
    args = parser.parse_args()
    
    try:
        if args.load_test:
            # Just test an existing model
            test_model_predictions(args.load_test)
        else:
            # Train new model
            if not Path(args.data_file).exists():
                logger.error(f"❌ Training data file not found: {args.data_file}")
                return 1
            
            # Train the model
            results = train_classifier(
                data_file=args.data_file,
                save_model=not args.no_save,
                model_path=args.model_path
            )
            
            # Test if requested
            if args.test:
                test_model_predictions(args.model_path)
            
            logger.info("🎉 Training completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 