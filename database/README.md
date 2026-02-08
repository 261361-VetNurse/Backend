# 🐾 Pet Medication Diary - MySQL Database Setup

Docker Compose setup for MySQL database (fresh installation, no MongoDB migration)

---

## 📁 Files Overview

```
database/
├── docker-compose.yml              # Docker services configuration
├── .env.example                    # Environment variables template
├── mysql.cnf                       # Custom MySQL configuration
├── setup_db_mysql_improved.sql     # Database schema
└── README.md                       # This file
```

---

## 🚀 Quick Start

### 1. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your preferred values
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### 2. Start MySQL Container

```bash
# Start all services (MySQL + phpMyAdmin + Adminer)
docker-compose up -d

# Or start only MySQL
docker-compose up -d mysql
```

### 3. Verify Installation

```bash
# Check container status
docker-compose ps

# Check MySQL logs
docker-compose logs -f mysql

# Wait for "ready for connections" message
```

### 4. Access Database

**MySQL Client:**
```bash
# Using Docker exec
docker exec -it pet_medic_mysql mysql -u pet_medic_user -p
# Password: secure_password_2026 (from .env)

# From host machine
mysql -h localhost -P 3306 -u pet_medic_user -p pet_medic_db
```

**phpMyAdmin:**
- URL: http://localhost:8080
- Username: `pet_medic_user`
- Password: (from .env file)

**Adminer:**
- URL: http://localhost:8081
- System: MySQL
- Server: mysql
- Username: `pet_medic_user`
- Password: (from .env file)

---

## 🗄️ Database Schema

The database will be automatically created with the following tables:

1. **users** - User accounts with LINE authentication
2. **jwt_tokens** - JWT authentication tokens (1:1 with users)
3. **pets** - Pet profiles (1:N with users)
4. **medicines** - Medication schedules (1:N with pets)
5. **medicines_notification** - Medicine reminders (1:N with medicines)
6. **appointments** - Veterinary appointments (1:N with pets)
7. **appointments_notification** - Appointment reminders (1:N with appointments)
8. **pets_records** - Health records (1:N with pets)

**Sample data is automatically inserted for testing.**

---

## 🔧 Configuration Options

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_ROOT_PASSWORD` | `root_password_change_me` | Root password |
| `MYSQL_DATABASE` | `pet_medic_db` | Database name |
| `MYSQL_USER` | `pet_medic_user` | Application user |
| `MYSQL_PASSWORD` | `pet_medic_password` | Application password |
| `MYSQL_PORT` | `3306` | MySQL port on host |
| `PHPMYADMIN_PORT` | `8080` | phpMyAdmin port |
| `ADMINER_PORT` | `8081` | Adminer port |

### MySQL Custom Settings (mysql.cnf)

- Character Set: `utf8mb4`
- Timezone: `Asia/Bangkok`
- Max Connections: `200`
- InnoDB Buffer Pool: `1G`
- Slow Query Log: Enabled (2s threshold)

---

## 📊 Useful Commands

### Docker Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (DELETE ALL DATA!)
docker-compose down -v

# Restart MySQL
docker-compose restart mysql

# View logs
docker-compose logs -f mysql

# Check resource usage
docker stats pet_medic_mysql
```

### Database Operations

```bash
# Backup database
docker exec pet_medic_mysql mysqldump \
  -u pet_medic_user -p'secure_password_2026' \
  pet_medic_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker exec -i pet_medic_mysql mysql \
  -u pet_medic_user -p'secure_password_2026' \
  pet_medic_db < backup.sql

# Access MySQL shell
docker exec -it pet_medic_mysql mysql \
  -u pet_medic_user -p'secure_password_2026' \
  pet_medic_db
```

### Useful SQL Queries

```sql
-- Check database size
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'pet_medic_db'
GROUP BY table_schema;

-- Show all tables
SHOW TABLES;

-- Count records in each table
SELECT 'users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'pets', COUNT(*) FROM pets
UNION ALL
SELECT 'medicines', COUNT(*) FROM medicines
UNION ALL
SELECT 'appointments', COUNT(*) FROM appointments;

-- Check active medicines
SELECT * FROM v_active_medicines_with_next_notification;

-- Check user dashboard
SELECT * FROM v_user_dashboard;
```

