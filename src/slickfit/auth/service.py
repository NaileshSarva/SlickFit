"""Authentication and user management service."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db.models import AthleteProfile, Availability, NutritionProfile, User
from .security import create_access_token, hash_password, verify_password


class AuthService:
    """Service handling user credentials, registration, and demo isolation."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.get(User, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.strip().lower())
        return db.execute(stmt).scalar_one_or_none()

    @classmethod
    def register_user(
        cls,
        db: Session,
        email: str,
        password: str,
        full_name: str = "",
        timezone: str = "Asia/Kolkata",
        locale: str = "en-IN",
        units: str = "metric",
        is_demo: bool = False,
    ) -> User:
        clean_email = email.strip().lower()
        if not clean_email or "@" not in clean_email:
            raise ValueError("A valid email address is required.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        existing = cls.get_user_by_email(db, clean_email)
        if existing:
            raise ValueError("An account with this email address already exists.")

        user = User(
            email=clean_email,
            hashed_password=hash_password(password),
            full_name=full_name.strip(),
            timezone=timezone or settings.default_timezone,
            locale=locale or settings.default_locale,
            units=units or settings.default_units,
            is_demo=is_demo,
        )
        db.add(user)
        db.flush()  # populate user.id

        # Attach default profile, availability, and nutrition profile
        # For real accounts, do not invent/fabricate demographic profile data
        if is_demo:
            profile = AthleteProfile(user_id=user.id, age_band="30-39", region="South Asia - Karnataka")
        else:
            profile = AthleteProfile(user_id=user.id, age_band="", region="")

        availability = Availability(user_id=user.id)
        nutrition = NutritionProfile(user_id=user.id)

        db.add_all([profile, availability, nutrition])
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def authenticate_user(
        cls,
        db: Session,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        user = cls.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("Account is disabled.")

        token = create_access_token(subject=user.id, claims={"email": user.email, "is_demo": user.is_demo})
        return user, token

    @classmethod
    def get_or_create_demo_user(
        cls,
        db: Session,
        demo_key: str = "demo1",
    ) -> tuple[User, str]:
        """Get or initialize isolated local demo users (no external cloud required)."""
        demo_specs = {
            "demo1": {
                "email": "demo.runner@slickfit.local",
                "name": "Arjun Sharma (10K Runner)",
                "password": "DemoRunner2026!Secure",
                "timezone": "Asia/Kolkata",
            },
            "demo2": {
                "email": "runner2.beginner@slickfit.local",
                "name": "Priya Nair (Baseline Builder)",
                "password": "DemoPriya2026!Secure",
                "timezone": "Asia/Kolkata",
            },
        }

        spec = demo_specs.get(demo_key, demo_specs["demo1"])
        user = cls.get_user_by_email(db, spec["email"])
        if not user:
            user = cls.register_user(
                db=db,
                email=spec["email"],
                password=spec["password"],
                full_name=spec["name"],
                timezone=spec["timezone"],
                is_demo=True,
            )

        token = create_access_token(subject=user.id, claims={"email": user.email, "is_demo": True})
        return user, token

    @classmethod
    def delete_user_account(cls, db: Session, user_id: str) -> None:
        """Cascading deletion of all athlete records for privacy/account removal."""
        user = cls.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
