# 🚀 Quick Start Guide - Healthcare Analytics Project

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 minute)
```powershell
cd "C:\Users\ASUS\OneDrive\Desktop\HEALTH DATA ANALYTICS"
pip install -r requirements.txt
```

### Step 2: Setup Database (30 seconds)
```powershell
python Scripts/setup_database.py
```

### Step 3: Run Your First Analysis (Choose One)

#### Option A: Generate All Reports and Visualizations
```powershell
python Scripts/run_all_analytics.py
```

#### Option B: Individual Components

**Data Quality Check:**
```powershell
python Scripts/data_quality_validator.py
```

**Weekly Performance Report:**
```powershell
python Scripts/weekly_performance_report.py --mode once
```

**Dashboard Visualizations:**
```powershell
python Scripts/dashboard_visualizations.py
```

---

## 📋 Common Commands

### Run SQL Queries
```powershell
# Using Python
python -c "import sqlite3, pandas as pd; conn = sqlite3.connect('healthcare_analytics.db'); df = pd.read_sql_query('SELECT * FROM healthcare_patients LIMIT 10', conn); print(df)"
```

### Schedule Automated Reports
```powershell
# Runs every Monday at 9:00 AM
python Scripts/weekly_performance_report.py --mode schedule
```

### View Latest Reports
```powershell
# Open Reports folder
explorer Reports

# Open Visualizations folder
explorer Visualizations

# View logs
explorer Logs
```

---

## 📊 What You Get

After running `run_all_analytics.py`, you'll have:

### 📁 Reports/ folder:
- ✅ `Weekly_Performance_Report_*.xlsx` - Complete performance metrics
- ✅ `Data_Quality_Report_*.csv` - Data quality validation results
- ✅ `Weekly_Summary_*.csv` - Quick summary stats
- ✅ `Department_Performance_*.csv` - Department-wise metrics
- ✅ `Age_Group_Analysis_*.csv` - Demographics breakdown

### 📁 Visualizations/ folder:
- 📈 `monthly_trends_*.png` - 4 trend charts
- 📊 `department_performance_*.png` - 4 department charts
- 🔗 `wait_satisfaction_correlation_*.png` - Correlation analysis
- 👥 `demographics_analysis_*.png` - 4 demographic charts
- 📅 `day_of_week_patterns_*.png` - Weekly patterns
- ⭐ `satisfaction_analysis_*.png` - Satisfaction insights

### 📁 Logs/ folder:
- 📝 Performance report logs
- ⚠️ Data quality issue logs
- 📋 Execution summaries

---

## 🎯 Quick Analytics Tasks

### Task 1: Monthly Patient Trends
```powershell
python -c "import sqlite3, pandas as pd; conn = sqlite3.connect('healthcare_analytics.db'); df = pd.read_sql_query(\"SELECT strftime('%Y-%m', date) AS month, COUNT(*) AS patients FROM healthcare_patients GROUP BY month ORDER BY month\", conn); print(df)"
```

### Task 2: Department Performance
```powershell
python -c "import sqlite3, pandas as pd; conn = sqlite3.connect('healthcare_analytics.db'); df = pd.read_sql_query(\"SELECT department_referral, COUNT(*) AS patients, ROUND(AVG(patient_waittime), 2) AS avg_wait FROM healthcare_patients WHERE department_referral IS NOT NULL GROUP BY department_referral ORDER BY patients DESC LIMIT 10\", conn); print(df)"
```

### Task 3: Check Data Quality Score
```powershell
python Scripts/data_quality_validator.py
# Look for "Overall Quality Score" in output
```

---

## 🔍 Troubleshooting

### Problem: "Module not found"
**Solution:**
```powershell
pip install pandas numpy matplotlib seaborn schedule openpyxl
```

### Problem: "Database not found"
**Solution:**
```powershell
python Scripts/setup_database.py
```

### Problem: "Permission denied" when saving reports
**Solution:**
- Close any open Excel files from the Reports folder
- Run command prompt as Administrator

### Problem: Charts not displaying properly
**Solution:**
```powershell
pip install --upgrade matplotlib seaborn
```

---

## 📈 Key Metrics to Monitor

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Average Wait Time | < 30 min | 30-45 min | > 45 min |
| Patient Satisfaction | > 7.0 | 5.0-7.0 | < 5.0 |
| Data Quality Score | > 90% | 80-90% | < 80% |
| Admission Rate | 40-60% | 30-40% or 60-70% | < 30% or > 70% |

---

## 💡 Pro Tips

1. **Run data quality checks first** before analyzing
2. **Review logs** for any warnings or errors
3. **Compare reports** over time to track improvements
4. **Use visualizations** for presentations and dashboards
5. **Schedule reports** to run automatically

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review logs in `Logs/` folder
3. Verify Python version: `python --version` (need 3.8+)
4. Check installed packages: `pip list`

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Database created and populated
- [ ] Can run data quality validator
- [ ] Can generate reports
- [ ] Can create visualizations
- [ ] Reports folder has files
- [ ] Visualizations folder has charts

---

**Ready to dive deeper?** Check out `README.md` for comprehensive documentation!

**Project Version:** 1.0.0  
**Last Updated:** 2025-10-29
