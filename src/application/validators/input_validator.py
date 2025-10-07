"""Input validation utilities."""

import re

import bleach


class InputValidator:
    """Validator for input data."""

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Venezuelan phone number format (11 digits starting with 04).

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^04\d{9}$"
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_national_id(national_id: str) -> bool:
        """Validate Venezuelan national ID format (V or E followed by 4-8 digits).

        Args:
            national_id: National ID to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[VE]\d{4,8}$"
        return bool(re.match(pattern, national_id.upper()))

    @staticmethod
    def validate_reference(reference: str) -> bool:
        """Validate Banesco reference format (9 digits).

        Args:
            reference: Reference number to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^\d{9}$"
        return bool(re.match(pattern, reference))

    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """Sanitize text input to prevent XSS attacks.

        Args:
            text: Text to sanitize
            max_length: Maximum length allowed

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove HTML tags and limit length
        cleaned = bleach.clean(text, strip=True)
        return cleaned[:max_length]

    @staticmethod
    def validate_transaction_id(transaction_id: str) -> bool:
        """Validate transaction ID format (alphanumeric with - and _).

        Args:
            transaction_id: Transaction ID to validate

        Returns:
            True if valid, False otherwise
        """
        # Allow alphanumeric and common separators
        pattern = r"^[A-Za-z0-9\-_]{1,100}$"
        return bool(re.match(pattern, transaction_id))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
