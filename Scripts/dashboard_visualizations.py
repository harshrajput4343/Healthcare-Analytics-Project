"""
Healthcare Analytics - Interactive Dashboard and Visualizations
================================================================
Creates comprehensive visualizations and interactive dashboard for
healthcare analytics insights.

Author: Healthcare Analytics Team
Date: 2025-10-29
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_PATH = PROJECT_ROOT / "Dataset" / "HEALTHCARE PATIENT DATSET.csv"
VISUALIZATIONS_DIR = PROJECT_ROOT / "Visualizations"
REPORTS_DIR = PROJECT_ROOT / "Reports"

# Create directories
VISUALIZATIONS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# VISUALIZATION GENERATOR
# ============================================================================

class HealthcareDashboardVisualizer:
    """Generate comprehensive healthcare analytics visualizations"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def create_monthly_trends_chart(self):
        """Monthly patient volume and trends"""
        print("Creating monthly trends visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Monthly Patient Volume Trends', fontsize=16, fontweight='bold')
        
        # Monthly patient counts
        monthly_counts = self.df.groupby(self.df['date'].dt.to_period('M')).size()
        monthly_counts.index = monthly_counts.index.to_timestamp()
        
        axes[0, 0].plot(monthly_counts.index, monthly_counts.values, marker='o', linewidth=2, color='#2E86AB')
        axes[0, 0].set_title('Monthly Patient Volume', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Number of Patients')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Monthly average wait time
        monthly_wait = self.df.groupby(self.df['date'].dt.to_period('M'))['patient_waittime'].mean()
        monthly_wait.index = monthly_wait.index.to_timestamp()
        
        axes[0, 1].plot(monthly_wait.index, monthly_wait.values, marker='s', linewidth=2, color='#A23B72')
        axes[0, 1].set_title('Monthly Average Wait Time', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Month')
        axes[0, 1].set_ylabel('Average Wait Time (minutes)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Monthly satisfaction scores
        monthly_sat = self.df.groupby(self.df['date'].dt.to_period('M'))['patient_sat_score'].mean()
        monthly_sat.index = monthly_sat.index.to_timestamp()
        
        axes[1, 0].plot(monthly_sat.index, monthly_sat.values, marker='^', linewidth=2, color='#F18F01')
        axes[1, 0].set_title('Monthly Average Satisfaction Score', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Average Satisfaction (0-10)')
        axes[1, 0].set_ylim(0, 10)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Admission rate trend
        monthly_admin = self.df.groupby(self.df['date'].dt.to_period('M')).apply(
            lambda x: (x['patient_admin_flag'] == 'True').sum() / len(x) * 100
        )
        monthly_admin.index = monthly_admin.index.to_timestamp()
        
        axes[1, 1].plot(monthly_admin.index, monthly_admin.values, marker='D', linewidth=2, color='#C73E1D')
        axes[1, 1].set_title('Monthly Admission Rate', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Admission Rate (%)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"monthly_trends_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def create_department_performance_chart(self):
        """Department-wise performance metrics"""
        print("Creating department performance visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Department Performance Metrics', fontsize=16, fontweight='bold')
        
        # Filter out None/NaN departments and prepare data
        dept_data = self.df[self.df['department_referral'].notna() & (self.df['department_referral'] != 'None')].copy()
        
        # Patient volume by department
        dept_counts = dept_data['department_referral'].value_counts()
        axes[0, 0].barh(dept_counts.index, dept_counts.values, color='#2E86AB', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Patient Volume by Department', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Number of Patients')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(dept_counts.values):
            axes[0, 0].text(v + 10, i, str(v), va='center', fontsize=9)
        
        # Average wait time by department
        dept_wait = dept_data.groupby('department_referral')['patient_waittime'].mean().sort_values(ascending=True)
        colors_wait = ['#27AE60' if x < 30 else '#F39C12' if x < 45 else '#E74C3C' for x in dept_wait.values]
        axes[0, 1].barh(dept_wait.index, dept_wait.values, color=colors_wait, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Average Wait Time by Department', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Average Wait Time (minutes)')
        axes[0, 1].grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(dept_wait.values):
            axes[0, 1].text(v + 1, i, f'{v:.1f}', va='center', fontsize=9)
        
        # Average satisfaction by department
        dept_sat = dept_data.groupby('department_referral')['patient_sat_score'].mean().sort_values(ascending=False)
        dept_sat = dept_sat.dropna()
        colors_sat = ['#27AE60' if x >= 7 else '#F39C12' if x >= 5 else '#E74C3C' for x in dept_sat.values]
        axes[1, 0].barh(dept_sat.index, dept_sat.values, color=colors_sat, edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('Average Satisfaction by Department', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Average Satisfaction Score (0-10)')
        axes[1, 0].set_xlim(0, 10)
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(dept_sat.values):
            axes[1, 0].text(v + 0.2, i, f'{v:.2f}', va='center', fontsize=9)
        
        # Admission rate by department
        dept_admin = dept_data.groupby('department_referral').apply(
            lambda x: (x['patient_admin_flag'] == True).sum() / len(x) * 100
        ).sort_values(ascending=False)
        axes[1, 1].barh(dept_admin.index, dept_admin.values, color='#8E44AD', edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('Admission Rate by Department', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Admission Rate (%)')
        axes[1, 1].set_xlim(0, max(dept_admin.values) * 1.1)  # Add 10% padding
        axes[1, 1].grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, v in enumerate(dept_admin.values):
            axes[1, 1].text(v + 1, i, f'{v:.1f}%', va='center', fontsize=9)
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"department_performance_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def create_wait_time_satisfaction_correlation(self):
        """Wait time vs satisfaction correlation analysis"""
        print("Creating wait time vs satisfaction correlation visualization...")
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Wait Time vs Patient Satisfaction Analysis', fontsize=16, fontweight='bold')
        
        # Scatter plot with trend line
        data_complete = self.df.dropna(subset=['patient_waittime', 'patient_sat_score'])
        
        axes[0].scatter(data_complete['patient_waittime'], data_complete['patient_sat_score'], 
                       alpha=0.3, s=30, color='#3498DB')
        
        # Add trend line
        z = np.polyfit(data_complete['patient_waittime'], data_complete['patient_sat_score'], 1)
        p = np.poly1d(z)
        axes[0].plot(data_complete['patient_waittime'].sort_values(), 
                    p(data_complete['patient_waittime'].sort_values()), 
                    "r--", linewidth=2, label=f'Trend: y={z[0]:.4f}x+{z[1]:.2f}')
        
        axes[0].set_title('Scatter Plot: Wait Time vs Satisfaction', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Wait Time (minutes)')
        axes[0].set_ylabel('Satisfaction Score (0-10)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Wait time buckets
        wait_bins = [0, 15, 30, 45, 60, 300]
        wait_labels = ['0-15', '15-30', '30-45', '45-60', '60+']
        data_complete['wait_bucket'] = pd.cut(data_complete['patient_waittime'], 
                                              bins=wait_bins, labels=wait_labels)
        
        bucket_stats = data_complete.groupby('wait_bucket')['patient_sat_score'].agg(['mean', 'count'])
        
        colors = ['#27AE60', '#2ECC71', '#F39C12', '#E67E22', '#E74C3C']
        axes[1].bar(bucket_stats.index, bucket_stats['mean'], color=colors, alpha=0.7, edgecolor='black')
        
        # Add count labels on bars
        for i, (idx, row) in enumerate(bucket_stats.iterrows()):
            axes[1].text(i, row['mean'] + 0.2, f"n={int(row['count'])}", 
                        ha='center', fontsize=9)
        
        axes[1].set_title('Average Satisfaction by Wait Time Bucket', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Wait Time Bucket (minutes)')
        axes[1].set_ylabel('Average Satisfaction Score')
        axes[1].set_ylim(0, 10)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"wait_satisfaction_correlation_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def create_demographics_analysis(self):
        """Patient demographics analysis"""
        print("Creating demographics analysis visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Patient Demographics Analysis', fontsize=16, fontweight='bold')
        
        # Age distribution
        axes[0, 0].hist(self.df['patient_age'].dropna(), bins=30, color='#3498DB', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Age Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Age (years)')
        axes[0, 0].set_ylabel('Number of Patients')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Age groups with referral rates
        age_bins = [0, 12, 17, 29, 44, 64, 120]
        age_labels = ['Pediatric\n(0-12)', 'Adolescent\n(13-17)', 'Young Adult\n(18-29)',
                     'Adult\n(30-44)', 'Middle Age\n(45-64)', 'Senior\n(65+)']
        self.df['age_group'] = pd.cut(self.df['patient_age'], bins=age_bins, labels=age_labels)
        
        age_counts = self.df['age_group'].value_counts().sort_index()
        axes[0, 1].bar(age_counts.index, age_counts.values, color='#E67E22', edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Patient Distribution by Age Group', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Age Group')
        axes[0, 1].set_ylabel('Number of Patients')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Gender distribution
        gender_counts = self.df['patient_gender'].value_counts()
        colors_gender = ['#3498DB', '#E91E63', '#F39C12', '#9B59B6']  # More colors for additional values
        axes[1, 0].pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
                      colors=colors_gender[:len(gender_counts)], startangle=90, textprops={'fontsize': 11})
        axes[1, 0].set_title('Gender Distribution', fontsize=12, fontweight='bold')
        
        # Race distribution
        race_counts = self.df['patient_race'].value_counts().head(8)
        axes[1, 1].barh(race_counts.index, race_counts.values, color='#9B59B6', edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('Patient Distribution by Race (Top 8)', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Number of Patients')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"demographics_analysis_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def create_day_of_week_patterns(self):
        """Day of week operational patterns"""
        print("Creating day of week patterns visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Day of Week Operational Patterns', fontsize=16, fontweight='bold')
        
        # Day of week mapping
        self.df['day_of_week'] = self.df['date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Patient volume by day
        day_counts = self.df['day_of_week'].value_counts().reindex(day_order)
        axes[0, 0].bar(range(len(day_counts)), day_counts.values, color='#16A085', edgecolor='black', alpha=0.7)
        axes[0, 0].set_xticks(range(len(day_counts)))
        axes[0, 0].set_xticklabels(day_order, rotation=45, ha='right')
        axes[0, 0].set_title('Patient Volume by Day of Week', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Number of Patients')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Average wait time by day
        day_wait = self.df.groupby('day_of_week')['patient_waittime'].mean().reindex(day_order)
        colors_day = ['#27AE60' if x < 35 else '#F39C12' if x < 40 else '#E74C3C' for x in day_wait.values]
        axes[0, 1].bar(range(len(day_wait)), day_wait.values, color=colors_day, edgecolor='black', alpha=0.7)
        axes[0, 1].set_xticks(range(len(day_wait)))
        axes[0, 1].set_xticklabels(day_order, rotation=45, ha='right')
        axes[0, 1].set_title('Average Wait Time by Day of Week', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Average Wait Time (minutes)')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # AM vs PM distribution
        moment_counts = self.df['Moment'].value_counts()
        axes[1, 0].pie(moment_counts.values, labels=moment_counts.index, autopct='%1.1f%%',
                      colors=['#F39C12', '#3498DB'], startangle=90, textprops={'fontsize': 11})
        axes[1, 0].set_title('AM vs PM Visit Distribution', fontsize=12, fontweight='bold')
        
        # Heatmap: Day vs Time of day
        heatmap_data = self.df.groupby(['day_of_week', 'Moment']).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(day_order)
        
        im = axes[1, 1].imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
        axes[1, 1].set_xticks(range(len(heatmap_data.columns)))
        axes[1, 1].set_xticklabels(heatmap_data.columns)
        axes[1, 1].set_yticks(range(len(heatmap_data.index)))
        axes[1, 1].set_yticklabels(heatmap_data.index)
        axes[1, 1].set_title('Patient Volume Heatmap: Day vs Time', fontsize=12, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=axes[1, 1])
        cbar.set_label('Patient Count', rotation=270, labelpad=15)
        
        # Add values to heatmap
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                text = axes[1, 1].text(j, i, int(heatmap_data.values[i, j]),
                                      ha="center", va="center", color="black", fontsize=10)
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"day_of_week_patterns_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def create_satisfaction_analysis(self):
        """Patient satisfaction detailed analysis"""
        print("Creating satisfaction analysis visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Patient Satisfaction Analysis', fontsize=16, fontweight='bold')
        
        # Satisfaction score distribution
        sat_data = self.df['patient_sat_score'].dropna()
        axes[0, 0].hist(sat_data, bins=11, range=(0, 10), color='#3498DB', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Satisfaction Score Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Satisfaction Score (0-10)')
        axes[0, 0].set_ylabel('Number of Patients')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Satisfaction categories
        sat_categories = pd.cut(sat_data, bins=[0, 3, 6, 8, 10], 
                               labels=['Poor (0-3)', 'Fair (4-6)', 'Good (7-8)', 'Excellent (9-10)'])
        cat_counts = sat_categories.value_counts()
        colors_cat = ['#E74C3C', '#F39C12', '#3498DB', '#27AE60']
        axes[0, 1].pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%',
                      colors=colors_cat, startangle=90, textprops={'fontsize': 10})
        axes[0, 1].set_title('Satisfaction Categories', fontsize=12, fontweight='bold')
        
        # Satisfaction by department
        dept_sat = self.df[self.df['department_referral'].notna() & 
                          (self.df['department_referral'] != 'None')].groupby('department_referral')['patient_sat_score'].mean().sort_values(ascending=True)
        dept_sat = dept_sat.dropna()
        colors_dept = ['#27AE60' if x >= 7 else '#F39C12' if x >= 5 else '#E74C3C' for x in dept_sat.values]
        axes[1, 0].barh(dept_sat.index, dept_sat.values, color=colors_dept, edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('Average Satisfaction by Department', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Average Satisfaction Score (0-10)')
        axes[1, 0].set_xlim(0, 10)
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Satisfaction by age group
        age_sat = self.df.groupby('age_group')['patient_sat_score'].mean().dropna()
        axes[1, 1].bar(range(len(age_sat)), age_sat.values, color='#8E44AD', edgecolor='black', alpha=0.7)
        axes[1, 1].set_xticks(range(len(age_sat)))
        axes[1, 1].set_xticklabels(age_sat.index, rotation=45, ha='right')
        axes[1, 1].set_title('Average Satisfaction by Age Group', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Average Satisfaction Score')
        axes[1, 1].set_ylim(0, 10)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = VISUALIZATIONS_DIR / f"satisfaction_analysis_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {output_path}")
        return output_path
    
    def generate_all_visualizations(self):
        """Generate all dashboard visualizations"""
        print("\n" + "=" * 80)
        print("GENERATING HEALTHCARE ANALYTICS DASHBOARD VISUALIZATIONS")
        print("=" * 80 + "\n")
        
        visualizations = {}
        
        try:
            visualizations['monthly_trends'] = self.create_monthly_trends_chart()
            visualizations['department_performance'] = self.create_department_performance_chart()
            visualizations['wait_satisfaction'] = self.create_wait_time_satisfaction_correlation()
            visualizations['demographics'] = self.create_demographics_analysis()
            visualizations['day_patterns'] = self.create_day_of_week_patterns()
            visualizations['satisfaction'] = self.create_satisfaction_analysis()
            
            print("\n" + "=" * 80)
            print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
            print("=" * 80)
            print(f"\nVisualizations saved to: {VISUALIZATIONS_DIR}")
            print(f"Total visualizations created: {len(visualizations)}")
            print("=" * 80 + "\n")
            
            return visualizations
            
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
            import traceback
            traceback.print_exc()
            return visualizations

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("Loading healthcare dataset...")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        print(f"Dataset loaded: {len(df)} records\n")
        
        # Create visualizer
        visualizer = HealthcareDashboardVisualizer(df)
        
        # Generate all visualizations
        results = visualizer.generate_all_visualizations()
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
