"""Machine Learning expense classifier for automatic categorization."""

import pandas as pd
import numpy as np
import pickle
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Warning: scikit-learn not available. Using basic classification.")

try:
    from ..config import settings
    from ..models import CategoryEnum
except ImportError:
    # For standalone execution
    from config import settings
    from models import CategoryEnum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseClassifier:
    """Machine Learning classifier for expense categorization."""
    
    def __init__(self):
        self.models = {}
        self.vectorizer = None
        self.label_encoder = None
        self.is_trained = False
        self.feature_names = []
        self.model_metrics = {}
        
        # Categories to predict
        self.categories = [cat.value for cat in CategoryEnum]
        
        # Text preprocessing patterns
        self.preprocessing_patterns = [
            (r'[^\w\s]', ' '),  # Remove punctuation
            (r'\d+', 'NUM'),    # Replace numbers with NUM token
            (r'\s+', ' '),      # Normalize whitespace
        ]
        
        # Feature engineering keywords for each category
        self.category_keywords = {
            'IT Infrastructure': [
                'cloud', 'hosting', 'server', 'software', 'license', 'api', 'development',
                'infrastructure', 'database', 'security', 'backup', 'storage', 'compute'
            ],
            'Marketing': [
                'advertising', 'campaign', 'promotion', 'marketing', 'social', 'content',
                'brand', 'digital', 'seo', 'analytics', 'creative', 'media', 'ad'
            ],
            'Travel': [
                'flight', 'hotel', 'travel', 'trip', 'transportation', 'accommodation',
                'conference', 'meeting', 'airline', 'rental', 'uber', 'taxi', 'lodging'
            ],
            'Office Supplies': [
                'office', 'supplies', 'stationery', 'desk', 'chair', 'paper', 'pen',
                'furniture', 'equipment', 'materials', 'tools', 'workplace'
            ],
            'Personnel': [
                'payroll', 'salary', 'wages', 'benefits', 'recruitment', 'hiring',
                'contractor', 'employee', 'hr', 'human', 'resources', 'training'
            ],
            'Utilities': [
                'electricity', 'water', 'gas', 'internet', 'phone', 'utility',
                'communication', 'telecom', 'energy', 'power', 'service'
            ],
            'Professional Services': [
                'consulting', 'legal', 'accounting', 'audit', 'advisory', 'professional',
                'service', 'expert', 'law', 'financial', 'business', 'strategy'
            ],
            'Training': [
                'training', 'education', 'course', 'certification', 'learning',
                'development', 'workshop', 'seminar', 'conference', 'skill'
            ],
            'Equipment': [
                'computer', 'laptop', 'hardware', 'equipment', 'machine', 'device',
                'technology', 'electronics', 'monitor', 'printer', 'camera'
            ]
        }

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for feature extraction."""
        if not text:
            return ""
        
        text = str(text).lower().strip()
        
        # Apply preprocessing patterns
        for pattern, replacement in self.preprocessing_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text.strip()

    def extract_features(self, vendor: str, description: str = "") -> str:
        """Extract and combine features from vendor and description."""
        # Combine vendor and description
        combined_text = f"{vendor} {description}".strip()
        
        # Preprocess
        processed_text = self.preprocess_text(combined_text)
        
        # Add keyword-based features
        keyword_features = []
        for category, keywords in self.category_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in processed_text.lower())
            if keyword_count > 0:
                keyword_features.append(f"cat_{category.replace(' ', '_').lower()}_{keyword_count}")
        
        # Combine text and keyword features
        feature_text = processed_text
        if keyword_features:
            feature_text += " " + " ".join(keyword_features)
        
        return feature_text

    def prepare_training_data(self, data_file: str) -> Tuple[List[str], List[str]]:
        """Prepare training data from CSV file."""
        logger.info(f"Loading training data from {data_file}")
        
        try:
            df = pd.read_csv(data_file)
            
            # Check required columns
            required_cols = ['vendor', 'category']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Extract features and labels
            features = []
            labels = []
            
            for _, row in df.iterrows():
                vendor = str(row['vendor'])
                description = str(row.get('description', ''))
                category = str(row['category'])
                
                # Skip invalid entries
                if not vendor or category not in self.categories:
                    continue
                
                feature_text = self.extract_features(vendor, description)
                features.append(feature_text)
                labels.append(category)
            
            logger.info(f"Prepared {len(features)} training samples across {len(set(labels))} categories")
            return features, labels
        
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise

    def train_models(self, features: List[str], labels: List[str]) -> Dict[str, float]:
        """Train multiple ML models and select the best one."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Cannot train ML models.")
            return {}
        
        logger.info("Training ML models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            stop_words='english'
        )
        
        # Fit vectorizer and transform data
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Define models to train
        models_to_train = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'naive_bayes': MultinomialNB()
        }
        
        # Train and evaluate models
        model_scores = {}
        
        for name, model in models_to_train.items():
            logger.info(f"Training {name}...")
            
            # Train model
            model.fit(X_train_vec, y_train)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_vec, y_train, cv=5, scoring='accuracy')
            
            # Test score
            test_score = model.score(X_test_vec, y_test)
            
            # Store model and metrics
            self.models[name] = model
            model_scores[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_score': test_score
            }
            
            logger.info(f"{name} - CV: {cv_scores.mean():.3f} (±{cv_scores.std():.3f}), Test: {test_score:.3f}")
        
        # Select best model based on cross-validation score
        best_model_name = max(model_scores.keys(), key=lambda x: model_scores[x]['cv_mean'])
        self.best_model = self.models[best_model_name]
        self.best_model_name = best_model_name
        
        logger.info(f"Best model: {best_model_name}")
        
        # Generate classification report
        y_pred = self.best_model.predict(X_test_vec)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        self.model_metrics = {
            'best_model': best_model_name,
            'model_scores': model_scores,
            'classification_report': report,
            'training_samples': len(features),
            'test_accuracy': model_scores[best_model_name]['test_score']
        }
        
        self.is_trained = True
        logger.info("Model training completed successfully!")
        
        return model_scores

    def predict_category(self, vendor: str, description: str = "") -> Tuple[str, float]:
        """Predict category for a single expense."""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            # Fallback to rule-based classification
            return self._rule_based_classify(vendor, description), 0.5
        
        try:
            # Extract features
            feature_text = self.extract_features(vendor, description)
            
            # Vectorize
            feature_vec = self.vectorizer.transform([feature_text])
            
            # Predict
            prediction = self.best_model.predict(feature_vec)[0]
            
            # Get probability if available
            if hasattr(self.best_model, 'predict_proba'):
                probabilities = self.best_model.predict_proba(feature_vec)[0]
                max_prob = max(probabilities)
            else:
                max_prob = 0.8  # Default confidence for models without probability
            
            return prediction, max_prob
        
        except Exception as e:
            logger.warning(f"ML prediction failed: {e}. Using fallback classification.")
            return self._rule_based_classify(vendor, description), 0.3

    def _rule_based_classify(self, vendor: str, description: str) -> str:
        """Fallback rule-based classification."""
        vendor_lower = vendor.lower()
        description_lower = description.lower()
        
        # Simple keyword matching
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in vendor_lower or keyword in description_lower:
                    return category
        
        return 'Other'

    def batch_predict(self, expenses: List[Dict]) -> List[Tuple[str, float]]:
        """Predict categories for multiple expenses."""
        predictions = []
        
        for expense in expenses:
            vendor = expense.get('vendor', '')
            description = expense.get('description', '')
            category, confidence = self.predict_category(vendor, description)
            predictions.append((category, confidence))
        
        return predictions

    def save_model(self, model_path: str = None) -> str:
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("No trained model to save.")
        
        if not model_path:
            model_path = settings.models_dir / "expense_classifier.pkl"
        
        model_data = {
            'best_model': self.best_model,
            'vectorizer': self.vectorizer,
            'best_model_name': self.best_model_name,
            'categories': self.categories,
            'model_metrics': self.model_metrics,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {model_path}")
        return str(model_path)

    def load_model(self, model_path: str = None) -> bool:
        """Load trained model from disk."""
        if not model_path:
            model_path = settings.models_dir / "expense_classifier.pkl"
        
        if not Path(model_path).exists():
            logger.warning(f"Model file not found: {model_path}")
            return False
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.best_model = model_data['best_model']
            self.vectorizer = model_data['vectorizer']
            self.best_model_name = model_data['best_model_name']
            self.categories = model_data['categories']
            self.model_metrics = model_data.get('model_metrics', {})
            self.is_trained = True
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Model type: {self.best_model_name}")
            if 'test_accuracy' in self.model_metrics:
                logger.info(f"Model accuracy: {self.model_metrics['test_accuracy']:.3f}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def get_model_info(self) -> Dict:
        """Get information about the trained model."""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        info = {
            "status": "trained",
            "model_type": self.best_model_name,
            "categories": self.categories,
            "sklearn_available": SKLEARN_AVAILABLE
        }
        
        if self.model_metrics:
            info.update(self.model_metrics)
        
        return info

    def evaluate_model(self, test_data_file: str = None) -> Dict:
        """Evaluate model performance on test data."""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        if not test_data_file:
            return self.model_metrics
        
        # Load test data and evaluate
        try:
            features, labels = self.prepare_training_data(test_data_file)
            predictions = [self.predict_category(feat.split()[0], " ".join(feat.split()[1:]))[0] 
                          for feat in features]
            
            # Calculate accuracy
            correct = sum(1 for pred, true in zip(predictions, labels) if pred == true)
            accuracy = correct / len(predictions) if predictions else 0
            
            return {
                "test_accuracy": accuracy,
                "test_samples": len(predictions),
                "correct_predictions": correct
            }
        
        except Exception as e:
            return {"error": str(e)} 