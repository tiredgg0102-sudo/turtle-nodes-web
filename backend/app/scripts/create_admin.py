"""Create the first administrator user (CLI helper)."""

import argparse
import sys

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--role", default="admin", choices=["admin", "staff", "customer"])
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if db.query(User).filter_by(email=args.email).first():
            print(f"User {args.email} already exists")
            return
        user = User(
            email=args.email,
            username=args.username,
            password_hash=hash_password(args.password),
            role=args.role,
            status="active",
        )
        db.add(user)
        db.commit()
        print(f"Created {args.role} user: {args.email} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
