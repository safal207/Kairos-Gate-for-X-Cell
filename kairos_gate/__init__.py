"""Kairos Gate reference validation package."""

from .validator import ValidationError, recommend_decision, validate_record

__all__ = ["ValidationError", "recommend_decision", "validate_record"]
