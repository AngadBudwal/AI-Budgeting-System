"""Budget forecasting system using linear regression and trend analysis - no dependencies!"""

import csv
import json
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from pathlib import Path

class BudgetForecaster:
    """Advanced budget forecasting using pure Python."""
    
    def __init__(self):
        self.historical_data = []
        self.monthly_spending = {}
        self.category_trends = {}
        self.department_trends = {}
        self.seasonal_patterns = {}
        self.is_trained = False
        
        # Forecasting parameters
        self.forecast_horizon_months = 6
        self.confidence_interval = 0.95
        self.seasonal_adjustment = True
        self.trend_smoothing = 0.3  # Exponential smoothing alpha
        
    def load_historical_data(self, expenses_csv: str) -> bool:
        """Load historical expense data."""
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
                        continue  # Skip invalid rows
            
            print(f"📚 Loaded {len(self.historical_data)} expense records")
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
    
    def analyze_spending_patterns(self) -> Dict:
        """Analyze historical spending patterns."""
        if not self.historical_data:
            return {'error': 'No historical data available'}
        
        print("📊 Analyzing spending patterns...")
        
        # Group by month-year
        monthly_totals = defaultdict(float)
        category_monthly = defaultdict(lambda: defaultdict(float))
        department_monthly = defaultdict(lambda: defaultdict(float))
        
        for expense in self.historical_data:
            month_key = expense['date'].strftime('%Y-%m')
            amount = expense['amount']
            
            monthly_totals[month_key] += amount
            category_monthly[expense['category']][month_key] += amount
            department_monthly[expense['department']][month_key] += amount
        
        # Store monthly spending
        self.monthly_spending = dict(monthly_totals)
        
        # Calculate trends for categories
        self.category_trends = {}
        for category, monthly_data in category_monthly.items():
            self.category_trends[category] = self._calculate_trend(monthly_data)
        
        # Calculate trends for departments  
        self.department_trends = {}
        for department, monthly_data in department_monthly.items():
            self.department_trends[department] = self._calculate_trend(monthly_data)
        
        # Detect seasonal patterns
        self._detect_seasonal_patterns()
        
        self.is_trained = True
        
        # Generate analysis summary
        total_months = len(monthly_totals)
        avg_monthly = statistics.mean(monthly_totals.values()) if monthly_totals else 0
        
        recent_months = sorted(monthly_totals.keys())[-3:] if len(monthly_totals) >= 3 else sorted(monthly_totals.keys())
        recent_avg = statistics.mean([monthly_totals[m] for m in recent_months]) if recent_months else 0
        
        growth_rate = ((recent_avg - avg_monthly) / avg_monthly * 100) if avg_monthly > 0 else 0
        
        return {
            'total_months': total_months,
            'total_spending': sum(monthly_totals.values()),
            'average_monthly': avg_monthly,
            'recent_average': recent_avg,
            'growth_rate': growth_rate,
            'categories_analyzed': len(self.category_trends),
            'departments_analyzed': len(self.department_trends)
        }
    
    def _calculate_trend(self, monthly_data: Dict[str, float]) -> Dict:
        """Calculate linear trend using least squares regression."""
        if len(monthly_data) < 2:
            return {'slope': 0, 'intercept': 0, 'r_squared': 0, 'trend': 'insufficient_data'}
        
        # Sort by month
        sorted_months = sorted(monthly_data.keys())
        
        # Convert to numeric values (months since first month)
        x_values = list(range(len(sorted_months)))
        y_values = [monthly_data[month] for month in sorted_months]
        
        # Calculate linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0
            intercept = sum_y / n if n > 0 else 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_mean = sum_y / n if n > 0 else 0
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'trend': trend,
            'monthly_change': slope,
            'confidence': min(r_squared, 1.0)
        }
    
    def _detect_seasonal_patterns(self):
        """Detect seasonal spending patterns."""
        monthly_by_month = defaultdict(list)
        
        for expense in self.historical_data:
            month_num = expense['date'].month
            monthly_by_month[month_num].append(expense['amount'])
        
        # Calculate average spending by month
        self.seasonal_patterns = {}
        overall_avg = statistics.mean([exp['amount'] for exp in self.historical_data]) if self.historical_data else 0
        
        for month_num in range(1, 13):
            if month_num in monthly_by_month:
                month_avg = statistics.mean(monthly_by_month[month_num])
                seasonal_factor = month_avg / overall_avg if overall_avg > 0 else 1.0
            else:
                seasonal_factor = 1.0
            
            self.seasonal_patterns[month_num] = seasonal_factor
    
    def forecast_spending(self, months_ahead: int = 6) -> Dict:
        """Generate spending forecasts."""
        if not self.is_trained:
            return {'error': 'Model not trained. Run analyze_spending_patterns() first.'}
        
        print(f"🔮 Generating {months_ahead}-month spending forecast...")
        
        # Get the latest month from data
        if not self.monthly_spending:
            return {'error': 'No monthly spending data available'}
        
        latest_month = max(self.monthly_spending.keys())
        latest_date = datetime.strptime(latest_month, '%Y-%m')
        
        # Generate monthly forecasts
        monthly_forecasts = []
        total_forecast = 0
        
        for i in range(1, months_ahead + 1):
            forecast_date = latest_date + timedelta(days=32 * i)
            forecast_month = forecast_date.strftime('%Y-%m')
            
            # Base forecast using overall trend
            base_forecast = self._forecast_month_base(i)
            
            # Apply seasonal adjustment
            if self.seasonal_adjustment:
                seasonal_factor = self.seasonal_patterns.get(forecast_date.month, 1.0)
                base_forecast *= seasonal_factor
            
            # Calculate confidence interval
            confidence_range = self._calculate_confidence_interval(base_forecast, i)
            
            monthly_forecast = {
                'month': forecast_month,
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_amount': base_forecast,
                'confidence_lower': confidence_range[0],
                'confidence_upper': confidence_range[1],
                'seasonal_factor': self.seasonal_patterns.get(forecast_date.month, 1.0)
            }
            
            monthly_forecasts.append(monthly_forecast)
            total_forecast += base_forecast
        
        # Generate category forecasts
        category_forecasts = self._forecast_by_category(months_ahead)
        
        # Generate department forecasts
        department_forecasts = self._forecast_by_department(months_ahead)
        
        return {
            'forecast_period': months_ahead,
            'total_forecasted': total_forecast,
            'monthly_forecasts': monthly_forecasts,
            'category_forecasts': category_forecasts,
            'department_forecasts': department_forecasts,
            'confidence_level': self.confidence_interval,
            'generated_at': datetime.now().isoformat()
        }
    
    def _forecast_month_base(self, months_ahead: int) -> float:
        """Calculate base forecast for a month."""
        if not self.monthly_spending:
            return 0
        
        # Use recent months for trend calculation
        recent_months = sorted(self.monthly_spending.keys())[-6:]  # Last 6 months
        recent_values = [self.monthly_spending[month] for month in recent_months]
        
        if len(recent_values) < 2:
            return statistics.mean(recent_values) if recent_values else 0
        
        # Simple linear extrapolation
        x_values = list(range(len(recent_values)))
        trend = self._calculate_trend({str(i): val for i, val in enumerate(recent_values)})
        
        # Project forward
        next_x = len(recent_values) + months_ahead - 1
        forecast = trend['slope'] * next_x + trend['intercept']
        
        # Ensure positive forecast
        return max(forecast, 0)
    
    def _calculate_confidence_interval(self, base_forecast: float, months_ahead: int) -> Tuple[float, float]:
        """Calculate confidence interval for forecast."""
        if not self.monthly_spending:
            return (base_forecast * 0.8, base_forecast * 1.2)
        
        # Calculate historical variance
        monthly_values = list(self.monthly_spending.values())
        if len(monthly_values) < 2:
            std_dev = base_forecast * 0.1
        else:
            std_dev = statistics.stdev(monthly_values)
        
        # Increase uncertainty with time horizon
        uncertainty_multiplier = 1 + (months_ahead * 0.1)
        adjusted_std = std_dev * uncertainty_multiplier
        
        # 95% confidence interval (approximately 2 standard deviations)
        margin = adjusted_std * 1.96
        
        return (
            max(base_forecast - margin, 0),
            base_forecast + margin
        )
    
    def _forecast_by_category(self, months_ahead: int) -> Dict:
        """Generate forecasts by expense category."""
        category_forecasts = {}
        
        for category, trend_data in self.category_trends.items():
            if trend_data['trend'] == 'insufficient_data':
                continue
            
            # Calculate recent average for this category
            category_monthly = defaultdict(float)
            for expense in self.historical_data:
                if expense['category'] == category:
                    month_key = expense['date'].strftime('%Y-%m')
                    category_monthly[month_key] += expense['amount']
            
            recent_avg = 0
            if category_monthly:
                recent_months = sorted(category_monthly.keys())[-3:]
                recent_values = [category_monthly[month] for month in recent_months]
                recent_avg = statistics.mean(recent_values) if recent_values else 0
            
            # Project forward using trend
            total_forecast = 0
            for i in range(1, months_ahead + 1):
                month_forecast = recent_avg + (trend_data['slope'] * i)
                total_forecast += max(month_forecast, 0)
            
            category_forecasts[category] = {
                'total_forecast': total_forecast,
                'monthly_average': total_forecast / months_ahead,
                'trend': trend_data['trend'],
                'confidence': trend_data['confidence']
            }
        
        return category_forecasts
    
    def _forecast_by_department(self, months_ahead: int) -> Dict:
        """Generate forecasts by department."""
        department_forecasts = {}
        
        for department, trend_data in self.department_trends.items():
            if trend_data['trend'] == 'insufficient_data':
                continue
            
            # Calculate recent average for this department
            dept_monthly = defaultdict(float)
            for expense in self.historical_data:
                if expense['department'] == department:
                    month_key = expense['date'].strftime('%Y-%m')
                    dept_monthly[month_key] += expense['amount']
            
            recent_avg = 0
            if dept_monthly:
                recent_months = sorted(dept_monthly.keys())[-3:]
                recent_values = [dept_monthly[month] for month in recent_months]
                recent_avg = statistics.mean(recent_values) if recent_values else 0
            
            # Project forward using trend
            total_forecast = 0
            for i in range(1, months_ahead + 1):
                month_forecast = recent_avg + (trend_data['slope'] * i)
                total_forecast += max(month_forecast, 0)
            
            department_forecasts[department] = {
                'total_forecast': total_forecast,
                'monthly_average': total_forecast / months_ahead,
                'trend': trend_data['trend'],
                'confidence': trend_data['confidence']
            }
        
        return department_forecasts
    
    def analyze_budget_variance(self, budgets_csv: str) -> Dict:
        """Analyze actual vs budgeted spending."""
        try:
            # Load budget data
            budgets = {}
            with open(budgets_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    department = row.get('department', '')
                    category = row.get('category', '')
                    allocated = float(row.get('allocated_amount', 0))
                    
                    key = f"{department}_{category}"
                    budgets[key] = allocated
            
            # Calculate actual spending by department-category
            actuals = defaultdict(float)
            for expense in self.historical_data:
                key = f"{expense['department']}_{expense['category']}"
                actuals[key] += expense['amount']
            
            # Calculate variances
            variances = []
            total_budget = sum(budgets.values())
            total_actual = sum(actuals.values())
            
            for key in set(list(budgets.keys()) + list(actuals.keys())):
                budget_amount = budgets.get(key, 0)
                actual_amount = actuals.get(key, 0)
                variance = actual_amount - budget_amount
                variance_pct = (variance / budget_amount * 100) if budget_amount > 0 else 0
                
                dept_cat = key.split('_', 1)
                department = dept_cat[0] if len(dept_cat) > 0 else 'Unknown'
                category = dept_cat[1] if len(dept_cat) > 1 else 'Unknown'
                
                variances.append({
                    'department': department,
                    'category': category,
                    'budgeted': budget_amount,
                    'actual': actual_amount,
                    'variance': variance,
                    'variance_percent': variance_pct,
                    'status': 'over_budget' if variance > 0 else 'under_budget'
                })
            
            # Sort by largest variances
            variances.sort(key=lambda x: abs(x['variance']), reverse=True)
            
            return {
                'total_budgeted': total_budget,
                'total_actual': total_actual,
                'total_variance': total_actual - total_budget,
                'total_variance_percent': ((total_actual - total_budget) / total_budget * 100) if total_budget > 0 else 0,
                'line_items': variances,
                'over_budget_items': len([v for v in variances if v['variance'] > 0]),
                'under_budget_items': len([v for v in variances if v['variance'] < 0])
            }
            
        except Exception as e:
            return {'error': f'Error analyzing budget variance: {e}'}
    
    def get_insights(self) -> Dict:
        """Generate key insights from analysis."""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        insights = []
        
        # Spending trend insights
        if self.monthly_spending:
            recent_months = sorted(self.monthly_spending.keys())[-3:]
            recent_avg = statistics.mean([self.monthly_spending[m] for m in recent_months])
            overall_avg = statistics.mean(self.monthly_spending.values())
            
            if recent_avg > overall_avg * 1.1:
                insights.append({
                    'type': 'warning',
                    'title': 'Increasing Spending Trend',
                    'message': f'Recent spending (${recent_avg:,.0f}/month) is {((recent_avg/overall_avg-1)*100):.1f}% above historical average'
                })
            elif recent_avg < overall_avg * 0.9:
                insights.append({
                    'type': 'positive',
                    'title': 'Decreasing Spending Trend',
                    'message': f'Recent spending is {((1-recent_avg/overall_avg)*100):.1f}% below historical average'
                })
        
        # Category trend insights
        for category, trend in self.category_trends.items():
            if trend['confidence'] > 0.7:
                if trend['trend'] == 'increasing' and trend['slope'] > 100:
                    insights.append({
                        'type': 'warning',
                        'title': f'{category} Spending Rising',
                        'message': f'Monthly increase of ${trend["slope"]:.0f} detected'
                    })
                elif trend['trend'] == 'decreasing' and abs(trend['slope']) > 100:
                    insights.append({
                        'type': 'positive',
                        'title': f'{category} Spending Declining',
                        'message': f'Monthly decrease of ${abs(trend["slope"]):.0f} detected'
                    })
        
        # Seasonal insights
        if self.seasonal_patterns:
            highest_month = max(self.seasonal_patterns.keys(), key=lambda x: self.seasonal_patterns[x])
            lowest_month = min(self.seasonal_patterns.keys(), key=lambda x: self.seasonal_patterns[x])
            
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            if self.seasonal_patterns[highest_month] > 1.2:
                insights.append({
                    'type': 'info',
                    'title': 'Seasonal Spending Pattern',
                    'message': f'Highest spending typically occurs in {month_names[highest_month]}'
                })
        
        return {
            'insights': insights,
            'total_insights': len(insights)
        }
    
    def export_forecast_report(self, output_file: str, forecast_data: Dict) -> bool:
        """Export forecast to JSON report."""
        try:
            with open(output_file, 'w') as f:
                json.dump(forecast_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
            return False 