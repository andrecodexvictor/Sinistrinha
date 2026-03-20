"""
seed_levels.py — Management command to populate LevelConfig with default tiers.

Usage: python manage.py seed_levels
"""

from django.core.management.base import BaseCommand
from apps.game.models import LevelConfig


# IT-themed level configuration: each level has progressively harder XP
# requirements and more generous rewards.
LEVEL_DATA = [
    {
        "level": 1,
        "xp_required": 0,
        "bonus_coins": 0,
        "free_spins": 0,
        "prize_name": "Newbie (Estagiário)",
        "prize_icon": "🖱️",
        "house_edge_modifier": 1.0,
    },
    {
        "level": 2,
        "xp_required": 500,
        "bonus_coins": 50,
        "free_spins": 3,
        "prize_name": "Pendrive 8GB",
        "prize_icon": "🔌",
        "house_edge_modifier": 1.0,
    },
    {
        "level": 3,
        "xp_required": 1500,
        "bonus_coins": 150,
        "free_spins": 5,
        "prize_name": "Teclado Mecânico",
        "prize_icon": "⌨️",
        "house_edge_modifier": 1.0,
    },
    {
        "level": 4,
        "xp_required": 3500,
        "bonus_coins": 350,
        "free_spins": 7,
        "prize_name": "Mouse Gamer",
        "prize_icon": "🖱️",
        "house_edge_modifier": 1.02,
    },
    {
        "level": 5,
        "xp_required": 7000,
        "bonus_coins": 700,
        "free_spins": 10,
        "prize_name": "RAM DDR5 16GB",
        "prize_icon": "💾",
        "house_edge_modifier": 1.02,
    },
    {
        "level": 6,
        "xp_required": 12000,
        "bonus_coins": 1200,
        "free_spins": 12,
        "prize_name": "SSD NVMe 1TB",
        "prize_icon": "💿",
        "house_edge_modifier": 1.03,
    },
    {
        "level": 7,
        "xp_required": 20000,
        "bonus_coins": 2000,
        "free_spins": 15,
        "prize_name": "Monitor 144Hz",
        "prize_icon": "🖥️",
        "house_edge_modifier": 1.03,
    },
    {
        "level": 8,
        "xp_required": 35000,
        "bonus_coins": 3500,
        "free_spins": 20,
        "prize_name": "CPU Ryzen 7",
        "prize_icon": "🔲",
        "house_edge_modifier": 1.05,
    },
    {
        "level": 9,
        "xp_required": 60000,
        "bonus_coins": 6000,
        "free_spins": 25,
        "prize_name": "GPU RTX 4070",
        "prize_icon": "🎮",
        "house_edge_modifier": 1.05,
    },
    {
        "level": 10,
        "xp_required": 100000,
        "bonus_coins": 10000,
        "free_spins": 50,
        "prize_name": "Gorila Dourado (Setup Completo)",
        "prize_icon": "🦍",
        "house_edge_modifier": 1.08,
    },
]


class Command(BaseCommand):
    help = "Seed the LevelConfig table with default IT-themed level tiers."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for data in LEVEL_DATA:
            obj, created = LevelConfig.objects.update_or_create(
                level=data["level"],
                defaults={
                    "xp_required": data["xp_required"],
                    "bonus_coins": data["bonus_coins"],
                    "free_spins": data["free_spins"],
                    "prize_name": data["prize_name"],
                    "prize_icon": data["prize_icon"],
                    "house_edge_modifier": data["house_edge_modifier"],
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created_count} levels created, {updated_count} updated."
            )
        )
