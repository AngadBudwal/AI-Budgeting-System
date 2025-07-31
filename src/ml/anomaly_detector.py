"""Anomaly detection system for identifying unusual spending patterns - no dependencies!"""

import csv
import json
import math
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path

class IsolationTree:
    """Single isolation tree for anomaly detection."""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.root = None
        self.size = 0
    
    def fit(self, data: List[List[float]], current_depth: int = 0) -> 'TreeNode':
        """Build isolation tree recursively."""
        if current_depth >= self.max_depth or len(data) <= 1:
            return TreeNode(size=len(data), is_leaf=True)
        
        # Randomly select feature and split point
        n_features = len(data[0]) if data else 0
        if n_features == 0:
            return TreeNode(size=len(data), is_leaf=True)
        
        split_feature = random.randint(0, n_features - 1)
        feature_values = [row[split_feature] for row in data]
        
        if len(set(feature_values)) <= 1:
            return TreeNode(size=len(data), is_leaf=True)
        
        min_val, max_val = min(feature_values), max(feature_values)
        split_value = random.uniform(min_val, max_val)
        
        # Split data
        left_data = [row for row in data if row[split_feature] < split_value]
        right_data = [row for row in data if row[split_feature] >= split_value]
        
        if len(left_data) == 0 or len(right_data) == 0:
            return TreeNode(size=len(data), is_leaf=True)
        
        # Create internal node
        node = TreeNode(
            split_feature=split_feature,
            split_value=split_value,
            size=len(data),
            is_leaf=False
        )
        
        # Recursively build subtrees
        node.left = self.fit(left_data, current_depth + 1)
        node.right = self.fit(right_data, current_depth + 1)
        
        return node
    
    def path_length(self, point: List[float], node: 'TreeNode' = None, depth: int = 0) -> float:
        """Calculate path length from root to leaf for a point."""
        if node is None:
            node = self.root
        
        if node.is_leaf:
            # Estimate path length for leaf with multiple points
            return depth + self._average_path_length(node.size)
        
        if point[node.split_feature] < node.split_value:
            return self.path_length(point, node.left, depth + 1)
        else:
            return self.path_length(point, node.right, depth + 1)
    
    def _average_path_length(self, n: int) -> float:
        """Estimate average path length for n points."""
        if n <= 1:
            return 0
        return 2 * (math.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)

class TreeNode:
    """Node in isolation tree."""
    
    def __init__(self, split_feature: int = None, split_value: float = None, 
                 size: int = 0, is_leaf: bool = False):
        self.split_feature = split_feature
        self.split_value = split_value
        self.size = size
        self.is_leaf = is_leaf
        self.left = None
        self.right = None

