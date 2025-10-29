# Healthcare Analytics Project - Installation Script
# PowerShell script to set up the complete project

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "           HEALTHCARE ANALYTICS PROJECT - AUTOMATED SETUP                      " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check pip installation
Write-Host ""
Write-Host "Step 2: Checking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip found" -ForegroundColor Green
} catch {
    Write-Host "✗ pip not found. Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# Install dependencies
Write-Host ""
Write-Host "Step 3: Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

try {
    pip install -r requirements.txt --quiet
    Write-Host "✓ All dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Error installing some dependencies. Trying again..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Verify critical packages
Write-Host ""
Write-Host "Step 4: Verifying installed packages..." -ForegroundColor Yellow

$packages = @("pandas", "numpy", "matplotlib", "seaborn", "schedule", "openpyxl")
$allInstalled = $true

foreach ($package in $packages) {
    try {
        python -c "import $package" 2>&1 | Out-Null
        Write-Host "  ✓ $package" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $package - FAILED" -ForegroundColor Red
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    Write-Host ""
    Write-Host "⚠ Some packages failed to install. Please install manually:" -ForegroundColor Yellow
    Write-Host "  pip install pandas numpy matplotlib seaborn schedule openpyxl" -ForegroundColor Gray
    Write-Host ""
}

# Setup database
Write-Host ""
Write-Host "Step 5: Setting up database..." -ForegroundColor Yellow

try {
    python Scripts/setup_database.py
    Write-Host "✓ Database setup completed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Database setup encountered issues. Check logs for details." -ForegroundColor Yellow
}

# Create summary
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                           SETUP COMPLETE!                                     " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run complete analysis:" -ForegroundColor White
Write-Host "     python Scripts/run_all_analytics.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Or run individual components:" -ForegroundColor White
Write-Host "     python Scripts/data_quality_validator.py" -ForegroundColor Gray
Write-Host "     python Scripts/weekly_performance_report.py --mode once" -ForegroundColor Gray
Write-Host "     python Scripts/dashboard_visualizations.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. View documentation:" -ForegroundColor White
Write-Host "     - Quick Start: QUICK_START.md" -ForegroundColor Gray
Write-Host "     - Full Docs: README.md" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Access SQL queries:" -ForegroundColor White
Write-Host "     SQL_Queries/healthcare_analytics_queries.sql" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to run analytics now
$response = Read-Host "Do you want to run the complete analytics now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting complete analytics..." -ForegroundColor Yellow
    python Scripts/run_all_analytics.py
} else {
    Write-Host ""
    Write-Host "You can run analytics anytime with:" -ForegroundColor Yellow
    Write-Host "  python Scripts/run_all_analytics.py" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Happy analyzing! 📊" -ForegroundColor Cyan
Write-Host ""
