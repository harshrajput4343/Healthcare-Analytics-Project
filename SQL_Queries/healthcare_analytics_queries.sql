-- ============================================================================
-- HEALTHCARE PATIENT DATASET ANALYTICS - COMPREHENSIVE SQL QUERIES
-- Database: SQLite
-- Purpose: Healthcare data analysis for operational insights and performance metrics
-- ============================================================================

-- ============================================================================
-- QUERY 1: MONTHLY PATIENT VOLUME TRENDS
-- Purpose: Track patient admission trends over time to identify patterns
-- ============================================================================

-- Monthly patient counts with growth percentage
SELECT 
    strftime('%Y-%m', date) AS month,
    COUNT(*) AS patient_count,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admitted_patients,
    COUNT(CASE WHEN patient_admin_flag = 'False' THEN 1 END) AS non_admitted_patients,
    ROUND(COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) * 100.0 / COUNT(*), 2) AS admission_rate_percent,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction_score
FROM 
    healthcare_patients
WHERE 
    date IS NOT NULL
GROUP BY 
    strftime('%Y-%m', date)
ORDER BY 
    month;

-- Month-over-Month growth analysis
WITH monthly_stats AS (
    SELECT 
        strftime('%Y-%m', date) AS month,
        COUNT(*) AS patient_count
    FROM healthcare_patients
    GROUP BY strftime('%Y-%m', date)
)
SELECT 
    month,
    patient_count,
    LAG(patient_count, 1) OVER (ORDER BY month) AS previous_month_count,
    ROUND((patient_count - LAG(patient_count, 1) OVER (ORDER BY month)) * 100.0 / 
          LAG(patient_count, 1) OVER (ORDER BY month), 2) AS growth_percentage
FROM 
    monthly_stats
ORDER BY 
    month;

-- ============================================================================
-- QUERY 2: DEPARTMENT-WISE PERFORMANCE METRICS
-- Purpose: Analyze performance metrics across different departments
-- ============================================================================

-- Comprehensive department performance dashboard
SELECT 
    COALESCE(department_referral, 'No Referral/Walk-in') AS department,
    COUNT(*) AS total_patients,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time_minutes,
    MIN(patient_waittime) AS min_wait_time,
    MAX(patient_waittime) AS max_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction_score,
    COUNT(CASE WHEN patient_sat_score >= 8 THEN 1 END) AS high_satisfaction_count,
    COUNT(CASE WHEN patient_sat_score <= 3 THEN 1 END) AS low_satisfaction_count,
    ROUND(COUNT(CASE WHEN patient_sat_score >= 8 THEN 1 END) * 100.0 / 
          COUNT(CASE WHEN patient_sat_score IS NOT NULL THEN 1 END), 2) AS high_sat_percentage,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admissions,
    ROUND(COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) * 100.0 / COUNT(*), 2) AS admission_rate
FROM 
    healthcare_patients
GROUP BY 
    department_referral
ORDER BY 
    total_patients DESC;

-- Department efficiency ranking (wait time vs satisfaction)
SELECT 
    COALESCE(department_referral, 'No Referral/Walk-in') AS department,
    COUNT(*) AS patient_volume,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    RANK() OVER (ORDER BY AVG(patient_waittime) ASC) AS wait_time_rank,
    RANK() OVER (ORDER BY AVG(patient_sat_score) DESC) AS satisfaction_rank,
    ROUND((RANK() OVER (ORDER BY AVG(patient_waittime) ASC) + 
           RANK() OVER (ORDER BY AVG(patient_sat_score) DESC)) / 2.0, 2) AS overall_performance_score
FROM 
    healthcare_patients
WHERE 
    patient_sat_score IS NOT NULL
GROUP BY 
    department_referral
ORDER BY 
    overall_performance_score ASC;

-- ============================================================================
-- QUERY 3: WAIT TIME VS SATISFACTION CORRELATION ANALYSIS
-- Purpose: Identify relationship between wait times and patient satisfaction
-- ============================================================================