class AnomalyDetector:
    """Advanced anomaly detection using multiple methods."""
    
    def __init__(self):
        self.historical_data = []
        self.is_trained = False
        
        # Isolation Forest parameters
        self.n_trees = 100
        self.subsample_size = 256
        self.trees = []
        
        # Statistical parameters
        self.z_score_threshold = 3.0
        self.iqr_multiplier = 1.5
        
        # Pattern analysis
        self.normal_patterns = {}
        self.department_baselines = {}
        self.category_baselines = {}
        self.vendor_patterns = {}
        
        # Anomaly scoring
        self.anomaly_threshold = 0.6  # Isolation score threshold
        
    def load_historical_data(self, expenses_csv: str) -> bool:
        """Load historical expense data for training."""
        try:
            self.historical_data = []
            
            with open(expenses_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse date
                        date_str = row.get('date', '')
                        date_obj = self._parse_date(date_str)
                        
                        if date_obj:
                            expense = {
                                'date': date_obj,
                                'amount': float(row.get('amount', 0)),
                                'vendor': row.get('vendor', ''),
                                'description': row.get('description', ''),
                                'department': row.get('department', ''),
                                'category': row.get('category', 'Other')
                            }
                            self.historical_data.append(expense)
                    except (ValueError, TypeError):
                        continue
            
            print(f"📚 Loaded {len(self.historical_data)} expense records for anomaly training")
            return len(self.historical_data) > 0
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def train_anomaly_models(self) -> Dict:
        """Train all anomaly detection models."""
        if not self.historical_data:
            return {'error': 'No historical data available'}
        
        print("🤖 Training anomaly detection models...")
        
        # Prepare features for isolation forest
        features = self._extract_features()
        
        # Train isolation forest
        isolation_score = self._train_isolation_forest(features)
        
        # Calculate statistical baselines
        statistical_score = self._calculate_statistical_baselines()
        
        # Analyze spending patterns
        pattern_score = self._analyze_spending_patterns()
        
        self.is_trained = True
        
        return {
            'training_samples': len(self.historical_data),
            'isolation_forest_score': isolation_score,
            'statistical_baseline_score': statistical_score,
            'pattern_analysis_score': pattern_score,
            'anomaly_threshold': self.anomaly_threshold
        }
    
    def _extract_features(self) -> List[List[float]]:
        """Extract numerical features for isolation forest."""
        features = []
        
        for expense in self.historical_data:
            # Feature vector: [amount, day_of_month, day_of_week, month, hour_if_available]
            date_obj = expense['date']
            feature_vector = [
                math.log(expense['amount'] + 1),  # Log transform amount
                date_obj.day,  # Day of month (1-31)
                date_obj.weekday(),  # Day of week (0-6)
                date_obj.month,  # Month (1-12)
                date_obj.hour if hasattr(date_obj, 'hour') else 12  # Hour or default
            ]
            features.append(feature_vector)
        
        return features
    
    def _train_isolation_forest(self, features: List[List[float]]) -> float:
        """Train custom isolation forest."""
        if len(features) < 10:
            return 0.0
        
        print(f"🌲 Training isolation forest with {self.n_trees} trees...")
        
        self.trees = []
        subsample_size = min(self.subsample_size, len(features))
        
        for i in range(self.n_trees):
            # Random subsample
            sample_indices = random.sample(range(len(features)), subsample_size)
            sample_data = [features[idx] for idx in sample_indices]
            
            # Build tree
            tree = IsolationTree()
            tree.root = tree.fit(sample_data)
            self.trees.append(tree)
        
        # Calculate average path length for training data
        path_lengths = []
        for feature_vector in features[:100]:  # Sample for efficiency
            avg_path = self._calculate_isolation_score(feature_vector)
            path_lengths.append(avg_path)
        
        training_score = statistics.mean(path_lengths) if path_lengths else 0
        print(f"✅ Isolation forest trained. Average training score: {training_score:.3f}")
        
        return training_score
    
    def _calculate_statistical_baselines(self) -> float:
        """Calculate statistical baselines for normal spending."""
        print("📊 Calculating statistical baselines...")
        
        # Department baselines
        dept_amounts = defaultdict(list)
        for expense in self.historical_data:
            dept_amounts[expense['department']].append(expense['amount'])
        
        self.department_baselines = {}
        for dept, amounts in dept_amounts.items():
            if len(amounts) >= 3:
                self.department_baselines[dept] = {
                    'mean': statistics.mean(amounts),
                    'std': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                    'median': statistics.median(amounts),
                    'q1': statistics.quantiles(amounts, n=4)[0] if len(amounts) >= 4 else min(amounts),
                    'q3': statistics.quantiles(amounts, n=4)[2] if len(amounts) >= 4 else max(amounts)
                }
        
        # Category baselines
        cat_amounts = defaultdict(list)
        for expense in self.historical_data:
            cat_amounts[expense['category']].append(expense['amount'])
        
        self.category_baselines = {}
        for cat, amounts in cat_amounts.items():
            if len(amounts) >= 3:
                self.category_baselines[cat] = {
                    'mean': statistics.mean(amounts),
                    'std': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                    'median': statistics.median(amounts),
                    'q1': statistics.quantiles(amounts, n=4)[0] if len(amounts) >= 4 else min(amounts),
                    'q3': statistics.quantiles(amounts, n=4)[2] if len(amounts) >= 4 else max(amounts)
                }
        
        print(f"✅ Statistical baselines calculated for {len(self.department_baselines)} departments, {len(self.category_baselines)} categories")
        
        return len(self.department_baselines) + len(self.category_baselines)
    
    def _analyze_spending_patterns(self) -> float:
        """Analyze spending patterns for vendor and timing anomalies."""
        print("🔍 Analyzing spending patterns...")
        
        # Vendor spending patterns
        vendor_amounts = defaultdict(list)
        vendor_frequencies = defaultdict(int)
        
        for expense in self.historical_data:
            vendor = expense['vendor'].lower().strip()
            vendor_amounts[vendor].append(expense['amount'])
            vendor_frequencies[vendor] += 1
        
        self.vendor_patterns = {}
        for vendor, amounts in vendor_amounts.items():
            if len(amounts) >= 2:
                self.vendor_patterns[vendor] = {
                    'avg_amount': statistics.mean(amounts),
                    'frequency': vendor_frequencies[vendor],
                    'amount_std': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                    'max_amount': max(amounts),
                    'min_amount': min(amounts)
                }
        
        # Daily/monthly patterns
        daily_amounts = defaultdict(list)
        monthly_amounts = defaultdict(list)
        
        for expense in self.historical_data:
            day_key = expense['date'].weekday()  # 0=Monday, 6=Sunday
            month_key = expense['date'].month
            
            daily_amounts[day_key].append(expense['amount'])
            monthly_amounts[month_key].append(expense['amount'])
        
        self.normal_patterns = {
            'daily': {day: statistics.mean(amounts) for day, amounts in daily_amounts.items()},
            'monthly': {month: statistics.mean(amounts) for month, amounts in monthly_amounts.items()},
            'vendor_count': len(self.vendor_patterns)
        }
        
        print(f"✅ Pattern analysis completed. {len(self.vendor_patterns)} vendor patterns identified")
        
        return len(self.vendor_patterns)
    
    def _calculate_isolation_score(self, feature_vector: List[float]) -> float:
        """Calculate isolation score for a feature vector."""
        if not self.trees:
            return 0.5
        
        path_lengths = []
        for tree in self.trees:
            length = tree.path_length(feature_vector, tree.root)
            path_lengths.append(length)
        
        avg_path_length = statistics.mean(path_lengths)
        
        # Normalize to anomaly score (higher = more anomalous)
        c = self._average_path_length(self.subsample_size)
        if c == 0:
            return 0.5
        
        score = 2 ** (-avg_path_length / c)
        return score
    
    def _average_path_length(self, n: int) -> float:
        """Calculate average path length for n points."""
        if n <= 1:
            return 0
        return 2 * (math.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)
    
    def detect_anomalies(self, expenses: List[Dict] = None) -> Dict:
        """Detect anomalies in expense data."""
        if not self.is_trained:
            return {'error': 'Models not trained. Run train_anomaly_models() first.'}
        
        if expenses is None:
            expenses = self.historical_data
        
        print(f"🔍 Detecting anomalies in {len(expenses)} expenses...")
        
        anomalies = []
        
        for i, expense in enumerate(expenses):
            anomaly_score, reasons = self._score_expense_anomaly(expense)
            
            if anomaly_score >= self.anomaly_threshold:
                severity = self._classify_severity(anomaly_score)
                
                anomaly = {
                    'expense_index': i,
                    'date': expense['date'].strftime('%Y-%m-%d'),
                    'amount': expense['amount'],
                    'vendor': expense['vendor'],
                    'department': expense['department'],
                    'category': expense['category'],
                    'anomaly_score': anomaly_score,
                    'severity': severity,
                    'reasons': reasons,
                    'description': self._generate_anomaly_description(expense, reasons)
                }
                
                anomalies.append(anomaly)
        
        # Sort by anomaly score (highest first)
        anomalies.sort(key=lambda x: x['anomaly_score'], reverse=True)
        
        # Statistics
        total_expenses = len(expenses)
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_expenses * 100) if total_expenses > 0 else 0
        
        severity_counts = Counter([a['severity'] for a in anomalies])
        
        return {
            'total_expenses': total_expenses,
            'anomalies_detected': anomaly_count,
            'anomaly_rate': anomaly_rate,
            'severity_breakdown': dict(severity_counts),
            'anomalies': anomalies,
            'threshold_used': self.anomaly_threshold
        }
    
    def _score_expense_anomaly(self, expense: Dict) -> Tuple[float, List[str]]:
        """Score an individual expense for anomalies."""
        reasons = []
        scores = []
        
        # 1. Isolation Forest Score
        feature_vector = [
            math.log(expense['amount'] + 1),
            expense['date'].day,
            expense['date'].weekday(),
            expense['date'].month,
            expense['date'].hour if hasattr(expense['date'], 'hour') else 12
        ]
        
        isolation_score = self._calculate_isolation_score(feature_vector)
        scores.append(isolation_score)
        
        if isolation_score > 0.6:
            reasons.append(f"Unusual spending pattern (isolation score: {isolation_score:.2f})")
        
        # 2. Statistical Outlier Detection
        dept = expense['department']
        if dept in self.department_baselines:
            baseline = self.department_baselines[dept]
            z_score = abs((expense['amount'] - baseline['mean']) / baseline['std']) if baseline['std'] > 0 else 0
            
            if z_score > self.z_score_threshold:
                scores.append(min(z_score / 10, 1.0))  # Normalize
                reasons.append(f"Unusual amount for {dept} department (Z-score: {z_score:.1f})")
        
        # 3. Category Analysis
        cat = expense['category']
        if cat in self.category_baselines:
            baseline = self.category_baselines[cat]
            iqr = baseline['q3'] - baseline['q1']
            lower_bound = baseline['q1'] - self.iqr_multiplier * iqr
            upper_bound = baseline['q3'] + self.iqr_multiplier * iqr
            
            if expense['amount'] < lower_bound or expense['amount'] > upper_bound:
                outlier_score = min(abs(expense['amount'] - baseline['median']) / baseline['median'], 1.0) if baseline['median'] > 0 else 0
                scores.append(outlier_score)
                reasons.append(f"Unusual amount for {cat} category")
        
        # 4. Vendor Pattern Analysis
        vendor = expense['vendor'].lower().strip()
        if vendor in self.vendor_patterns:
            pattern = self.vendor_patterns[vendor]
            amount_deviation = abs(expense['amount'] - pattern['avg_amount'])
            if pattern['amount_std'] > 0:
                vendor_z_score = amount_deviation / pattern['amount_std']
                if vendor_z_score > 2.0:
                    scores.append(min(vendor_z_score / 10, 1.0))
                    reasons.append(f"Unusual amount for vendor {expense['vendor']}")
        
        # 5. Large Amount Detection
        if expense['amount'] > 10000:  # Configurable threshold
            large_amount_score = min(expense['amount'] / 50000, 1.0)
            scores.append(large_amount_score)
            reasons.append(f"Large expense amount: ${expense['amount']:,.0f}")
        
        # Combine scores
        if scores:
            final_score = max(scores)  # Take highest anomaly indicator
        else:
            final_score = 0.0
        
        return final_score, reasons
    
    def _classify_severity(self, score: float) -> str:
        """Classify anomaly severity based on score."""
        if score >= 0.8:
            return 'High'
        elif score >= 0.7:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_anomaly_description(self, expense: Dict, reasons: List[str]) -> str:
        """Generate human-readable anomaly description."""
        base_desc = f"${expense['amount']:,.0f} expense to {expense['vendor']} in {expense['department']}"
        
        if reasons:
            reason_text = "; ".join(reasons)
            return f"{base_desc}. {reason_text}."
        else:
            return f"{base_desc}. General anomaly detected."
    
    def get_anomaly_summary(self, anomaly_results: Dict) -> Dict:
        """Generate summary insights from anomaly detection."""
        if 'error' in anomaly_results:
            return anomaly_results
        
        anomalies = anomaly_results.get('anomalies', [])
        
        if not anomalies:
            return {
                'message': 'No anomalies detected',
                'total_expenses': anomaly_results.get('total_expenses', 0)
            }
        
        # Department analysis
        dept_anomalies = defaultdict(list)
        for anomaly in anomalies:
            dept_anomalies[anomaly['department']].append(anomaly)
        
        dept_summary = {}
        for dept, dept_anomalies_list in dept_anomalies.items():
            total_amount = sum(a['amount'] for a in dept_anomalies_list)
            avg_score = statistics.mean(a['anomaly_score'] for a in dept_anomalies_list)
            dept_summary[dept] = {
                'count': len(dept_anomalies_list),
                'total_amount': total_amount,
                'avg_anomaly_score': avg_score
            }
        
        # Top anomalies
        top_anomalies = sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True)[:5]
        
        return {
            'anomaly_rate': anomaly_results['anomaly_rate'],
            'total_anomalies': len(anomalies),
            'severity_breakdown': anomaly_results['severity_breakdown'],
            'department_summary': dept_summary,
            'top_anomalies': top_anomalies,
            'recommendations': self._generate_recommendations(anomalies)
        }
    
    def _generate_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on anomalies."""
        recommendations = []
        
        if not anomalies:
            return ["No anomalies detected - spending patterns appear normal"]
        
        # High severity recommendations
        high_severity = [a for a in anomalies if a['severity'] == 'High']
        if high_severity:
            recommendations.append(f"Review {len(high_severity)} high-severity anomalies immediately")
        
        # Large amount recommendations
        large_amounts = [a for a in anomalies if a['amount'] > 10000]
        if large_amounts:
            recommendations.append(f"Verify approval for {len(large_amounts)} large expenses (>${10000:,}+)")
        
        # Department recommendations
        dept_counts = Counter(a['department'] for a in anomalies)
        if dept_counts:
            top_dept = dept_counts.most_common(1)[0]
            recommendations.append(f"Focus review on {top_dept[0]} department ({top_dept[1]} anomalies)")
        
        # Pattern recommendations
        if len(anomalies) > len(set(a['vendor'] for a in anomalies)) * 0.5:
            recommendations.append("Multiple anomalies from same vendors - review vendor relationships")
        
        return recommendations
    
    def export_anomaly_report(self, anomaly_results: Dict, output_file: str) -> bool:
        """Export anomaly detection results to JSON."""
        try:
            with open(output_file, 'w') as f:
                json.dump(anomaly_results, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
            return False 