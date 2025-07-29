import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging
from datetime import datetime

class FinancialDataQualityMonitor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

    def check_completeness(self, df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
        """Identify missing values that could impact financial reporting"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'check_type': 'completeness',
            'total_rows': len(df),
            'issues': []
        }

        for column in required_columns:
            if column in df.columns:
                missing_count = df[column].isnull().sum()
                missing_percentage = (missing_count / len(df)) * 100

                if missing_percentage > 0:
                    results['issues'].append({
                        'column': column,
                        'missing_count': int(missing_count),
                        'missing_percentage': round(missing_percentage, 2),
                        'severity': 'critical' if missing_percentage > 10 else 'high'
                    })

        results['status'] = 'failed' if results['issues'] else 'passed'
        return results

    def check_consistency(self, df: pd.DataFrame, consistency_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify consistency across different data points or tables"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'check_type': 'consistency',
            'total_rows': len(df),
            'issues': []
        }

        for rule in consistency_rules:
            rule_type = rule.get('type')
            columns = rule.get('columns')

            if rule_type == 'sum_check' and columns and len(columns) >= 2:
                col1, col2 = columns[0], columns[1]
                if col1 in df.columns and col2 in df.columns:
                    if not np.isclose(df[col1].sum(), df[col2].sum()):
                        results['issues'].append({
                            'rule': f"Sum of {col1} not consistent with {col2}",
                            'severity': 'high'
                        })
            # Add more consistency rules as needed

        results['status'] = 'failed' if results['issues'] else 'passed'
        return results

    def check_accuracy(self, df: pd.DataFrame, accuracy_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare data against known-good sources or established benchmarks"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'check_type': 'accuracy',
            'total_rows': len(df),
            'issues': []
        }

        for rule in accuracy_rules:
            column = rule.get('column')
            benchmark = rule.get('benchmark')
            tolerance = rule.get('tolerance', 0.01) # default tolerance 1%

            if column in df.columns and benchmark is not None:
                # Example: check if average of column is close to benchmark
                if not np.isclose(df[column].mean(), benchmark, rtol=tolerance):
                    results['issues'].append({
                        'column': column,
                        'rule': f"Average of {column} is not accurate compared to benchmark {benchmark}",
                        'severity': 'critical'
                    })
            # Add more accuracy rules as needed

        results['status'] = 'failed' if results['issues'] else 'passed'
        return results

    def check_timeliness(self, df: pd.DataFrame, timestamp_column: str, max_age_hours: int) -> Dict[str, Any]:
        """Assess if data is available when expected and is up-to-date"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'check_type': 'timeliness',
            'total_rows': len(df),
            'issues': []
        }

        if timestamp_column in df.columns:
            try:
                latest_data_time = pd.to_datetime(df[timestamp_column]).max()
                age_hours = (datetime.now() - latest_data_time).total_seconds() / 3600

                if age_hours > max_age_hours:
                    results['issues'].append({
                        'column': timestamp_column,
                        'rule': f"Data is {age_hours:.2f} hours old, exceeding max age of {max_age_hours} hours",
                        'severity': 'critical'
                    })
            except Exception as e:
                results['issues'].append({
                    'column': timestamp_column,
                    'rule': f"Error parsing timestamp: {e}",
                    'severity': 'error'
                })

        results['status'] = 'failed' if results['issues'] else 'passed'
        return results

    def run_all_checks(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Run all defined data quality checks and aggregate results"""
        # For demonstration, using dummy data if none provided
        if df is None:
            self.logger.info("No DataFrame provided, generating dummy data for quality checks.")
            df = pd.DataFrame({
                'transaction_id': range(100),
                'amount': np.random.rand(100) * 1000,
                'currency': np.random.choice(['USD', 'EUR', 'GBP', None], 100),
                'timestamp': pd.to_datetime('2023-01-01') + pd.to_timedelta(np.arange(100), unit='H'),
                'category': np.random.choice(['A', 'B', 'C'], 100)
            })
            # Introduce some missing values for testing completeness
            df.loc[df.sample(frac=0.05).index, 'amount'] = np.nan
            df.loc[df.sample(frac=0.03).index, 'currency'] = np.nan

        overall_results = {
            'overall_status': 'passed',
            'checks': []
        }

        # Example configuration for checks
        completeness_config = self.config.get('completeness', {'required_columns': ['amount', 'currency', 'transaction_id']})
        consistency_config = self.config.get('consistency', {'rules': [{'type': 'sum_check', 'columns': ['amount', 'amount']}]})  
        accuracy_config = self.config.get('accuracy', {'rules': [{'column': 'amount', 'benchmark': 500, 'tolerance': 0.1}]})
        timeliness_config = self.config.get('timeliness', {'timestamp_column': 'timestamp', 'max_age_hours': 24})

        # Run completeness check
        completeness_results = self.check_completeness(df, completeness_config['required_columns'])
        overall_results['checks'].append(completeness_results)
        if completeness_results['status'] == 'failed':
            overall_results['overall_status'] = 'failed'

        # Run consistency check
        consistency_results = self.check_consistency(df, consistency_config['rules'])
        overall_results['checks'].append(consistency_results)
        if consistency_results['status'] == 'failed':
            overall_results['overall_status'] = 'failed'

        # Run accuracy check
        accuracy_results = self.check_accuracy(df, accuracy_config['rules'])
        overall_results['checks'].append(accuracy_results)
        if accuracy_results['status'] == 'failed':
            overall_results['overall_status'] = 'failed'

        # Run timeliness check
        timeliness_results = self.check_timeliness(df, timeliness_config['timestamp_column'], timeliness_config['max_age_hours'])
        overall_results['checks'].append(timeliness_results)
        if timeliness_results['status'] == 'failed':
            overall_results['overall_status'] = 'failed'

        self.logger.info(f"Data Quality Monitoring Results: {overall_results}")
        return overall_results

    def generate_quality_report(self, df: pd.DataFrame, quality_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report for financial data"""
        try:
            # Initialize report structure
            report = {
                'overall_quality_score': 100,
                'total_rows': len(df),
                'timestamp': datetime.now().isoformat(),
                'checks': {},
                'issues': [],
                'status': 'passed'
            }
            
            # Check completeness
            required_columns = quality_config.get('required_columns', [])
            if required_columns:
                completeness_result = self.check_completeness(df, required_columns)
                report['checks']['completeness'] = completeness_result
                if completeness_result['status'] == 'failed':
                    report['issues'].extend(completeness_result.get('issues', []))
                    report['status'] = 'failed'
                    report['overall_quality_score'] -= 20
            
            # Check validation rules
            validation_rules = quality_config.get('validation_rules', {})
            if validation_rules:
                validation_issues = []
                for column, rules in validation_rules.items():
                    if column in df.columns:
                        # Check data type
                        if rules.get('dtype') == 'numeric' and not pd.api.types.is_numeric_dtype(df[column]):
                            validation_issues.append({
                                'column': column,
                                'rule': 'data_type',
                                'issue': f'Expected numeric type, got {df[column].dtype}',
                                'severity': 'high'
                            })
                        
                        # Check min value
                        min_value = rules.get('min_value')
                        if min_value is not None and (df[column] < min_value).any():
                            invalid_count = (df[column] < min_value).sum()
                            validation_issues.append({
                                'column': column,
                                'rule': 'min_value',
                                'issue': f'{invalid_count} values below minimum {min_value}',
                                'severity': 'high'
                            })
                
                if validation_issues:
                    report['checks']['validation'] = {
                        'status': 'failed',
                        'issues': validation_issues
                    }
                    report['issues'].extend(validation_issues)
                    report['status'] = 'failed'
                    report['overall_quality_score'] -= 25
                else:
                    report['checks']['validation'] = {'status': 'passed'}
            
            # Ensure score is within bounds
            report['overall_quality_score'] = max(0, min(100, report['overall_quality_score']))
            
            self.logger.info(f"Generated quality report: {report}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating quality report: {e}")
            return None