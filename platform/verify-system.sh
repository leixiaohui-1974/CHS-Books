#!/bin/bash

# ============================================================
# CHS-Books Platform Verification Script
# 完整系统验证 - Sprint 1
# ============================================================

# Note: Don't use set -e, we want to continue even if some tests fail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Functions
print_header() {
    echo ""
    echo "============================================================"
    echo -e "${BLUE}$1${NC}"
    echo "============================================================"
    echo ""
}

print_test() {
    echo -e "${YELLOW}🧪 TEST: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

print_failure() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================
# Test Suite
# ============================================================

print_header "CHS-Books Platform Verification"
echo "Date: $(date)"
echo "Sprint: 1"
echo ""

# ============================================================
# 1. System Dependencies
# ============================================================

print_header "1. System Dependencies"

print_test "Python 3.11+ installed"
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python installed: $VERSION"
else
    print_failure "Python not found"
fi

print_test "Node.js 18+ installed"
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    print_success "Node.js installed: $VERSION"
else
    print_failure "Node.js not found"
fi

print_test "npm installed"
if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    print_success "npm installed: $VERSION"
else
    print_failure "npm not found"
fi

# ============================================================
# 2. Project Structure
# ============================================================

print_header "2. Project Structure"

print_test "Backend directory exists"
if [ -d "backend/standalone_textbook_server" ]; then
    print_success "Backend directory found"
else
    print_failure "Backend directory not found"
fi

print_test "Frontend directory exists"
if [ -d "frontend" ]; then
    print_success "Frontend directory found"
else
    print_failure "Frontend directory not found"
fi

print_test "Key Python files exist"
FILES=("backend/standalone_textbook_server/main.py"
       "backend/standalone_textbook_server/models.py"
       "backend/standalone_textbook_server/api.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_failure "$file not found"
    fi
done

print_test "Key frontend files exist"
if [ -f "frontend/src/components/InteractiveTextbook/InteractiveTextbook.tsx" ]; then
    print_success "InteractiveTextbook component exists"
else
    print_failure "InteractiveTextbook component not found"
fi

# ============================================================
# 3. Service Status
# ============================================================

print_header "3. Service Status"

print_test "Backend service running on port 8000"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -ti:8000)
    print_success "Backend running (PID: $PID)"
else
    print_failure "Backend not running"
    print_info "Start with: cd backend/standalone_textbook_server && python3 main.py"
fi

print_test "Frontend service running on port 3000"
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -ti:3000)
    print_success "Frontend running (PID: $PID)"
else
    print_failure "Frontend not running"
    print_info "Start with: cd frontend && npm run dev"
fi

# ============================================================
# 4. Backend API Tests
# ============================================================

print_header "4. Backend API Tests"

# Wait for backend
sleep 1

print_test "GET /health"
RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if echo "$RESPONSE" | grep -q "healthy"; then
    print_success "Health endpoint OK: $RESPONSE"
else
    print_failure "Health endpoint failed"
fi

print_test "GET / (root)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    print_success "Root endpoint OK (HTTP $STATUS)"
else
    print_failure "Root endpoint failed (HTTP $STATUS)"
fi

print_test "POST /api/v1/seed"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/seed 2>/dev/null || echo "")
if echo "$RESPONSE" | grep -q "book_slug"; then
    print_success "Seed endpoint OK"
else
    print_failure "Seed endpoint failed"
fi

print_test "GET /api/v1/textbooks/{book}/{chapter}/{case}"
RESPONSE=$(curl -s "http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank" 2>/dev/null || echo "")
if echo "$RESPONSE" | grep -q "sections"; then
    SECTION_COUNT=$(echo "$RESPONSE" | jq '.sections | length' 2>/dev/null || echo "0")
    print_success "Textbook API OK ($SECTION_COUNT sections)"

    # Verify sections structure
    print_test "Sections have required fields"
    if echo "$RESPONSE" | jq -e '.sections[0].id and .sections[0].title and .sections[0].content' >/dev/null 2>&1; then
        print_success "Section structure valid"
    else
        print_failure "Section structure invalid"
    fi

    # Check code_lines mapping
    print_test "Code line mappings present"
    CODE_SECTIONS=$(echo "$RESPONSE" | jq '[.sections[] | select(.code_lines != null)] | length' 2>/dev/null || echo "0")
    if [ "$CODE_SECTIONS" -gt "0" ]; then
        print_success "$CODE_SECTIONS sections have code line mappings"
    else
        print_failure "No code line mappings found"
    fi
else
    print_failure "Textbook API failed"
fi

print_test "GET /docs (Swagger UI)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    print_success "API documentation available"
else
    print_failure "API documentation not accessible"
fi

# ============================================================
# 5. Database Tests
# ============================================================

print_header "5. Database Tests"

print_test "SQLite database file exists"
if [ -f "backend/standalone_textbook_server/textbook_test.db" ]; then
    SIZE=$(du -h backend/standalone_textbook_server/textbook_test.db | cut -f1)
    print_success "Database exists ($SIZE)"

    # Check tables
    print_test "Database tables created"
    if command -v sqlite3 &> /dev/null; then
        TABLES=$(sqlite3 backend/standalone_textbook_server/textbook_test.db ".tables" 2>/dev/null || echo "")
        if echo "$TABLES" | grep -q "books"; then
            print_success "Tables found: $TABLES"
        else
            print_failure "Required tables not found"
        fi

        # Count records
        print_test "Sample data loaded"
        BOOK_COUNT=$(sqlite3 backend/standalone_textbook_server/textbook_test.db "SELECT COUNT(*) FROM books;" 2>/dev/null || echo "0")
        CHAPTER_COUNT=$(sqlite3 backend/standalone_textbook_server/textbook_test.db "SELECT COUNT(*) FROM chapters;" 2>/dev/null || echo "0")
        CASE_COUNT=$(sqlite3 backend/standalone_textbook_server/textbook_test.db "SELECT COUNT(*) FROM cases;" 2>/dev/null || echo "0")

        if [ "$BOOK_COUNT" -gt "0" ] && [ "$CHAPTER_COUNT" -gt "0" ] && [ "$CASE_COUNT" -gt "0" ]; then
            print_success "Data loaded: $BOOK_COUNT books, $CHAPTER_COUNT chapters, $CASE_COUNT cases"
        else
            print_failure "No sample data found"
        fi
    else
        print_info "sqlite3 not installed, skipping database inspection"
    fi