---

## 🔐 Security Recommendations

### For Development

- ✅ Use `.env` for credentials (already configured)
- ✅ Change default passwords in `.env`
- ✅ Don't commit `.env` to git (already in .gitignore)

### For Production

- ⚠️ Use strong passwords (minimum 16 characters)
- ⚠️ Disable phpMyAdmin and Adminer
- ⚠️ Use SSL/TLS connections
- ⚠️ Enable firewall rules (allow only application server)
- ⚠️ Regular backups (automated)
- ⚠️ Use secrets management (e.g., Docker Secrets, Vault)

**Production docker-compose:**
```yaml
# Remove or comment out these services in production
# phpmyadmin:
#   ...
# adminer:
#   ...
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs mysql

# Check if port is in use
netstat -an | findstr :3306  # Windows
lsof -i :3306                # Linux/Mac

# Remove old containers and volumes
docker-compose down -v
docker-compose up -d
```

### Connection refused

```bash
# Wait for MySQL to be ready
docker-compose logs -f mysql
# Look for: "ready for connections"

# Test connection
docker exec pet_medic_mysql mysqladmin ping -h localhost -u root -p
```

### Performance issues

```bash
# Check resource usage
docker stats pet_medic_mysql

# Increase buffer pool size in mysql.cnf:
# innodb_buffer_pool_size = 2G

# Restart after changes
docker-compose restart mysql
```

### Forgot password

```bash
# Reset root password
docker-compose down
docker-compose up -d mysql --env MYSQL_ROOT_PASSWORD=new_password

# Or use skip-grant-tables (dangerous!)
docker exec -it pet_medic_mysql mysql --skip-grant-tables
# Then reset password manually
```

---

## 📦 Data Persistence

Data is stored in named Docker volumes:

- **pet_medic_mysql_data** - Database files
- **pet_medic_mysql_logs** - MySQL logs

### Backup volumes

```bash
# Backup data volume
docker run --rm \
  -v pet_medic_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql_data_backup.tar.gz -C /data .

# Restore data volume
docker run --rm \
  -v pet_medic_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mysql_data_backup.tar.gz -C /data
```

---

## 🔄 Migration from MongoDB (Future)

If you need to migrate data from MongoDB later:

1. Export data from MongoDB
2. Transform to SQL format
3. Load into MySQL

**Script example** (to be created):
```bash
# Export from MongoDB
python migrate_mongo_to_mysql.py --export

# Transform data
python migrate_mongo_to_mysql.py --transform

# Import to MySQL
python migrate_mongo_to_mysql.py --import
```

---

## 📚 API Connection

### Python (FastAPI/SQLAlchemy)

```python
# requirements.txt
aiomysql==0.2.0
sqlalchemy==2.0.25
pymysql==1.1.0

# config.py
DATABASE_URL = "mysql+aiomysql://pet_medic_user:secure_password_2026@localhost:3306/pet_medic_db?charset=utf8mb4"

# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Node.js (Express)

```javascript
// npm install mysql2
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  port: 3306,
  user: 'pet_medic_user',
  password: 'secure_password_2026',
  database: 'pet_medic_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});
```

---

## 🎯 Next Steps

1. ✅ Start Docker containers
2. ✅ Verify database creation
3. ✅ Test sample data
4. ⬜ Update FastAPI backend to use MySQL
5. ⬜ Implement notification scheduler
6. ⬜ Test CRUD operations
7. ⬜ Deploy to production

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f mysql`
2. Review MySQL error log: `docker exec pet_medic_mysql tail -f /var/log/mysql/error.log`
3. Check database schema: `setup_db_mysql_improved.sql`

---

**Created:** February 8, 2026  
**Database Version:** MySQL 8.0  
**Migration Status:** Fresh installation (no MongoDB data)
