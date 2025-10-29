"""
Healthcare Analytics - Comprehensive Data Quality Validator
============================================================
Advanced data quality validation module for healthcare datasets
Performs in-depth checks, generates detailed reports, and provides
data cleaning recommendations.

Author: Healthcare Analytics Team
Date: 2025-10-29
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "Dataset" / "HEALTHCARE PATIENT DATSET.csv"
REPORTS_DIR = PROJECT_ROOT / "Reports"
LOGS_DIR = PROJECT_ROOT / "Logs"
VISUALIZATIONS_DIR = PROJECT_ROOT / "Visualizations"

# Create directories
for directory in [REPORTS_DIR, LOGS_DIR, VISUALIZATIONS_DIR]:
    directory.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# COMPREHENSIVE DATA QUALITY VALIDATOR
# ============================================================================

class ComprehensiveDataQualityValidator:
    """Advanced data quality validation with detailed analysis"""
    
    def __init__(self, df, config=None):
        self.df = df.copy()
        self.original_df = df.copy()
        self.config = config or self._default_config()
        self.validation_results = {}
        self.recommendations = []
        
    def _default_config(self):
        """Default validation configuration"""
        return {
            'critical_columns': ['date', 'patient_id', 'patient_age', 'patient_waittime'],
            'numeric_columns': ['patient_age', 'patient_waittime', 'patient_sat_score'],
            'categorical_columns': ['patient_gender', 'patient_race', 'department_referral'],
            'expected_ranges': {
                'patient_age': (0, 120),
                'patient_waittime': (0, 300),
                'patient_sat_score': (0, 10)
            },
            'valid_values': {
                'patient_gender': ['M', 'F'],
                'patient_admin_flag': ['True', 'False', True, False],
                'Moment': ['AM', 'PM']
            }
        }
    
    # ========================================================================
    # COMPLETENESS CHECKS
    # ========================================================================
    
    def check_completeness(self):
        """Comprehensive completeness analysis"""
        logger.info("Performing completeness checks...")
        
        results = {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_by_column': {},
            'missing_by_record': {},
            'completeness_score': 0
        }
        
        # Column-wise missing values
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            
            results['missing_by_column'][col] = {
                'count': int(missing_count),
                'percentage': round(float(missing_pct), 2),
                'is_critical': col in self.config['critical_columns']
            }
            
            if col in self.config['critical_columns'] and missing_count > 0:
                self.recommendations.append({
                    'severity': 'HIGH',
                    'category': 'Completeness',
                    'issue': f"Critical column '{col}' has {missing_count} missing values",
                    'recommendation': f"Investigate and fill missing values in {col}"
                })
        
        # Record-wise completeness
        records_with_missing = self.df.isnull().any(axis=1).sum()
        results['missing_by_record'] = {
            'records_with_missing': int(records_with_missing),
            'percentage': round(float((records_with_missing / len(self.df)) * 100), 2)
        }
        
        # Overall completeness score
        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        completeness_score = ((total_cells - missing_cells) / total_cells) * 100
        results['completeness_score'] = round(float(completeness_score), 2)
        
        self.validation_results['completeness'] = results
        logger.info(f"Completeness score: {completeness_score:.2f}%")
        
        return results
    
    # ========================================================================
    # UNIQUENESS CHECKS
    # ========================================================================
    
    def check_uniqueness(self):
        """Check for duplicate records and unique constraints"""
        logger.info("Performing uniqueness checks...")
        
        results = {
            'duplicate_records': {},
            'unique_constraints': {}
        }
        
        # Check for exact duplicates
        exact_duplicates = self.df[self.df.duplicated(keep=False)]
        results['duplicate_records']['exact_duplicates'] = {
            'count': len(exact_duplicates),
            'percentage': round((len(exact_duplicates) / len(self.df)) * 100, 2)
        }
        
        if len(exact_duplicates) > 0:
            self.recommendations.append({
                'severity': 'MEDIUM',
                'category': 'Uniqueness',
                'issue': f"Found {len(exact_duplicates)} exact duplicate records",
                'recommendation': "Review and remove duplicate records"
            })
        
        # Check patient_id + date uniqueness (should be unique)
        id_date_duplicates = self.df[
            self.df.duplicated(subset=['patient_id', 'date'], keep=False)
        ]
        results['duplicate_records']['id_date_duplicates'] = {
            'count': len(id_date_duplicates),
            'percentage': round((len(id_date_duplicates) / len(self.df)) * 100, 2)
        }
        
        if len(id_date_duplicates) > 0:
            self.recommendations.append({
                'severity': 'HIGH',
                'category': 'Uniqueness',
                'issue': f"Found {len(id_date_duplicates)} records with duplicate patient_id and date",
                'recommendation': "Investigate why same patient has multiple records on same date"
            })
        
        # Unique value counts for key columns
        for col in ['patient_id', 'patient_gender', 'patient_race', 'department_referral']:
            if col in self.df.columns:
                unique_count = self.df[col].nunique()
                total_count = len(self.df)
                results['unique_constraints'][col] = {
                    'unique_values': int(unique_count),
                    'total_records': int(total_count),
                    'uniqueness_ratio': round(float(unique_count / total_count), 4)
                }
        
        self.validation_results['uniqueness'] = results
        return results
    
    # ========================================================================
    # VALIDITY CHECKS
    # ========================================================================
    
    def check_validity(self):
        """Check data validity against expected ranges and values"""
        logger.info("Performing validity checks...")
        
        results = {
            'range_violations': {},
            'value_violations': {},
            'format_violations': {}
        }
        
        # Check numeric ranges
        for col, (min_val, max_val) in self.config['expected_ranges'].items():
            if col in self.df.columns:
                violations = self.df[
                    (self.df[col] < min_val) | (self.df[col] > max_val)
                ]
                
                results['range_violations'][col] = {
                    'expected_range': f"{min_val}-{max_val}",
                    'violations': len(violations),
                    'percentage': round((len(violations) / len(self.df)) * 100, 2)
                }
                
                if len(violations) > 0:
                    self.recommendations.append({
                        'severity': 'MEDIUM',
                        'category': 'Validity',
                        'issue': f"{len(violations)} records in '{col}' outside range {min_val}-{max_val}",
                        'recommendation': f"Validate and correct out-of-range values in {col}"
                    })
        
        # Check categorical values
        for col, valid_values in self.config['valid_values'].items():
            if col in self.df.columns:
                invalid = self.df[~self.df[col].isin(valid_values) & self.df[col].notna()]
                
                results['value_violations'][col] = {
                    'expected_values': valid_values,
                    'violations': len(invalid),
                    'invalid_values': invalid[col].unique().tolist() if len(invalid) > 0 else []
                }
                
                if len(invalid) > 0:
                    self.recommendations.append({
                        'severity': 'MEDIUM',
                        'category': 'Validity',
                        'issue': f"{len(invalid)} records in '{col}' have invalid values",
                        'recommendation': f"Standardize values in {col} to match expected categories"
                    })
        
        # Check date format
        if 'date' in self.df.columns:
            try:
                pd.to_datetime(self.df['date'])
                results['format_violations']['date'] = {
                    'violations': 0,
                    'status': 'Valid'
                }
            except Exception as e:
                results['format_violations']['date'] = {
                    'violations': 'Unknown',
                    'status': 'Invalid',
                    'error': str(e)
                }
                self.recommendations.append({
                    'severity': 'HIGH',
                    'category': 'Validity',
                    'issue': f"Date format issues detected: {str(e)}",
                    'recommendation': "Standardize date format to YYYY-MM-DD"
                })
        
        self.validation_results['validity'] = results
        return results
    
    # ========================================================================
    # CONSISTENCY CHECKS
    # ========================================================================
    
    def check_consistency(self):
        """Check data consistency and logical relationships"""
        logger.info("Performing consistency checks...")
        
        results = {
            'temporal_consistency': {},
            'logical_consistency': {},
            'cross_field_consistency': {}
        }
        
        # Check temporal consistency
        if 'date' in self.df.columns:
            self.df['date_parsed'] = pd.to_datetime(self.df['date'], errors='coerce')
            future_dates = self.df[self.df['date_parsed'] > datetime.now()]
            
            results['temporal_consistency']['future_dates'] = {
                'count': len(future_dates),
                'percentage': round((len(future_dates) / len(self.df)) * 100, 2)
            }
            
            if len(future_dates) > 0:
                self.recommendations.append({
                    'severity': 'HIGH',
                    'category': 'Consistency',
                    'issue': f"Found {len(future_dates)} records with future dates",
                    'recommendation': "Correct dates that are in the future"
                })
        
        # Check logical consistency: high satisfaction with high wait time
        if 'patient_sat_score' in self.df.columns and 'patient_waittime' in self.df.columns:
            suspicious = self.df[
                (self.df['patient_sat_score'] >= 8) & 
                (self.df['patient_waittime'] >= 60)
            ]
            
            results['logical_consistency']['high_sat_high_wait'] = {
                'count': len(suspicious),
                'percentage': round((len(suspicious) / len(self.df)) * 100, 2),
                'note': 'High satisfaction despite long wait times (may be valid)'
            }
        
        # Check for pediatric patients with certain departments
        if 'patient_age' in self.df.columns and 'department_referral' in self.df.columns:
            adult_only_depts = ['Cardiology', 'Gastroenterology']
            pediatric_in_adult = self.df[
                (self.df['patient_age'] < 13) & 
                (self.df['department_referral'].isin(adult_only_depts))
            ]
            
            results['cross_field_consistency']['pediatric_in_adult_dept'] = {
                'count': len(pediatric_in_adult),
                'note': 'Pediatric patients in typically adult-focused departments'
            }
        
        self.validation_results['consistency'] = results
        return results
    
    # ========================================================================
    # ACCURACY CHECKS (Statistical Analysis)
    # ========================================================================
    
    def check_accuracy(self):
        """Statistical accuracy and outlier detection"""
        logger.info("Performing accuracy and outlier checks...")
        
        results = {
            'outliers': {},
            'statistical_summary': {}
        }
        
        for col in self.config['numeric_columns']:
            if col in self.df.columns and self.df[col].notna().any():
                # Calculate statistics
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = self.df[
                    (self.df[col] < lower_bound) | 
                    (self.df[col] > upper_bound)
                ]
                
                results['outliers'][col] = {
                    'count': len(outliers),
                    'percentage': round((len(outliers) / len(self.df[self.df[col].notna()])) * 100, 2),
                    'lower_bound': round(float(lower_bound), 2),
                    'upper_bound': round(float(upper_bound), 2),
                    'Q1': round(float(Q1), 2),
                    'Q3': round(float(Q3), 2),
                    'IQR': round(float(IQR), 2)
                }
                
                results['statistical_summary'][col] = {
                    'mean': round(float(self.df[col].mean()), 2),
                    'median': round(float(self.df[col].median()), 2),
                    'std': round(float(self.df[col].std()), 2),
                    'min': round(float(self.df[col].min()), 2),
                    'max': round(float(self.df[col].max()), 2)
                }
                
                if len(outliers) > 0:
                    self.recommendations.append({
                        'severity': 'LOW',
                        'category': 'Accuracy',
                        'issue': f"Found {len(outliers)} statistical outliers in '{col}'",
                        'recommendation': f"Review outliers in {col} (outside {lower_bound:.2f}-{upper_bound:.2f})"
                    })
        
        self.validation_results['accuracy'] = results
        return results
    
    # ========================================================================
    # GENERATE COMPREHENSIVE REPORT
    # ========================================================================
    
    def run_all_validations(self):
        """Run all validation checks"""
        logger.info("Running comprehensive data quality validation...")
        
        self.check_completeness()
        self.check_uniqueness()
        self.check_validity()
        self.check_consistency()
        self.check_accuracy()
        
        # Calculate overall quality score
        scores = {
            'completeness': self.validation_results['completeness']['completeness_score'],
            'uniqueness': 100 - (self.validation_results['uniqueness']['duplicate_records']['exact_duplicates']['percentage']),
            'validity': self._calculate_validity_score(),
            'consistency': self._calculate_consistency_score(),
            'accuracy': self._calculate_accuracy_score()
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        self.validation_results['overall'] = {
            'quality_score': round(overall_score, 2),
            'dimension_scores': scores,
            'total_recommendations': len(self.recommendations),
            'critical_issues': len([r for r in self.recommendations if r['severity'] == 'HIGH'])
        }
        
        logger.info(f"Overall Data Quality Score: {overall_score:.2f}%")
        
        return self.validation_results
    
    def _calculate_validity_score(self):
        """Calculate validity score based on violations"""
        if 'validity' not in self.validation_results:
            return 100
        
        total_violations = 0
        for violations in self.validation_results['validity']['range_violations'].values():
            total_violations += violations['violations']
        for violations in self.validation_results['validity']['value_violations'].values():
            total_violations += violations['violations']
        
        violation_rate = (total_violations / len(self.df)) * 100
        return max(0, 100 - violation_rate)
    
    def _calculate_consistency_score(self):
        """Calculate consistency score"""
        if 'consistency' not in self.validation_results:
            return 100
        
        issues = 0
        if 'future_dates' in self.validation_results['consistency']['temporal_consistency']:
            issues += self.validation_results['consistency']['temporal_consistency']['future_dates']['count']
        
        issue_rate = (issues / len(self.df)) * 100
        return max(0, 100 - issue_rate)
    
    def _calculate_accuracy_score(self):
        """Calculate accuracy score based on outliers"""
        if 'accuracy' not in self.validation_results:
            return 100
        
        total_outliers = sum(
            data['count'] 
            for data in self.validation_results['accuracy']['outliers'].values()
        )
        
        outlier_rate = (total_outliers / len(self.df)) * 100
        return max(0, 100 - (outlier_rate * 0.5))  # Outliers are less severe
    
    # ========================================================================
    # EXPORT REPORTS
    # ========================================================================
    
    def export_validation_report(self, format='all'):
        """Export validation results in multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON Report
        if format in ['json', 'all']:
            json_path = REPORTS_DIR / f"Data_Quality_Validation_{timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(self.validation_results, f, indent=2, default=str)
            logger.info(f"JSON report saved to {json_path}")
        
        # Excel Report
        if format in ['excel', 'all']:
            excel_path = REPORTS_DIR / f"Data_Quality_Report_{timestamp}.xlsx"
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Overall Quality Score', 'Completeness', 'Uniqueness', 'Validity', 'Consistency', 'Accuracy'],
                    'Score': [
                        self.validation_results['overall']['quality_score'],
                        self.validation_results['overall']['dimension_scores']['completeness'],
                        self.validation_results['overall']['dimension_scores']['uniqueness'],
                        self.validation_results['overall']['dimension_scores']['validity'],
                        self.validation_results['overall']['dimension_scores']['consistency'],
                        self.validation_results['overall']['dimension_scores']['accuracy']
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Recommendations sheet
                if self.recommendations:
                    pd.DataFrame(self.recommendations).to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Missing values sheet
                missing_data = []
                for col, data in self.validation_results['completeness']['missing_by_column'].items():
                    missing_data.append({
                        'Column': col,
                        'Missing Count': data['count'],
                        'Missing Percentage': data['percentage'],
                        'Is Critical': data['is_critical']
                    })
                pd.DataFrame(missing_data).to_excel(writer, sheet_name='Missing Values', index=False)
            
            logger.info(f"Excel report saved to {excel_path}")
        
        # Text Report for logging
        if format in ['txt', 'all']:
            txt_path = LOGS_DIR / f"Data_Quality_Summary_{timestamp}.txt"
            with open(txt_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("DATA QUALITY VALIDATION REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Dataset Records: {len(self.df)}\n")
                f.write(f"Overall Quality Score: {self.validation_results['overall']['quality_score']}%\n\n")
                
                f.write("DIMENSION SCORES:\n")
                f.write("-" * 80 + "\n")
                for dimension, score in self.validation_results['overall']['dimension_scores'].items():
                    f.write(f"  {dimension.capitalize()}: {score:.2f}%\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"RECOMMENDATIONS ({len(self.recommendations)} total)\n")
                f.write("=" * 80 + "\n\n")
                
                for idx, rec in enumerate(self.recommendations, 1):
                    f.write(f"{idx}. [{rec['severity']}] {rec['category']}\n")
                    f.write(f"   Issue: {rec['issue']}\n")
                    f.write(f"   Recommendation: {rec['recommendation']}\n\n")
            
            logger.info(f"Text report saved to {txt_path}")
        
        return timestamp

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    logger.info("Starting comprehensive data quality validation...")
    
    try:
        # Load dataset
        df = pd.read_csv(DATASET_PATH)
        logger.info(f"Loaded dataset: {len(df)} records, {len(df.columns)} columns")
        
        # Create validator
        validator = ComprehensiveDataQualityValidator(df)
        
        # Run all validations
        results = validator.run_all_validations()
        
        # Export reports
        timestamp = validator.export_validation_report(format='all')
        
        # Print summary
        print("\n" + "=" * 80)
        print("DATA QUALITY VALIDATION COMPLETE")
        print("=" * 80)
        print(f"\nOverall Quality Score: {results['overall']['quality_score']}%")
        print(f"Critical Issues: {results['overall']['critical_issues']}")
        print(f"Total Recommendations: {results['overall']['total_recommendations']}")
        print(f"\nReports saved with timestamp: {timestamp}")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
