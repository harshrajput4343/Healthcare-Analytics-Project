"""
Healthcare Analytics - Weekly Performance Report Generator
===========================================================
This script automatically generates comprehensive weekly performance reports
with data quality checks, automated scheduling, and logging functionality.

Author: Healthcare Analytics Team
Date: 2025-10-29
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import schedule
import time
import logging
import os
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "Dataset" / "HEALTHCARE PATIENT DATSET.csv"
REPORTS_DIR = PROJECT_ROOT / "Reports"
LOGS_DIR = PROJECT_ROOT / "Logs"
DB_PATH = PROJECT_ROOT / "healthcare_analytics.db"

# Create necessary directories
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Configure logging
log_file = LOGS_DIR / f"performance_report_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# DATA QUALITY CHECKS
# ============================================================================

class DataQualityChecker:
    """Performs comprehensive data quality checks on healthcare dataset"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.issues = []
        self.quality_report = {}
        
    def check_missing_values(self):
        """Check for missing values in critical columns"""
        logger.info("Checking for missing values...")
        
        missing_stats = self.df.isnull().sum()
        missing_percent = (missing_stats / len(self.df)) * 100
        
        critical_columns = ['date', 'patient_id', 'patient_age', 'patient_waittime']
        
        for col in critical_columns:
            if col in self.df.columns:
                missing = missing_stats[col]
                percent = missing_percent[col]
                
                if missing > 0:
                    issue = f"Missing values in {col}: {missing} ({percent:.2f}%)"
                    self.issues.append(issue)
                    logger.warning(issue)
        
        self.quality_report['missing_values'] = {
            'total_columns': len(self.df.columns),
            'columns_with_missing': (missing_stats > 0).sum(),
            'details': missing_stats[missing_stats > 0].to_dict()
        }
        
        return missing_stats
    
    def check_duplicates(self):
        """Check for duplicate patient records"""
        logger.info("Checking for duplicate records...")
        
        # Check for duplicate patient IDs on the same date
        duplicates = self.df[self.df.duplicated(subset=['patient_id', 'date'], keep=False)]
        
        if len(duplicates) > 0:
            issue = f"Found {len(duplicates)} duplicate patient records (same ID and date)"
            self.issues.append(issue)
            logger.warning(issue)
        
        self.quality_report['duplicates'] = {
            'duplicate_count': len(duplicates),
            'duplicate_percentage': (len(duplicates) / len(self.df)) * 100
        }
        
        return duplicates
    
    def check_outliers(self):
        """Detect outliers in numerical columns"""
        logger.info("Checking for outliers...")
        
        outliers_info = {}
        
        # Check wait time outliers
        if 'patient_waittime' in self.df.columns:
            Q1 = self.df['patient_waittime'].quantile(0.25)
            Q3 = self.df['patient_waittime'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            wait_outliers = self.df[
                (self.df['patient_waittime'] < lower_bound) | 
                (self.df['patient_waittime'] > upper_bound)
            ]
            
            if len(wait_outliers) > 0:
                issue = f"Found {len(wait_outliers)} wait time outliers (< {lower_bound:.2f} or > {upper_bound:.2f} minutes)"
                self.issues.append(issue)
                logger.warning(issue)
            
            outliers_info['wait_time'] = {
                'count': len(wait_outliers),
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        # Check age outliers
        if 'patient_age' in self.df.columns:
            age_outliers = self.df[
                (self.df['patient_age'] < 0) | 
                (self.df['patient_age'] > 120)
            ]
            
            if len(age_outliers) > 0:
                issue = f"Found {len(age_outliers)} age outliers (< 0 or > 120 years)"
                self.issues.append(issue)
                logger.warning(issue)
            
            outliers_info['age'] = {
                'count': len(age_outliers)
            }
        
        # Check satisfaction score outliers
        if 'patient_sat_score' in self.df.columns:
            invalid_scores = self.df[
                (self.df['patient_sat_score'] < 0) | 
                (self.df['patient_sat_score'] > 10)
            ]
            
            if len(invalid_scores) > 0:
                issue = f"Found {len(invalid_scores)} invalid satisfaction scores (< 0 or > 10)"
                self.issues.append(issue)
                logger.warning(issue)
            
            outliers_info['satisfaction'] = {
                'count': len(invalid_scores)
            }
        
        self.quality_report['outliers'] = outliers_info
        
        return outliers_info
    
    def check_data_consistency(self):
        """Check for data consistency issues"""
        logger.info("Checking data consistency...")
        
        consistency_issues = []
        
        # Check date format
        if 'date' in self.df.columns:
            try:
                pd.to_datetime(self.df['date'])
            except Exception as e:
                issue = f"Date format inconsistency: {str(e)}"
                consistency_issues.append(issue)
                logger.error(issue)
        
        # Check gender values
        if 'patient_gender' in self.df.columns:
            valid_genders = ['M', 'F']
            invalid_genders = self.df[~self.df['patient_gender'].isin(valid_genders)]
            
            if len(invalid_genders) > 0:
                issue = f"Found {len(invalid_genders)} records with invalid gender values"
                consistency_issues.append(issue)
                logger.warning(issue)
        
        # Check admin flag values
        if 'patient_admin_flag' in self.df.columns:
            valid_flags = ['True', 'False', True, False]
            invalid_flags = self.df[~self.df['patient_admin_flag'].isin(valid_flags)]
            
            if len(invalid_flags) > 0:
                issue = f"Found {len(invalid_flags)} records with invalid admin flag values"
                consistency_issues.append(issue)
                logger.warning(issue)
        
        self.quality_report['consistency'] = {
            'issues_count': len(consistency_issues),
            'issues': consistency_issues
        }
        
        return consistency_issues
    
    def generate_quality_report(self):
        """Generate comprehensive data quality report"""
        logger.info("Generating comprehensive quality report...")
        
        self.check_missing_values()
        self.check_duplicates()
        self.check_outliers()
        self.check_data_consistency()
        
        # Overall quality score
        total_checks = 4
        issues_count = len(self.issues)
        quality_score = max(0, 100 - (issues_count * 10))
        
        self.quality_report['overall'] = {
            'quality_score': quality_score,
            'total_issues': issues_count,
            'issues_list': self.issues
        }
        
        return self.quality_report
    
    def save_quality_report(self, output_path):
        """Save quality report to CSV"""
        report_data = []
        
        for category, details in self.quality_report.items():
            if category == 'overall':
                report_data.append({
                    'Category': 'Overall Quality',
                    'Metric': 'Quality Score',
                    'Value': details['quality_score'],
                    'Details': f"{details['total_issues']} issues found"
                })
            elif category == 'missing_values':
                for col, count in details.get('details', {}).items():
                    report_data.append({
                        'Category': 'Missing Values',
                        'Metric': col,
                        'Value': count,
                        'Details': f"{(count/len(self.df)*100):.2f}% missing"
                    })
            elif category == 'duplicates':
                report_data.append({
                    'Category': 'Duplicates',
                    'Metric': 'Duplicate Records',
                    'Value': details['duplicate_count'],
                    'Details': f"{details['duplicate_percentage']:.2f}% of total"
                })
        
        df_report = pd.DataFrame(report_data)
        df_report.to_csv(output_path, index=False)
        logger.info(f"Quality report saved to {output_path}")

# ============================================================================
# PERFORMANCE REPORT GENERATOR
# ============================================================================

class PerformanceReportGenerator:
    """Generates comprehensive weekly performance reports"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        
    def get_weekly_summary(self):
        """Generate weekly summary statistics"""
        logger.info("Generating weekly summary...")
        
        # Get current week data
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_data = self.df[
            (self.df['date'] >= week_start.strftime('%Y-%m-%d')) &
            (self.df['date'] <= week_end.strftime('%Y-%m-%d'))
        ]
        
        summary = {
            'Week Start': week_start.strftime('%Y-%m-%d'),
            'Week End': week_end.strftime('%Y-%m-%d'),
            'Total Patients': len(weekly_data),
            'Average Wait Time': weekly_data['patient_waittime'].mean(),
            'Average Satisfaction': weekly_data['patient_sat_score'].mean(),
            'Admission Rate': (weekly_data['patient_admin_flag'] == 'True').sum() / len(weekly_data) * 100,
            'Referral Rate': (weekly_data['department_referral'].notna() & 
                            (weekly_data['department_referral'] != 'None')).sum() / len(weekly_data) * 100
        }
        
        return pd.DataFrame([summary])
    
    def get_department_performance(self):
        """Generate department-wise performance metrics"""
        logger.info("Generating department performance metrics...")
        
        dept_stats = self.df.groupby('department_referral').agg({
            'patient_id': 'count',
            'patient_waittime': ['mean', 'min', 'max'],
            'patient_sat_score': 'mean',
            'patient_admin_flag': lambda x: (x == 'True').sum()
        }).round(2)
        
        dept_stats.columns = ['Patient_Count', 'Avg_Wait_Time', 'Min_Wait_Time', 
                              'Max_Wait_Time', 'Avg_Satisfaction', 'Admissions']
        
        return dept_stats.reset_index()
    
    def get_age_group_analysis(self):
        """Generate age group analysis"""
        logger.info("Generating age group analysis...")
        
        self.df['age_group'] = pd.cut(
            self.df['patient_age'],
            bins=[0, 12, 17, 29, 44, 64, 120],
            labels=['Pediatric (0-12)', 'Adolescent (13-17)', 'Young Adult (18-29)',
                   'Adult (30-44)', 'Middle Age (45-64)', 'Senior (65+)']
        )
        
        age_stats = self.df.groupby('age_group').agg({
            'patient_id': 'count',
            'patient_waittime': 'mean',
            'patient_sat_score': 'mean',
            'patient_admin_flag': lambda x: (x == 'True').sum() / len(x) * 100
        }).round(2)
        
        age_stats.columns = ['Patient_Count', 'Avg_Wait_Time', 'Avg_Satisfaction', 'Admission_Rate']
        
        return age_stats.reset_index()
    
    def get_daily_trends(self):
        """Generate daily trends for the week"""
        logger.info("Generating daily trends...")
        
        daily_stats = self.df.groupby(self.df['date'].dt.date).agg({
            'patient_id': 'count',
            'patient_waittime': 'mean',
            'patient_sat_score': 'mean',
            'patient_admin_flag': lambda x: (x == 'True').sum()
        }).round(2)
        
        daily_stats.columns = ['Patient_Count', 'Avg_Wait_Time', 'Avg_Satisfaction', 'Admissions']
        
        return daily_stats.reset_index()
    
    def generate_full_report(self, output_path):
        """Generate and save comprehensive report"""
        logger.info("Generating comprehensive performance report...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate all report sections
        weekly_summary = self.get_weekly_summary()
        dept_performance = self.get_department_performance()
        age_analysis = self.get_age_group_analysis()
        daily_trends = self.get_daily_trends()
        
        # Save to Excel with multiple sheets
        excel_path = output_path / f"Weekly_Performance_Report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            weekly_summary.to_excel(writer, sheet_name='Weekly Summary', index=False)
            dept_performance.to_excel(writer, sheet_name='Department Performance', index=False)
            age_analysis.to_excel(writer, sheet_name='Age Group Analysis', index=False)
            daily_trends.to_excel(writer, sheet_name='Daily Trends', index=False)
        
        logger.info(f"Performance report saved to {excel_path}")
        
        # Also save individual CSVs
        weekly_summary.to_csv(output_path / f"Weekly_Summary_{timestamp}.csv", index=False)
        dept_performance.to_csv(output_path / f"Department_Performance_{timestamp}.csv", index=False)
        age_analysis.to_csv(output_path / f"Age_Group_Analysis_{timestamp}.csv", index=False)
        daily_trends.to_csv(output_path / f"Daily_Trends_{timestamp}.csv", index=False)
        
        return excel_path

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def load_data_to_database(csv_path, db_path):
    """Load CSV data into SQLite database"""
    logger.info(f"Loading data from {csv_path} to database...")
    
    try:
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(db_path)
        df.to_sql('healthcare_patients', conn, if_exists='replace', index=False)
        conn.close()
        logger.info("Data loaded successfully to database")
        return True
    except Exception as e:
        logger.error(f"Error loading data to database: {str(e)}")
        return False

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_weekly_report():
    """Main function to execute weekly report generation"""
    logger.info("=" * 80)
    logger.info("STARTING WEEKLY PERFORMANCE REPORT GENERATION")
    logger.info("=" * 80)
    
    try:
        # Load dataset
        logger.info(f"Loading dataset from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)
        logger.info(f"Dataset loaded successfully: {len(df)} records")
        
        # Perform data quality checks
        logger.info("\n" + "=" * 80)
        logger.info("PERFORMING DATA QUALITY CHECKS")
        logger.info("=" * 80)
        
        quality_checker = DataQualityChecker(df)
        quality_report = quality_checker.generate_quality_report()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        quality_report_path = REPORTS_DIR / f"Data_Quality_Report_{timestamp}.csv"
        quality_checker.save_quality_report(quality_report_path)
        
        # Log quality issues to separate file
        if quality_checker.issues:
            issues_log_path = LOGS_DIR / f"data_quality_issues_{timestamp}.log"
            with open(issues_log_path, 'w') as f:
                f.write("DATA QUALITY ISSUES DETECTED\n")
                f.write("=" * 80 + "\n\n")
                for idx, issue in enumerate(quality_checker.issues, 1):
                    f.write(f"{idx}. {issue}\n")
            logger.warning(f"Data quality issues logged to {issues_log_path}")
        else:
            logger.info("No data quality issues detected!")
        
        # Generate performance reports
        logger.info("\n" + "=" * 80)
        logger.info("GENERATING PERFORMANCE REPORTS")
        logger.info("=" * 80)
        
        report_generator = PerformanceReportGenerator(df)
        report_path = report_generator.generate_full_report(REPORTS_DIR)
        
        # Load data to database for SQL queries
        load_data_to_database(DATASET_PATH, DB_PATH)
        
        logger.info("\n" + "=" * 80)
        logger.info("WEEKLY REPORT GENERATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Reports saved to: {REPORTS_DIR}")
        logger.info(f"Logs saved to: {LOGS_DIR}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}", exc_info=True)
        return False

# ============================================================================
# SCHEDULING FUNCTIONALITY
# ============================================================================

def schedule_weekly_reports():
    """Schedule weekly reports to run automatically"""
    logger.info("Setting up weekly report scheduler...")
    
    # Schedule report to run every Monday at 9:00 AM
    schedule.every().monday.at("09:00").do(run_weekly_report)
    
    # Also schedule for immediate testing (run every hour during testing)
    # schedule.every().hour.do(run_weekly_report)
    
    logger.info("Weekly reports scheduled for every Monday at 9:00 AM")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Healthcare Weekly Performance Report Generator')
    parser.add_argument('--mode', choices=['once', 'schedule'], default='once',
                       help='Run once or schedule for recurring execution')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        # Run report generation once
        success = run_weekly_report()
        sys.exit(0 if success else 1)
    else:
        # Run on schedule
        schedule_weekly_reports()