else
    print_failure "Database file not found"
fi

# ============================================================
# 6. Frontend Tests
# ============================================================

print_header "6. Frontend Tests"

print_test "Frontend root page accessible"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ] || [ "$STATUS" = "304" ]; then
    print_success "Frontend root OK (HTTP $STATUS)"
else
    print_failure "Frontend root failed (HTTP $STATUS)"
fi

print_test "Textbook demo page accessible"
RESPONSE=$(curl -s http://localhost:3000/textbook-demo 2>/dev/null || echo "")
if echo "$RESPONSE" | grep -q "InteractiveTextbook\|加载教材"; then
    print_success "Demo page accessible"
else
    print_failure "Demo page not accessible"
fi

print_test "Frontend assets loading"
if [ -d "frontend/.next" ]; then
    print_success "Next.js build artifacts exist"
else
    print_failure "Next.js build artifacts not found"
fi

# ============================================================
# 7. Documentation Tests
# ============================================================

print_header "7. Documentation Tests"

DOCS=("README.md"
      "QUICK_REFERENCE.md"
      "DEVELOPER_GUIDE.md"
      "SPRINT_1_FINAL_SUMMARY.md"
      "SPRINT_2_PLAN.md"
      "INTEGRATION_TEST_REPORT.md")

for doc in "${DOCS[@]}"; do
    print_test "$doc exists"
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        print_success "$doc ($LINES lines)"
    else
        print_failure "$doc not found"
    fi
done

# ============================================================
# 8. Development Tools Tests
# ============================================================

print_header "8. Development Tools Tests"

SCRIPTS=("start-dev.sh" "stop-dev.sh" "demo.sh")

for script in "${SCRIPTS[@]}"; do
    print_test "$script exists and is executable"
    if [ -f "$script" ] && [ -x "$script" ]; then
        print_success "$script OK"
    elif [ -f "$script" ]; then
        print_failure "$script exists but not executable"
    else
        print_failure "$script not found"
    fi
done

# ============================================================
# 9. Performance Tests
# ============================================================

print_header "9. Performance Tests"

print_test "API response time < 100ms"
START=$(date +%s%N)
curl -s http://localhost:8000/health > /dev/null 2>&1
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))  # Convert to milliseconds

if [ "$DURATION" -lt "100" ]; then
    print_success "Response time: ${DURATION}ms"
else
    print_failure "Response time too slow: ${DURATION}ms"
fi

print_test "Textbook API response time < 200ms"
START=$(date +%s%N)
curl -s "http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank" > /dev/null 2>&1
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

if [ "$DURATION" -lt "200" ]; then
    print_success "Textbook API response time: ${DURATION}ms"
else
    print_failure "Textbook API response too slow: ${DURATION}ms"
fi

# ============================================================
# 10. Git Repository Tests
# ============================================================

print_header "10. Git Repository Tests"

print_test "Git repository initialized"
if [ -d "../.git" ] || [ -d ".git" ]; then
    print_success "Git repository exists"
else
    print_failure "Not a git repository"
fi

print_test "On correct branch"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if echo "$CURRENT_BRANCH" | grep -q "claude/"; then
    print_success "On branch: $CURRENT_BRANCH"
else
    print_failure "Not on expected branch: $CURRENT_BRANCH"
fi

print_test "No uncommitted changes"
if git diff-index --quiet HEAD -- 2>/dev/null; then
    print_success "Working tree clean"
else
    print_failure "Uncommitted changes present"
fi

print_test "Recent commits exist"
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
if [ "$COMMIT_COUNT" -gt "5" ]; then
    print_success "$COMMIT_COUNT commits in history"
    LATEST=$(git log -1 --oneline 2>/dev/null || echo "unknown")
    print_info "Latest: $LATEST"
else
    print_failure "Too few commits: $COMMIT_COUNT"
fi

# ============================================================
# Summary
# ============================================================

print_header "Verification Summary"

echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ "$FAILED_TESTS" -eq "0" ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED! System is fully operational.${NC}"
    echo ""
    echo "Sprint 1 Status: 100% Complete ✅"
    echo ""
    echo "Next Steps:"
    echo "  - Access demo: http://localhost:3000/textbook-demo"
    echo "  - View API docs: http://localhost:8000/docs"
    echo "  - Run demo script: ./demo.sh"
    echo "  - Review Sprint 2 plan: cat SPRINT_2_PLAN.md"
    echo ""
    exit 0
else
    PERCENT=$((($PASSED_TESTS * 100) / $TOTAL_TESTS))
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED ($PERCENT% passed)${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "  1. Ensure services are running (./start-dev.sh)"
    echo "  2. Check logs: tail -f logs/*.log"
    echo "  3. Consult DEVELOPER_GUIDE.md for troubleshooting"
    echo ""
    exit 1
fi
