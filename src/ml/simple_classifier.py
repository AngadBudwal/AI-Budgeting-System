"""Simple expense classifier using only Python standard library - no dependencies required!"""

import json
import re
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
import math

class SimpleExpenseClassifier:
    """Dependency-free expense classifier using basic ML concepts."""
    
    def __init__(self):
        self.is_trained = False
        self.vocabulary = {}
        self.category_counts = {}
        self.word_category_counts = {}
        self.total_documents = 0
        
        # Categories to predict  
        self.categories = [
            'IT Infrastructure', 'Marketing', 'Travel', 'Office Supplies',
            'Personnel', 'Utilities', 'Professional Services', 'Training', 
            'Equipment', 'Other'
        ]
        
        # Enhanced keyword mappings for rule-based classification
        self.category_keywords = {
            'IT Infrastructure': [
                'aws', 'azure', 'cloud', 'hosting', 'server', 'software', 'license', 
                'api', 'development', 'github', 'gitlab', 'docker', 'kubernetes',
                'infrastructure', 'database', 'security', 'backup', 'storage'
            ],
            'Marketing': [
                'google ads', 'facebook', 'instagram', 'linkedin', 'twitter', 'tiktok',
                'advertising', 'campaign', 'promotion', 'marketing', 'social', 'content',
                'brand', 'digital', 'seo', 'analytics', 'creative', 'media', 'ad'
            ],
            'Travel': [
                'delta', 'american airlines', 'united', 'southwest', 'jetblue',
                'flight', 'hotel', 'travel', 'trip', 'transportation', 'accommodation',
                'conference', 'meeting', 'airline', 'rental', 'uber', 'lyft', 'taxi'
            ],
            'Office Supplies': [
                'staples', 'office depot', 'amazon', 'walmart', 'costco',
                'office', 'supplies', 'stationery', 'desk', 'chair', 'paper', 'pen',
                'furniture', 'equipment', 'materials', 'tools', 'workplace'
            ],
            'Personnel': [
                'adp', 'payroll', 'workday', 'bamboohr', 'gusto', 'paychex',
                'salary', 'wages', 'benefits', 'recruitment', 'hiring',
                'contractor', 'employee', 'hr', 'human', 'resources', 'training'
            ],
            'Utilities': [
                'edison', 'pge', 'verizon', 'att', 'comcast', 'spectrum',
                'electricity', 'water', 'gas', 'internet', 'phone', 'utility',
                'communication', 'telecom', 'energy', 'power', 'service'
            ],
            'Professional Services': [
                'deloitte', 'pwc', 'kpmg', 'mckinsey', 'bcg', 'accenture',
                'consulting', 'legal', 'accounting', 'audit', 'advisory', 'professional',
                'service', 'expert', 'law', 'financial', 'business', 'strategy'
            ],
            'Training': [
                'coursera', 'udemy', 'linkedin learning', 'pluralsight', 'skillshare',
                'training', 'education', 'course', 'certification', 'learning',
                'development', 'workshop', 'seminar', 'conference', 'skill'
            ],
            'Equipment': [
                'apple', 'dell', 'hp', 'lenovo', 'microsoft', 'canon', 'epson',
                'computer', 'laptop', 'hardware', 'equipment', 'machine', 'device',
                'technology', 'electronics', 'monitor', 'printer', 'camera'
            ]
        }

    def preprocess_text(self, text: str) -> List[str]:
        """Basic text preprocessing."""
        if not text:
            return []
        
        # Convert to lowercase and remove special chars
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\d+', 'NUM', text)  # Replace numbers
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple tokenization
        words = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        return words

    def rule_based_classify(self, vendor: str, description: str = "") -> Tuple[str, float]:
        """Enhanced rule-based classification."""
        text = f"{vendor} {description}".lower()
        
        # Direct vendor matching (highest confidence)
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # Higher confidence for exact vendor matches
                    if keyword in vendor.lower():
                        return category, 0.95
                    else:
                        return category, 0.80
        
        # Fallback patterns
        if any(word in text for word in ['cloud', 'software', 'tech', 'system']):
            return 'IT Infrastructure', 0.60
        elif any(word in text for word in ['ad', 'campaign', 'promotion']):
            return 'Marketing', 0.60
        elif any(word in text for word in ['flight', 'hotel', 'travel']):
            return 'Travel', 0.60
        elif any(word in text for word in ['office', 'supply', 'desk']):
            return 'Office Supplies', 0.60
        elif any(word in text for word in ['salary', 'payroll', 'employee']):
            return 'Personnel', 0.60
        
        return 'Other', 0.30

    def train_naive_bayes(self, training_data: List[Dict]) -> Dict:
        """Train a simple Naive Bayes classifier."""
        print("🤖 Training Naive Bayes classifier...")
        
        # Reset training state
        self.vocabulary = {}
        self.category_counts = Counter()
        self.word_category_counts = {}
        self.total_documents = 0
        
        # Process training data
        word_id = 0
        for doc in training_data:
            vendor = doc.get('vendor', '')
            description = doc.get('description', '')
            category = doc.get('category', 'Other')
            
            # Combine vendor and description
            text = f"{vendor} {description}"
            words = self.preprocess_text(text)
            
            # Count category occurrences
            self.category_counts[category] += 1
            self.total_documents += 1
            
            # Count word-category pairs
            if category not in self.word_category_counts:
                self.word_category_counts[category] = Counter()
            
            for word in words:
                if word not in self.vocabulary:
                    self.vocabulary[word] = word_id
                    word_id += 1
                
                self.word_category_counts[category][word] += 1
        
        self.is_trained = True
        
        # Calculate training accuracy
        correct = 0
        total = len(training_data)
        
        for doc in training_data:
            vendor = doc.get('vendor', '')
            description = doc.get('description', '')
            true_category = doc.get('category', 'Other')
            
            predicted_category, _ = self.predict_naive_bayes(vendor, description)
            if predicted_category == true_category:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        print(f"✅ Training completed!")
        print(f"📊 Training samples: {total}")
        print(f"📈 Categories: {len(self.category_counts)}")
        print(f"🎯 Training accuracy: {accuracy:.3f}")
        
        return {
            'training_samples': total,
            'categories': len(self.category_counts),
            'vocabulary_size': len(self.vocabulary),
            'training_accuracy': accuracy
        }

    def predict_naive_bayes(self, vendor: str, description: str = "") -> Tuple[str, float]:
        """Predict using Naive Bayes."""
        if not self.is_trained:
            return self.rule_based_classify(vendor, description)
        
        text = f"{vendor} {description}"
        words = self.preprocess_text(text)
        
        if not words:
            return self.rule_based_classify(vendor, description)
        
        # Calculate log probabilities for each category
        category_scores = {}
        
        for category in self.categories:
            if category not in self.category_counts:
                continue
                
            # Prior probability: P(category)
            prior = self.category_counts[category] / self.total_documents
            log_prob = math.log(prior)
            
            # Likelihood: P(word|category)
            category_word_count = sum(self.word_category_counts.get(category, {}).values())
            vocab_size = len(self.vocabulary)
            
            for word in words:
                if word in self.vocabulary:
                    word_count = self.word_category_counts.get(category, {}).get(word, 0)
                    # Laplace smoothing
                    likelihood = (word_count + 1) / (category_word_count + vocab_size)
                    log_prob += math.log(likelihood)
            
            category_scores[category] = log_prob
        
        if not category_scores:
            return self.rule_based_classify(vendor, description)
        
        # Get best category
        best_category = max(category_scores.keys(), key=lambda x: category_scores[x])
        
        # Convert log probability to confidence score
        max_score = max(category_scores.values())
        min_score = min(category_scores.values())
        
        if max_score == min_score:
            confidence = 0.5
        else:
            # Normalize to 0.5-0.95 range
            normalized = (category_scores[best_category] - min_score) / (max_score - min_score)
            confidence = 0.5 + (normalized * 0.45)
        
        return best_category, confidence

    def predict(self, vendor: str, description: str = "") -> Tuple[str, float]:
        """Main prediction method."""
        if self.is_trained:
            return self.predict_naive_bayes(vendor, description)
        else:
            return self.rule_based_classify(vendor, description)

    def load_training_data(self, csv_file: str) -> List[Dict]:
        """Load training data from CSV file."""
        training_data = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'vendor' in row and 'category' in row:
                        training_data.append({
                            'vendor': row['vendor'],
                            'description': row.get('description', ''),
                            'category': row['category']
                        })
        except Exception as e:
            print(f"❌ Error loading training data: {e}")
            return []
        
        return training_data

    def train_from_csv(self, csv_file: str) -> Dict:
        """Train the classifier from a CSV file."""
        training_data = self.load_training_data(csv_file)
        
        if not training_data:
            print(f"❌ No training data loaded from {csv_file}")
            return {}
        
        return self.train_naive_bayes(training_data)

    def batch_predict(self, expenses: List[Dict]) -> List[Tuple[str, float]]:
        """Predict categories for multiple expenses."""
        predictions = []
        
        for expense in expenses:
            vendor = expense.get('vendor', '')
            description = expense.get('description', '')
            category, confidence = self.predict(vendor, description)
            predictions.append((category, confidence))
        
        return predictions

    def evaluate(self, test_data: List[Dict]) -> Dict:
        """Evaluate model performance."""
        if not test_data:
            return {'error': 'No test data provided'}
        
        correct = 0
        total = len(test_data)
        category_results = {}
        
        for doc in test_data:
            vendor = doc.get('vendor', '')
            description = doc.get('description', '')
            true_category = doc.get('category', 'Other')
            
            predicted_category, confidence = self.predict(vendor, description)
            
            if true_category not in category_results:
                category_results[true_category] = {'correct': 0, 'total': 0}
            
            category_results[true_category]['total'] += 1
            
            if predicted_category == true_category:
                correct += 1
                category_results[true_category]['correct'] += 1
        
        overall_accuracy = correct / total if total > 0 else 0
        
        return {
            'overall_accuracy': overall_accuracy,
            'correct_predictions': correct,
            'total_predictions': total,
            'category_breakdown': category_results
        }

    def get_model_info(self) -> Dict:
        """Get model information."""
        info = {
            'model_type': 'Simple Naive Bayes' if self.is_trained else 'Rule-based',
            'is_trained': self.is_trained,
            'categories': self.categories,
            'dependencies': 'None (Python standard library only)'
        }
        
        if self.is_trained:
            info.update({
                'vocabulary_size': len(self.vocabulary),
                'total_training_docs': self.total_documents,
                'categories_trained': len(self.category_counts)
            })
        
        return info 