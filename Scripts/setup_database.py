"""
Healthcare Analytics - Database Setup Script
=============================================
Sets up SQLite database and loads healthcare data for SQL analytics.

Author: Healthcare Analytics Team
Date: 2025-10-29
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "Dataset" / "HEALTHCARE PATIENT DATSET.csv"
DB_PATH = PROJECT_ROOT / "healthcare_analytics.db"

def setup_database():
    """Setup SQLite database and load healthcare data"""
    
    logger.info("=" * 80)
    logger.info("HEALTHCARE ANALYTICS DATABASE SETUP")
    logger.info("=" * 80)
    
    try:
        # Load CSV data
        logger.info(f"\nLoading data from: {DATASET_PATH}")
        df = pd.read_csv(DATASET_PATH)
        logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
        
        # Display column info
        logger.info("\nDataset Columns:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            logger.info(f"  - {col}: {dtype} ({null_count} nulls)")
        
        # Create SQLite connection
        logger.info(f"\nCreating database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        
        # Load data to database
        logger.info("Loading data to 'healthcare_patients' table...")
        df.to_sql('healthcare_patients', conn, if_exists='replace', index=False)
        
        # Verify data load
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM healthcare_patients")
        count = cursor.fetchone()[0]
        logger.info(f"✓ Successfully loaded {count:,} records to database")
        
        # Create indexes for better query performance
        logger.info("\nCreating database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_date ON healthcare_patients(date)",
            "CREATE INDEX IF NOT EXISTS idx_patient_id ON healthcare_patients(patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_department ON healthcare_patients(department_referral)",
            "CREATE INDEX IF NOT EXISTS idx_age ON healthcare_patients(patient_age)",
            "CREATE INDEX IF NOT EXISTS idx_waittime ON healthcare_patients(patient_waittime)"
        ]
        
        for idx_query in indexes:
            cursor.execute(idx_query)
            logger.info(f"  ✓ Created index")
        
        conn.commit()
        
        # Display sample data
        logger.info("\nSample data from database:")
        sample_query = """
        SELECT date, patient_id, patient_age, patient_waittime, 
               department_referral, patient_sat_score
        FROM healthcare_patients 
        LIMIT 5
        """
        sample_df = pd.read_sql_query(sample_query, conn)
        print("\n" + sample_df.to_string(index=False))
        
        # Display summary statistics
        logger.info("\n" + "=" * 80)
        logger.info("DATABASE SUMMARY STATISTICS")
        logger.info("=" * 80)
        
        stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT date) as unique_dates,
            COUNT(DISTINCT department_referral) as departments,
            ROUND(AVG(patient_age), 2) as avg_age,
            ROUND(AVG(patient_waittime), 2) as avg_wait_time,
            ROUND(AVG(patient_sat_score), 2) as avg_satisfaction
        FROM healthcare_patients
        """
        
        stats_df = pd.read_sql_query(stats_query, conn)
        print("\n" + stats_df.to_string(index=False))
        
        conn.close()
        
        logger.info("\n" + "=" * 80)
        logger.info("DATABASE SETUP COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"\nDatabase location: {DB_PATH}")
        logger.info("You can now run SQL queries using:")
        logger.info("  - SQLite CLI: sqlite3 healthcare_analytics.db")
        logger.info("  - Python: See README.md for examples")
        logger.info("  - SQL files: SQL_Queries/healthcare_analytics_queries.sql")
        logger.info("=" * 80 + "\n")
        
        return True
        
    except FileNotFoundError:
        logger.error(f"Error: Dataset file not found at {DATASET_PATH}")
        logger.error("Please ensure HEALTHCARE PATIENT DATSET.csv is in the Dataset folder")
        return False
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}", exc_info=True)
        return False

def test_database():
    """Test database with sample queries"""
    
    logger.info("\nTesting database with sample queries...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Test query 1: Monthly patient counts
        query1 = """
        SELECT 
            strftime('%Y-%m', date) AS month,
            COUNT(*) AS patient_count
        FROM healthcare_patients
        GROUP BY month
        ORDER BY month
        LIMIT 5
        """
        
        logger.info("\nTest Query 1: Monthly Patient Counts (first 5 months)")
        df1 = pd.read_sql_query(query1, conn)
        print(df1.to_string(index=False))
        
        # Test query 2: Department stats
        query2 = """
        SELECT 
            department_referral,
            COUNT(*) AS patients,
            ROUND(AVG(patient_waittime), 2) AS avg_wait_time
        FROM healthcare_patients
        WHERE department_referral IS NOT NULL 
          AND department_referral != 'None'
        GROUP BY department_referral
        ORDER BY patients DESC
        LIMIT 5
        """
        
        logger.info("\nTest Query 2: Top 5 Departments by Patient Volume")
        df2 = pd.read_sql_query(query2, conn)
        print(df2.to_string(index=False))
        
        conn.close()
        
        logger.info("\n✓ Database tests completed successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"Error testing database: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    # Setup database
    success = setup_database()
    
    # Test database if setup was successful
    if success:
        test_database()
    
    sys.exit(0 if success else 1)
