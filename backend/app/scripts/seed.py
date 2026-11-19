"""Seed default hosting categories."""

from app.database import SessionLocal
from app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Minecraft Hosting", "slug": "minecraft", "icon": "⛏️", "sort_order": 1},
    {"name": "Modded Minecraft Hosting", "slug": "modded-minecraft", "icon": "🧩", "sort_order": 2},
    {"name": "Discord Bot Hosting", "slug": "discord-bot", "icon": "🤖", "sort_order": 3},
    {"name": "Python Bot Hosting", "slug": "python-bot", "icon": "🐍", "sort_order": 4},
    {"name": "KVM VPS Hosting", "slug": "kvm-vps", "icon": "💻", "sort_order": 5},
    {"name": "Other Services", "slug": "other", "icon": "☁️", "sort_order": 6},
]


def main() -> None:
    db = SessionLocal()
    try:
        for c in DEFAULT_CATEGORIES:
            if not db.query(Category).filter_by(slug=c["slug"]).first():
                db.add(Category(**c))
        db.commit()
        print("Seeded categories")
    finally:
        db.close()


if __name__ == "__main__":
    main()
