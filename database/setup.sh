#!/bin/bash
# ====================================================================
# Pet Medication Diary - MySQL Setup Script (Bash)
# Quick setup script for Linux/Mac
# ====================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}🐾 Pet Medication Diary - MySQL Database Setup${NC}"
echo "============================================================"
echo ""

# Check if Docker is installed
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed or not in PATH${NC}"
    echo -e "${YELLOW}  Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓ Docker found: $DOCKER_VERSION${NC}"

# Check if docker-compose is available
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not available${NC}"
    exit 1
fi
COMPOSE_VERSION=$(docker-compose --version)
echo -e "${GREEN}✓ Docker Compose found: $COMPOSE_VERSION${NC}"

echo ""
echo "============================================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Please edit .env file to set your passwords:${NC}"
    echo -e "${CYAN}   nano .env${NC}"
    echo ""
    
    read -p "Do you want to edit .env now? (Y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        ${EDITOR:-nano} .env
        echo ""
        read -p "Press Enter after saving .env file to continue..."
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo "============================================================"
echo ""

# Ask user which services to start
echo -e "${CYAN}Which services do you want to start?${NC}"
echo "  1. MySQL only (recommended for production)"
echo "  2. MySQL + phpMyAdmin (recommended for development)"
echo "  3. All services (MySQL + phpMyAdmin + Adminer)"
echo ""
read -p "Enter your choice (1-3) [default: 2]: " choice

case $choice in
    1)
        SERVICES="mysql"
        echo -e "${YELLOW}Starting MySQL only...${NC}"
        ;;
    3)
        SERVICES=""
        echo -e "${YELLOW}Starting all services...${NC}"
        ;;
    *)
        SERVICES="mysql phpmyadmin"
        echo -e "${YELLOW}Starting MySQL + phpMyAdmin...${NC}"
        ;;
esac

echo ""

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
echo ""

if [ -z "$SERVICES" ]; then
    docker-compose up -d
else
    docker-compose up -d $SERVICES
fi

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Failed to start Docker containers${NC}"
    echo -e "${YELLOW}  Please check the error messages above${NC}"
    exit 1
fi

echo ""
echo "============================================================"
echo ""

# Wait for MySQL to be ready
echo -e "${YELLOW}Waiting for MySQL to be ready...${NC}"
echo -e "${GRAY}This may take 30-60 seconds on first run...${NC}"

MAX_ATTEMPTS=30
ATTEMPT=0
READY=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ "$READY" = false ]; do
    ATTEMPT=$((ATTEMPT+1))
    sleep 2
    
    if docker exec pet_medic_mysql mysqladmin ping -h localhost 2>&1 | grep -q "mysqld is alive"; then
        READY=true
    fi
    
    echo -n "."
done

echo ""
echo ""

if [ "$READY" = true ]; then
    echo -e "${GREEN}✓ MySQL is ready!${NC}"
else
    echo -e "${YELLOW}⚠️  MySQL might not be ready yet. Please check logs:${NC}"
    echo -e "${CYAN}   docker-compose logs -f mysql${NC}"
fi

echo ""
echo "============================================================"
echo ""

# Show connection information
echo -e "${CYAN}📊 Database Information:${NC}"
echo ""

# Load .env to get actual values
source .env

echo -e "${GRAY}  Database Name: ${NC}${MYSQL_DATABASE}"
echo -e "${GRAY}  MySQL Port:    ${NC}localhost:3306"
echo ""
echo -e "${GRAY}  Username:      ${NC}${MYSQL_USER}"
echo -e "${GRAY}  Password:      ${NC}${MYSQL_PASSWORD}"

echo ""
echo "============================================================"
echo ""

# Show web interface URLs
if [[ $SERVICES == *"phpmyadmin"* ]] || [ -z "$SERVICES" ]; then
    echo -e "${CYAN}🌐 Web Interfaces:${NC}"
    echo ""
    echo -e "${GRAY}  phpMyAdmin:    ${NC}http://localhost:${PHPMYADMIN_PORT:-8080}"
    
    if [[ $SERVICES == *"adminer"* ]] || [ -z "$SERVICES" ]; then
        echo -e "${GRAY}  Adminer:       ${NC}http://localhost:${ADMINER_PORT:-8081}"
    fi
    
    echo ""
    echo "============================================================"
    echo ""
fi

# Show useful commands
echo -e "${CYAN}📝 Useful Commands:${NC}"
echo ""
echo -e "${GRAY}  View logs:           ${NC}${YELLOW}docker-compose logs -f mysql${NC}"
echo ""
echo -e "${GRAY}  Stop containers:     ${NC}${YELLOW}docker-compose down${NC}"
echo ""
echo -e "${GRAY}  Restart MySQL:       ${NC}${YELLOW}docker-compose restart mysql${NC}"
echo ""
echo -e "${GRAY}  Access MySQL shell:  ${NC}${YELLOW}docker exec -it pet_medic_mysql mysql -u ${MYSQL_USER} -p${NC}"
echo ""
echo -e "${GRAY}  Backup database:     ${NC}${YELLOW}docker exec pet_medic_mysql mysqldump -u ${MYSQL_USER} -p ${MYSQL_DATABASE} > backup.sql${NC}"
echo ""

echo "============================================================"
echo ""
echo -e "${GREEN}✅ Setup complete! Your MySQL database is ready to use.${NC}"
echo ""

# Ask if user wants to open phpMyAdmin
if [[ $SERVICES == *"phpmyadmin"* ]] || [ -z "$SERVICES" ]; then
    read -p "Do you want to open phpMyAdmin in browser? (Y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:${PHPMYADMIN_PORT:-8080}"
        elif command -v open &> /dev/null; then
            open "http://localhost:${PHPMYADMIN_PORT:-8080}"
        else
            echo -e "${YELLOW}Please open http://localhost:${PHPMYADMIN_PORT:-8080} in your browser${NC}"
        fi
    fi
fi

echo ""
