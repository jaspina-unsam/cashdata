#!/bin/bash

# CashData - Project Status Report Generator
# Generates a quick status report with key metrics

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    CASHDATA PROJECT STATUS                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Date
echo "📅 Report Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Git Info
echo "🔧 Git Information:"
echo "   Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "   Last Commit: $(git log -1 --pretty=format:'%h - %s (%cr)')"
echo ""

# Backend Status
echo "🐍 Backend Status:"
cd backend
if [ -f "cashdata.db" ]; then
    DB_SIZE=$(du -h cashdata.db | cut -f1)
    echo "   Database: ✅ Present ($DB_SIZE)"
else
    echo "   Database: ❌ Not found"
fi

# Count migrations
MIGRATIONS=$(ls alembic/versions/*.py 2>/dev/null | wc -l | xargs)
echo "   Migrations: $MIGRATIONS applied"

# Run tests and capture results
echo "   Running tests..."
TEST_OUTPUT=$(poetry run pytest tests/ --tb=no -q 2>&1)
PASSED=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+")
FAILED=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+")

if [ -z "$FAILED" ] || [ "$FAILED" = "0" ]; then
    echo "   Tests: ✅ $PASSED passed"
else
    echo "   Tests: ⚠️  $PASSED passed, $FAILED failed"
fi

cd ..

# Frontend Status
echo ""
echo "⚛️  Frontend Status:"
cd frontend
if [ -d "node_modules" ]; then
    echo "   Dependencies: ✅ Installed"
else
    echo "   Dependencies: ❌ Not installed (run npm install)"
fi

if [ -d "dist" ]; then
    echo "   Build: ✅ Present"
else
    echo "   Build: ⚠️  No production build"
fi
cd ..

# Documentation Status
echo ""
echo "📚 Documentation Status:"
DOCS_COUNT=$(find .support -name "*.md" -o -name "*.yaml" -o -name "*.csv" | wc -l | xargs)
echo "   Documentation Files: $DOCS_COUNT"

# Count completed stories
if [ -f ".support/unified_board.csv" ]; then
    TOTAL_STORIES=$(tail -n +2 .support/unified_board.csv | wc -l | xargs)
    DONE_STORIES=$(tail -n +2 .support/unified_board.csv | grep ",Done," | wc -l | xargs)
    BACKLOG_STORIES=$(tail -n +2 .support/unified_board.csv | grep ",Backlog," | wc -l | xargs)
    
    echo "   Total Stories: $TOTAL_STORIES"
    echo "   ✅ Done: $DONE_STORIES"
    echo "   📋 Backlog: $BACKLOG_STORIES"
    
    # Calculate percentage
    if [ "$TOTAL_STORIES" -gt 0 ]; then
        PERCENT=$((DONE_STORIES * 100 / TOTAL_STORIES))
        echo "   Progress: $PERCENT% complete"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                         QUICK LINKS                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📖 Documentation:"
echo "   • Handoff (AI):     .support/handoff.yaml"
echo "   • Status (Human):   .support/estado_proyecto.md"
echo "   • Stories Board:    .support/unified_board.csv"
echo ""
echo "🚀 Start Application:"
echo "   • Backend:  ./start-backend.sh"
echo "   • Frontend: ./start-frontend.sh"
echo ""
echo "🧪 Run Tests:"
echo "   • cd backend && poetry run pytest tests/ -v"
echo ""
echo "📊 API Documentation:"
echo "   • http://localhost:8000/docs (when backend is running)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
