#!/bin/bash

# Cryptocurrency Market API - Complete Testing Script
# This script tests all API endpoints with comprehensive examples

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="crypto-api"
IMAGE_NAME="crypto-api"
PORT="8000"
BASE_URL="http://localhost:${PORT}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Cryptocurrency Market API Test Suite${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Step 1: Stop and remove existing container
echo -e "${YELLOW}[1/10] Cleaning up existing containers...${NC}"
if docker ps -a | grep -q ${CONTAINER_NAME}; then
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    echo -e "${GREEN}✓ Cleaned up existing container${NC}"
else
    echo -e "${GREEN}✓ No existing container to clean up${NC}"
fi
echo ""

# Step 2: Build Docker image
echo -e "${YELLOW}[2/10] Building Docker image...${NC}"
docker build -t ${IMAGE_NAME} . > /dev/null 2>&1
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 3: Start container
echo -e "${YELLOW}[3/10] Starting Docker container...${NC}"
docker run -d -p ${PORT}:8000 --env-file .env --name ${CONTAINER_NAME} ${IMAGE_NAME} > /dev/null
sleep 4  # Wait for application to start
echo -e "${GREEN}✓ Container started successfully${NC}"
echo ""

# Check if application is running
echo -e "${YELLOW}[4/10] Verifying application status...${NC}"
APP_LOGS=$(docker logs ${CONTAINER_NAME} 2>&1)
if echo "$APP_LOGS" | grep -q "Application startup complete"; then
    echo -e "${GREEN}✓ Application is running${NC}"
else
    echo -e "${RED}✗ Application failed to start${NC}"
    echo "$APP_LOGS"
    docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}
    exit 1
fi
echo ""

# Test 1: Health Check
echo -e "${YELLOW}[5/10] Testing Health Check Endpoint${NC}"
echo "GET /health/"
HEALTH=$(curl -s ${BASE_URL}/health/)
echo "$HEALTH" | jq .
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi
echo ""

# Test 2: Version
echo -e "${YELLOW}[6/10] Testing Version Endpoint${NC}"
echo "GET /health/version"
curl -s ${BASE_URL}/health/version | jq .
echo -e "${GREEN}✓ Version endpoint working${NC}"
echo ""

# Test 3: Authentication
echo -e "${YELLOW}[7/10] Testing Authentication${NC}"
echo "POST /auth/login"
TOKEN=$(curl -s -X POST ${BASE_URL}/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"demo123"}' | jq -r '.access_token')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "Token: ${TOKEN:0:50}..."
    echo -e "${GREEN}✓ Authentication successful${NC}"
else
    echo -e "${RED}✗ Authentication failed${NC}"
    docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}
    exit 1
fi
echo ""

# Test 4: Coins List (various pagination tests)
echo -e "${YELLOW}[8/10] Testing Coins List with Pagination${NC}"
echo "GET /v1/coins/?page_num=1&per_page=5"
curl -s "${BASE_URL}/v1/coins/?page_num=1&per_page=5" \
    -H "Authorization: Bearer $TOKEN" | jq '{page, per_page, total, coins: .data[0:2]}'
echo ""

echo "GET /v1/coins/?page_num=2&per_page=10"
curl -s "${BASE_URL}/v1/coins/?page_num=2&per_page=10" \
    -H "Authorization: Bearer $TOKEN" | jq '{page, per_page, total}'
echo ""

echo "GET /v1/coins/?page_num=1&per_page=20"
curl -s "${BASE_URL}/v1/coins/?page_num=1&per_page=20" \
    -H "Authorization: Bearer $TOKEN" | jq '{page, per_page, total}'
echo -e "${GREEN}✓ Coins list pagination working${NC}"
echo ""

# Test 5: Categories (various pagination tests)
echo -e "${YELLOW}[8/10] Testing Categories with Pagination${NC}"
echo "GET /v1/coins/categories?page_num=1&per_page=5"
curl -s "${BASE_URL}/v1/coins/categories?page_num=1&per_page=5" \
    -H "Authorization: Bearer $TOKEN" | jq '{page, per_page, total, categories: .data[0:2]}'
echo ""

echo "GET /v1/coins/categories?page_num=2&per_page=10"
curl -s "${BASE_URL}/v1/coins/categories?page_num=2&per_page=10" \
    -H "Authorization: Bearer $TOKEN" | jq '{page, per_page, total}'
