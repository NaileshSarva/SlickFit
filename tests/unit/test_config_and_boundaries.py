"""Unit tests for configuration boundaries, environment safety guards, and production secret requirements."""

import os
import pytest

from src.slickfit.config import DEV_DEFAULT_SECRET, Settings


def test_development_mode_allows_default_secret_and_demo_mode():
    cfg = Settings(
        environment="development",
        raw_secret_key=None,
        raw_demo_mode=None,
    )
    assert cfg.is_production is False
    assert cfg.secret_key == DEV_DEFAULT_SECRET
    assert cfg.demo_mode_enabled is True


def test_production_mode_fails_startup_when_secret_key_missing():
    cfg = Settings(
        environment="production",
        raw_secret_key=None,
        raw_demo_mode=None,
    )
    assert cfg.is_production is True
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        _ = cfg.secret_key


def test_production_mode_fails_startup_when_default_dev_secret_used():
    cfg = Settings(
        environment="production",
        raw_secret_key=DEV_DEFAULT_SECRET,
        raw_demo_mode=None,
    )
    assert cfg.is_production is True
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        _ = cfg.secret_key


def test_production_mode_accepts_secure_custom_secret_and_disables_demo():
    custom_secret = "a" * 32
    cfg = Settings(
        environment="production",
        raw_secret_key=custom_secret,
        raw_demo_mode=None,
    )
    assert cfg.is_production is True
    assert cfg.secret_key == custom_secret
    assert cfg.demo_mode_enabled is False


def test_demo_mode_override_behavior():
    cfg_forced = Settings(
        environment="production",
        raw_secret_key="b" * 32,
        raw_demo_mode="true",
    )
    assert cfg_forced.demo_mode_enabled is True

    cfg_disabled_in_dev = Settings(
        environment="development",
        raw_secret_key=None,
        raw_demo_mode="false",
    )
    assert cfg_disabled_in_dev.demo_mode_enabled is False
