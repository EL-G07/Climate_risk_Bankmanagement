#!/bin/bash
# deploy.sh - One-click deployment script

echo "======================================"
echo "  DEPLOYING RISK DASHBOARD"
echo "======================================"

# Check for required packages
echo "📦 Checking dependencies..."

# Check if ipython is installed
if ! command -v ipython &> /dev/null; then
    echo "⚠️  IPython not found. Installing..."
    pip install ipython
fi

# Check if dash is installed
python -c "import dash" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Dash not found. Installing..."
    pip install dash plotly pandas geopandas folium
fi

echo "✅ Dependencies ready"
echo ""

# Run the deployment script
echo "🚀 Starting deployment..."
python start_servers.py