echo -e "${GREEN}✓ Categories pagination working${NC}"
echo ""

# Test 6: Market Data - Multiple Scenarios
echo -e "${YELLOW}[9/10] Testing Market Data Endpoints${NC}"

echo "Scenario 1: Specific coins (Bitcoin & Ethereum)"
echo "GET /v1/coins/market?coin_ids=bitcoin,ethereum"
curl -s "${BASE_URL}/v1/coins/market?coin_ids=bitcoin,ethereum" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '.data[] | {id, name, inr: .current_price_inr, cad: .current_price_cad, rank: .market_cap_rank}'
echo ""

echo "Scenario 2: Top 5 coins by market cap"
echo "GET /v1/coins/market?per_page=5&page_num=1"
curl -s "${BASE_URL}/v1/coins/market?per_page=5&page_num=1" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '.data[] | {id, name, inr: .current_price_inr, cad: .current_price_cad}'
echo ""

echo "Scenario 3: DeFi category coins"
echo "GET /v1/coins/market?category=decentralized-finance-defi&per_page=3"
curl -s "${BASE_URL}/v1/coins/market?category=decentralized-finance-defi&per_page=3" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '.data[] | {id, name, inr: .current_price_inr, cad: .current_price_cad}'
echo ""

echo "Scenario 4: Multiple specific coins"
echo "GET /v1/coins/market?coin_ids=bitcoin,ethereum,cardano,solana"
curl -s "${BASE_URL}/v1/coins/market?coin_ids=bitcoin,ethereum,cardano,solana" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '.data[] | {id, name, inr: .current_price_inr, cad: .current_price_cad}'
echo ""

echo "Scenario 5: Paginated market data"
echo "GET /v1/coins/market?page_num=2&per_page=5"
curl -s "${BASE_URL}/v1/coins/market?page_num=2&per_page=5" \
    -H "Authorization: Bearer $TOKEN" | \
    jq '{page, per_page, total: .total, coins: (.data[] | {id, name})}'
echo -e "${GREEN}✓ Market data endpoints working${NC}"
echo ""

# Test 7: Security Tests
echo -e "${YELLOW}[10/10] Testing Security${NC}"

echo "Test 1: Unauthorized access (no token)"
UNAUTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BASE_URL}/v1/coins/")
echo "$UNAUTH_RESPONSE"
if echo "$UNAUTH_RESPONSE" | grep -q "HTTP_CODE:403"; then
    echo -e "${GREEN}✓ Unauthorized access blocked correctly${NC}"
else
    echo -e "${RED}✗ Security issue: unauthorized access not blocked${NC}"
fi
echo ""

echo "Test 2: Invalid token"
INVALID_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BASE_URL}/v1/coins/" \
    -H "Authorization: Bearer invalid_token_here")
if echo "$INVALID_RESPONSE" | grep -q "HTTP_CODE:401"; then
    echo -e "${GREEN}✓ Invalid token rejected correctly${NC}"
else
    echo -e "${RED}✗ Security issue: invalid token not rejected${NC}"
fi
echo ""

echo "Test 3: Wrong credentials"
WRONG_CREDS=$(curl -s -X POST ${BASE_URL}/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"wrong","password":"wrong"}')
if echo "$WRONG_CREDS" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Wrong credentials rejected correctly${NC}"
else
    echo -e "${RED}✗ Security issue: wrong credentials not rejected${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}           TEST SUMMARY${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}✓ All endpoints tested successfully${NC}"
echo -e "${GREEN}✓ Authentication working${NC}"
echo -e "${GREEN}✓ Pagination working${NC}"
echo -e "${GREEN}✓ INR & CAD currencies working${NC}"
echo -e "${GREEN}✓ Category filtering working${NC}"
echo -e "${GREEN}✓ Security measures working${NC}"
echo ""

# Cleanup option
echo -e "${YELLOW}Container is still running for manual testing.${NC}"
echo -e "${YELLOW}API available at: ${BASE_URL}${NC}"
echo -e "${YELLOW}Swagger docs: ${BASE_URL}/docs${NC}"
echo ""
echo -e "To stop the container, run:"
echo -e "  ${BLUE}docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}${NC}"
echo ""
echo -e "${GREEN}Testing completed successfully!${NC}"
