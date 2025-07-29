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