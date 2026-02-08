#!/usr/bin/env pwsh
# ====================================================================
# Pet Medication Diary - MySQL Setup Script (PowerShell)
# Quick setup script for Windows
# ====================================================================

Write-Host "🐾 Pet Medication Diary - MySQL Database Setup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose is not available" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please edit .env file to set your passwords:" -ForegroundColor Yellow
    Write-Host "   notepad .env" -ForegroundColor Cyan
    Write-Host ""
    
    $response = Read-Host "Do you want to edit .env now? (Y/n)"
    if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
        notepad .env
        Write-Host ""
        Write-Host "Press Enter after saving .env file to continue..."
        Read-Host
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Ask user which services to start
Write-Host "Which services do you want to start?" -ForegroundColor Cyan
Write-Host "  1. MySQL only (recommended for production)" -ForegroundColor White
Write-Host "  2. MySQL + phpMyAdmin (recommended for development)" -ForegroundColor White
Write-Host "  3. All services (MySQL + phpMyAdmin + Adminer)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter your choice (1-3) [default: 2]"

if ($choice -eq "" -or $choice -eq "2") {
    $services = "mysql phpmyadmin"
    Write-Host "Starting MySQL + phpMyAdmin..." -ForegroundColor Yellow
} elseif ($choice -eq "1") {
    $services = "mysql"
    Write-Host "Starting MySQL only..." -ForegroundColor Yellow
} elseif ($choice -eq "3") {
    $services = ""
    Write-Host "Starting all services..." -ForegroundColor Yellow
} else {
    Write-Host "Invalid choice. Starting MySQL + phpMyAdmin..." -ForegroundColor Yellow
    $services = "mysql phpmyadmin"
}

Write-Host ""

# Start Docker containers
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
Write-Host ""

if ($services -eq "") {
    docker-compose up -d
} else {
    docker-compose up -d $services.Split(" ")
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Failed to start Docker containers" -ForegroundColor Red
    Write-Host "  Please check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Wait for MySQL to be ready
Write-Host "Waiting for MySQL to be ready..." -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds on first run..." -ForegroundColor Gray

$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    $attempt++
    Start-Sleep -Seconds 2
    
    try {
        $healthCheck = docker exec pet_medic_mysql mysqladmin ping -h localhost 2>&1
        if ($healthCheck -like "*mysqld is alive*") {
            $ready = $true
        }
    } catch {
        # Container not ready yet
    }
    
    Write-Host "." -NoNewline
}

Write-Host ""
Write-Host ""

if ($ready) {
    Write-Host "✓ MySQL is ready!" -ForegroundColor Green
} else {
    Write-Host "⚠️  MySQL might not be ready yet. Please check logs:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs -f mysql" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Show connection information
Write-Host "📊 Database Information:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Database Name: " -NoNewline -ForegroundColor Gray
Write-Host "pet_medic_db" -ForegroundColor White
Write-Host "  MySQL Port:    " -NoNewline -ForegroundColor Gray
Write-Host "localhost:3306" -ForegroundColor White
Write-Host ""

# Load .env to get actual values
Get-Content .env | ForEach-Object {
    if ($_ -match '^MYSQL_USER=(.+)$') {
        $mysqlUser = $matches[1]
    }
    if ($_ -match '^MYSQL_PASSWORD=(.+)$') {
        $mysqlPassword = $matches[1]
    }
    if ($_ -match '^PHPMYADMIN_PORT=(.+)$') {
        $phpMyAdminPort = $matches[1]
    }
    if ($_ -match '^ADMINER_PORT=(.+)$') {
        $adminerPort = $matches[1]
    }
}

Write-Host "  Username:      " -NoNewline -ForegroundColor Gray
Write-Host "$mysqlUser" -ForegroundColor White
Write-Host "  Password:      " -NoNewline -ForegroundColor Gray
Write-Host "$mysqlPassword" -ForegroundColor White

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Show web interface URLs
if ($services -like "*phpmyadmin*" -or $services -eq "") {
    Write-Host "🌐 Web Interfaces:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  phpMyAdmin:    " -NoNewline -ForegroundColor Gray
    Write-Host "http://localhost:$phpMyAdminPort" -ForegroundColor White
    
    if ($services -like "*adminer*" -or $services -eq "") {
        Write-Host "  Adminer:       " -NoNewline -ForegroundColor Gray
        Write-Host "http://localhost:$adminerPort" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host ""
}

# Show useful commands
Write-Host "📝 Useful Commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  View logs:           " -NoNewline -ForegroundColor Gray
Write-Host "docker-compose logs -f mysql" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Stop containers:     " -NoNewline -ForegroundColor Gray
Write-Host "docker-compose down" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Restart MySQL:       " -NoNewline -ForegroundColor Gray
Write-Host "docker-compose restart mysql" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Access MySQL shell:  " -NoNewline -ForegroundColor Gray
Write-Host "docker exec -it pet_medic_mysql mysql -u $mysqlUser -p" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Backup database:     " -NoNewline -ForegroundColor Gray
Write-Host "docker exec pet_medic_mysql mysqldump -u $mysqlUser -p pet_medic_db > backup.sql" -ForegroundColor Yellow
Write-Host ""

Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Setup complete! Your MySQL database is ready to use." -ForegroundColor Green
Write-Host ""

# Ask if user wants to open phpMyAdmin
if ($services -like "*phpmyadmin*" -or $services -eq "") {
    $openBrowser = Read-Host "Do you want to open phpMyAdmin in browser? (Y/n)"
    if ($openBrowser -eq "" -or $openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "http://localhost:$phpMyAdminPort"
    }
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