-- Wait time buckets with satisfaction scores
SELECT 
    CASE 
        WHEN patient_waittime < 15 THEN '0-15 minutes'
        WHEN patient_waittime < 30 THEN '15-30 minutes'
        WHEN patient_waittime < 45 THEN '30-45 minutes'
        WHEN patient_waittime < 60 THEN '45-60 minutes'
        ELSE '60+ minutes'
    END AS wait_time_category,
    COUNT(*) AS patient_count,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    ROUND(MIN(patient_sat_score), 2) AS min_satisfaction,
    ROUND(MAX(patient_sat_score), 2) AS max_satisfaction,
    COUNT(CASE WHEN patient_sat_score >= 8 THEN 1 END) AS highly_satisfied,
    COUNT(CASE WHEN patient_sat_score <= 3 THEN 1 END) AS dissatisfied,
    ROUND(AVG(patient_waittime), 2) AS avg_actual_wait_time
FROM 
    healthcare_patients
WHERE 
    patient_sat_score IS NOT NULL 
    AND patient_waittime IS NOT NULL
GROUP BY 
    wait_time_category
ORDER BY 
    avg_actual_wait_time;

-- Detailed correlation analysis
SELECT 
    ROUND(AVG(patient_waittime), 2) AS overall_avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS overall_avg_satisfaction,
    COUNT(*) AS total_records,
    -- High satisfaction with low wait time
    COUNT(CASE WHEN patient_waittime < 30 AND patient_sat_score >= 8 THEN 1 END) AS quick_and_satisfied,
    -- Low satisfaction with high wait time
    COUNT(CASE WHEN patient_waittime >= 45 AND patient_sat_score <= 3 THEN 1 END) AS slow_and_dissatisfied,
    -- Percentage showing negative correlation
    ROUND(COUNT(CASE WHEN patient_waittime >= 45 AND patient_sat_score <= 3 THEN 1 END) * 100.0 / 
          COUNT(CASE WHEN patient_sat_score IS NOT NULL THEN 1 END), 2) AS problem_case_percentage
FROM 
    healthcare_patients
WHERE 
    patient_sat_score IS NOT NULL;

-- ============================================================================
-- QUERY 4: AGE GROUP DEMOGRAPHICS WITH REFERRAL RATES
-- Purpose: Analyze patient demographics and department referral patterns
-- ============================================================================

-- Age group analysis with comprehensive metrics
SELECT 
    CASE 
        WHEN patient_age < 13 THEN 'Pediatric (0-12)'
        WHEN patient_age < 18 THEN 'Adolescent (13-17)'
        WHEN patient_age < 30 THEN 'Young Adult (18-29)'
        WHEN patient_age < 45 THEN 'Adult (30-44)'
        WHEN patient_age < 65 THEN 'Middle Age (45-64)'
        ELSE 'Senior (65+)'
    END AS age_group,
    COUNT(*) AS total_patients,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total,
    COUNT(CASE WHEN department_referral IS NOT NULL AND department_referral != 'None' THEN 1 END) AS referred_patients,
    ROUND(COUNT(CASE WHEN department_referral IS NOT NULL AND department_referral != 'None' THEN 1 END) * 100.0 / COUNT(*), 2) AS referral_rate,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admissions,
    COUNT(CASE WHEN patient_gender = 'M' THEN 1 END) AS male_count,
    COUNT(CASE WHEN patient_gender = 'F' THEN 1 END) AS female_count
FROM 
    healthcare_patients
WHERE 
    patient_age IS NOT NULL
GROUP BY 
    age_group
ORDER BY 
    MIN(patient_age);

-- Age group by department referral breakdown
SELECT 
    CASE 
        WHEN patient_age < 13 THEN 'Pediatric (0-12)'
        WHEN patient_age < 18 THEN 'Adolescent (13-17)'
        WHEN patient_age < 30 THEN 'Young Adult (18-29)'
        WHEN patient_age < 45 THEN 'Adult (30-44)'
        WHEN patient_age < 65 THEN 'Middle Age (45-64)'
        ELSE 'Senior (65+)'
    END AS age_group,
    COALESCE(department_referral, 'No Referral') AS department,
    COUNT(*) AS patient_count,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction
FROM 
    healthcare_patients
WHERE 
    patient_age IS NOT NULL
GROUP BY 
    age_group, department_referral
ORDER BY 
    MIN(patient_age), patient_count DESC;

-- Race demographics analysis
SELECT 
    patient_race,
    COUNT(*) AS total_patients,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(patient_age), 2) AS avg_age,
    COUNT(CASE WHEN department_referral IS NOT NULL AND department_referral != 'None' THEN 1 END) AS referrals,
    ROUND(COUNT(CASE WHEN department_referral IS NOT NULL AND department_referral != 'None' THEN 1 END) * 100.0 / COUNT(*), 2) AS referral_rate,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction
