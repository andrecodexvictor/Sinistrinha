#!/bin/bash
# =============================================================================
# Sinistrinha — Complete Setup Script
# =============================================================================
# This script builds all containers, runs migrations, seeds data, and creates
# test accounts. Run from the project root.
# =============================================================================

set -e

echo "🦍 ======================================"
echo "   SINISTRINHA — Setup Script"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- 1. Check prerequisites ---
echo -e "\n${YELLOW}[1/7] Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo "Docker is required. Install it first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is required."; exit 1; }

# --- 2. Create .env if not exists ---
echo -e "\n${YELLOW}[2/7] Checking .env file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — please update with your credentials!"
fi

# --- 3. Build containers ---
echo -e "\n${YELLOW}[3/7] Building containers...${NC}"
docker-compose build

# --- 4. Start services ---
echo -e "\n${YELLOW}[4/7] Starting services...${NC}"
docker-compose up -d redis probability_engine
sleep 3
docker-compose up -d web celery celery-beat nginx

# Wait for web to be ready
echo "Waiting for Django to start..."
sleep 5

# --- 5. Run migrations ---
echo -e "\n${YELLOW}[5/7] Running migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --noinput

# --- 6. Seed data ---
echo -e "\n${YELLOW}[6/7] Seeding data...${NC}"

# Create superuser
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
from apps.users.models import UserProfile
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@sinistrinha.local', 'admin123')
    UserProfile.objects.get_or_create(user=u, defaults={'balance': 10000, 'level': 1})
    print('✅ Superuser created: admin / admin123')
else:
    print('ℹ️  Superuser already exists')
"

# Create test user
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
from apps.users.models import UserProfile
if not User.objects.filter(username='player1').exists():
    u = User.objects.create_user('player1', 'player1@test.com', 'test1234')
    UserProfile.objects.get_or_create(user=u, defaults={'balance': 100, 'level': 1})
    print('✅ Test user created: player1 / test1234 (balance: R\$100)')
else:
    print('ℹ️  Test user already exists')
"

# Initialize Jackpot Pool
docker-compose exec -T web python manage.py shell -c "
from apps.game.models import JackpotPool
pool, created = JackpotPool.objects.get_or_create(pk=1, defaults={'current_amount': 500, 'min_amount': 500})
if created:
    print('✅ Jackpot pool initialized: R\$500.00')
else:
    print('ℹ️  Jackpot pool exists: R\$' + str(pool.current_amount))
"

# Seed Level Configs
docker-compose exec -T web python manage.py shell -c "
from apps.game.models import LevelConfig
from apps.game.level_system import LEVEL_CONFIG

created_count = 0
for cfg in LEVEL_CONFIG:
    _, created = LevelConfig.objects.get_or_create(
        level=cfg['level'],
        defaults={
            'xp_required': cfg['xp'],
            'bonus_coins': cfg['bonus'],
            'free_spins': cfg['free_spins'],
            'prize_name': cfg['prize'],
            'prize_icon': cfg['icon'],
            'prize_rarity': cfg['rarity'],
        }
    )
    if created:
        created_count += 1

print(f'✅ Level configs: {created_count} created, {len(LEVEL_CONFIG) - created_count} already existed')
"

# --- 7. Show status ---
echo -e "\n${YELLOW}[7/7] Setup complete!${NC}"
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  🦍 SINISTRINHA is ready!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "📍 Access URLs:"
echo "   Django API:      http://localhost:8000/api/docs/"
echo "   Admin Panel:     http://localhost:8000/admin/"
echo "   Casino Dashboard:http://localhost:8000/admin/casino/dashboard/"
echo "   Probability API: http://localhost:8001/docs"
echo "   Nginx (prod):    http://localhost/"
echo ""
echo "🔐 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🧪 Test User:"
echo "   Username: player1"
echo "   Password: test1234"
echo "   Balance:  R\$100.00"
echo ""
echo "📝 Quick Test (get JWT token):"
echo "   curl -X POST http://localhost:8000/api/auth/login/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"player1\",\"password\":\"test1234\"}'"
echo ""
