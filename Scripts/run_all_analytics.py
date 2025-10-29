"""
Healthcare Analytics - Master Execution Script
==============================================
Runs all analytics components in the correct order:
1. Database setup
2. Data quality validation
3. Performance reports
4. Visualizations

Author: Healthcare Analytics Team
Date: 2025-10-29
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "Logs"
LOGS_DIR.mkdir(exist_ok=True)

log_file = LOGS_DIR / f"master_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def run_database_setup():
    """Setup database"""
    print_banner("STEP 1: DATABASE SETUP")
    
    try:
        # Import and run database setup
        sys.path.insert(0, str(PROJECT_ROOT / "Scripts"))
        from setup_database import setup_database
        
        success = setup_database()
        
        if success:
            logger.info("✓ Database setup completed successfully")
            return True
        else:
            logger.error("✗ Database setup failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in database setup: {str(e)}", exc_info=True)
        return False

def run_data_quality_validation():
    """Run data quality validation"""
    print_banner("STEP 2: DATA QUALITY VALIDATION")
    
    try:
        from data_quality_validator import main as validate_data
        
        success = validate_data()
        
        if success:
            logger.info("✓ Data quality validation completed successfully")
            return True
        else:
            logger.error("✗ Data quality validation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in data quality validation: {str(e)}", exc_info=True)
        return False

def run_performance_reports():
    """Generate performance reports"""
    print_banner("STEP 3: PERFORMANCE REPORTS")
    
    try:
        from weekly_performance_report import run_weekly_report
        
        success = run_weekly_report()
        
        if success:
            logger.info("✓ Performance reports generated successfully")
            return True
        else:
            logger.error("✗ Performance report generation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error generating performance reports: {str(e)}", exc_info=True)
        return False

def run_visualizations():
    """Generate visualizations"""
    print_banner("STEP 4: DASHBOARD VISUALIZATIONS")
    
    try:
        from dashboard_visualizations import main as generate_visualizations
        
        success = generate_visualizations()
        
        if success:
            logger.info("✓ Visualizations generated successfully")
            return True
        else:
            logger.error("✗ Visualization generation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}", exc_info=True)
        return False

def generate_summary_report():
    """Generate execution summary"""
    print_banner("EXECUTION SUMMARY")
    
    summary = f"""
Healthcare Analytics - Complete Analysis Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OUTPUTS GENERATED:
------------------

📁 Reports/ folder:
   - Weekly Performance Report (Excel with multiple sheets)
   - Data Quality Report (CSV and JSON)
   - Weekly Summary (CSV)
   - Department Performance (CSV)
   - Age Group Analysis (CSV)
   - Daily Trends (CSV)

📁 Visualizations/ folder:
   - Monthly Trends (4 charts in 1 image)
   - Department Performance (4 charts in 1 image)
   - Wait Time vs Satisfaction Correlation (2 charts in 1 image)
   - Demographics Analysis (4 charts in 1 image)
   - Day of Week Patterns (4 charts in 1 image)
   - Satisfaction Analysis (4 charts in 1 image)

📁 Logs/ folder:
   - Performance report logs
   - Data quality validation logs
   - Master execution log (this file)

💾 Database:
   - healthcare_analytics.db (SQLite database with indexed tables)

NEXT STEPS:
-----------
1. Review reports in the Reports/ folder
2. Check visualizations in the Visualizations/ folder
3. Review any warnings in the Logs/ folder
4. Run SQL queries using the database file

For SQL queries, see: SQL_Queries/healthcare_analytics_queries.sql
For detailed documentation, see: README.md
For quick start guide, see: QUICK_START.md
"""
    
    print(summary)
    logger.info(summary)
    
    # Save summary to file
    summary_file = PROJECT_ROOT / "EXECUTION_SUMMARY.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    logger.info(f"\nSummary saved to: {summary_file}")

def main():
    """Main execution function"""
    
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("HEALTHCARE ANALYTICS - COMPLETE ANALYSIS")
    print("=" * 80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    results = {
        'database_setup': False,
        'data_quality': False,
        'performance_reports': False,
        'visualizations': False
    }
    
    # Step 1: Database Setup
    results['database_setup'] = run_database_setup()
    
    if not results['database_setup']:
        logger.error("Cannot proceed without database setup. Exiting...")
        return False
    
    # Step 2: Data Quality Validation
    results['data_quality'] = run_data_quality_validation()
    
    # Step 3: Performance Reports
    results['performance_reports'] = run_performance_reports()
    
    # Step 4: Visualizations
    results['visualizations'] = run_visualizations()
    
    # Calculate success rate
    success_count = sum(results.values())
    total_steps = len(results)
    success_rate = (success_count / total_steps) * 100
    
    # Print final summary
    print_banner("FINAL RESULTS")
    
    print("Component Results:")
    print("-" * 80)
    for component, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{component.replace('_', ' ').title():<40} {status}")
    
    print("-" * 80)
    print(f"Overall Success Rate: {success_rate:.1f}% ({success_count}/{total_steps} components)")
    print("-" * 80)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\nStart Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration:   {duration}")
    
    # Generate summary report
    generate_summary_report()
    
    if success_rate == 100:
        print_banner("🎉 ALL ANALYTICS COMPLETED SUCCESSFULLY! 🎉")
        return True
    elif success_rate >= 75:
        print_banner("⚠️ ANALYTICS COMPLETED WITH SOME WARNINGS")
        return True
    else:
        print_banner("❌ ANALYTICS COMPLETED WITH ERRORS")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