FROM 
    healthcare_patients
GROUP BY 
    patient_race
ORDER BY 
    total_patients DESC;

-- ============================================================================
-- QUERY 5: DAY OF WEEK PATTERNS FOR OPERATIONAL INSIGHTS
-- Purpose: Analyze patient flow patterns by day of week and time of day
-- ============================================================================

-- Day of week analysis with operational metrics
SELECT 
    CASE CAST(strftime('%w', date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    CAST(strftime('%w', date) AS INTEGER) AS day_number,
    COUNT(*) AS total_patients,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    MAX(patient_waittime) AS max_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admissions,
    COUNT(CASE WHEN Moment = 'AM' THEN 1 END) AS morning_visits,
    COUNT(CASE WHEN Moment = 'PM' THEN 1 END) AS afternoon_visits,
    ROUND(COUNT(CASE WHEN patient_waittime > 45 THEN 1 END) * 100.0 / COUNT(*), 2) AS high_wait_percentage
FROM 
    healthcare_patients
WHERE 
    date IS NOT NULL
GROUP BY 
    day_of_week, day_number
ORDER BY 
    day_number;

-- Time of day (AM/PM) analysis
SELECT 
    Moment AS time_of_day,
    COUNT(*) AS total_patients,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admissions,
    COUNT(CASE WHEN department_referral IS NOT NULL AND department_referral != 'None' THEN 1 END) AS referrals,
    ROUND(AVG(patient_age), 2) AS avg_age
FROM 
    healthcare_patients
WHERE 
    Moment IS NOT NULL
GROUP BY 
    Moment
ORDER BY 
    Moment;

-- Combined day and time pattern analysis
SELECT 
    CASE CAST(strftime('%w', date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    Moment AS time_of_day,
    COUNT(*) AS patient_count,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    MAX(patient_waittime) AS peak_wait_time
FROM 
    healthcare_patients
WHERE 
    date IS NOT NULL AND Moment IS NOT NULL
GROUP BY 
    day_of_week, CAST(strftime('%w', date) AS INTEGER), Moment
ORDER BY 
    CAST(strftime('%w', date) AS INTEGER), Moment;

-- ============================================================================
-- BONUS QUERIES: ADDITIONAL INSIGHTS
-- ============================================================================

-- Top performing days (lowest wait time + highest satisfaction)
WITH daily_performance AS (
    SELECT 
        date,
        COUNT(*) AS patient_count,
        ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
        ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction
    FROM healthcare_patients
    WHERE patient_sat_score IS NOT NULL
    GROUP BY date
)
SELECT 
    date,
    patient_count,
    avg_wait_time,
    avg_satisfaction,
    RANK() OVER (ORDER BY avg_wait_time ASC, avg_satisfaction DESC) AS performance_rank
FROM daily_performance
ORDER BY performance_rank
LIMIT 10;

-- Patient satisfaction distribution
SELECT 
    patient_sat_score AS satisfaction_score,
    COUNT(*) AS patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time
FROM 
    healthcare_patients
WHERE 
    patient_sat_score IS NOT NULL
GROUP BY 
    patient_sat_score
ORDER BY 
    patient_sat_score DESC;

-- Gender-based analysis
SELECT 
    patient_gender,
    COUNT(*) AS total_patients,
    ROUND(AVG(patient_age), 2) AS avg_age,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time,
    ROUND(AVG(patient_sat_score), 2) AS avg_satisfaction,
    COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) AS admissions,
    ROUND(COUNT(CASE WHEN patient_admin_flag = 'True' THEN 1 END) * 100.0 / COUNT(*), 2) AS admission_rate
FROM 
    healthcare_patients
WHERE 
    patient_gender IS NOT NULL
GROUP BY 
    patient_gender;

-- Department workload by month
SELECT 
    strftime('%Y-%m', date) AS month,
    COALESCE(department_referral, 'No Referral') AS department,
    COUNT(*) AS patient_count,
    ROUND(AVG(patient_waittime), 2) AS avg_wait_time
FROM 
    healthcare_patients
GROUP BY 
    month, department_referral
ORDER BY 
    month, patient_count DESC;
