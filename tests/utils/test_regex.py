import re
import unittest

from lox_services.utils.regex import make_get_first


class TestMakeGetFirst(unittest.TestCase):
    def test_get_first_alpha(self) -> None:
        get_first_alpha = make_get_first(r"[a-zA-Z]+")
        result = get_first_alpha("abc123def456")
        self.assertEqual(result, "abc")

    def test_get_first_email(self) -> None:
        get_first_email = make_get_first(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        result = get_first_email(
            "Please contact me at test@example.com for further assistance."
        )
        self.assertEqual(result, "test@example.com")

    def test_get_first_phone(self) -> None:
        get_first_phone = make_get_first(r"\b\d{3}-\d{3}-\d{4}\b")
        result = get_first_phone("Call me at 123-456-7890 for any queries.")
        self.assertEqual(result, "123-456-7890")

    def test_get_first_url(self) -> None:
        get_first_url = make_get_first(r"\b(?:https?://)?(?:www\.)?\w+\.\w+\.\w+\b")
        result = get_first_url(
            "Visit our website at https://www.example.com for more information."
        )
        self.assertEqual(result, "https://www.example.com")

    def test_get_first_match(self) -> None:
        # Test with a valid regex pattern and a string containing a match
        get_first_digit = make_get_first(r"\d+")
        result = get_first_digit("abc 123 def 456")
        self.assertEqual(result, "123")

    def test_get_first_match_with_process_match(self) -> None:
        # Test with a valid regex pattern, a string containing a match, and a process_match function
        def process_match(match):
            return int(match)

        get_first_digit = make_get_first(r"\d+", process_match=process_match)
        result = get_first_digit("abc 123 def 456")
        self.assertEqual(result, 123)

    def test_get_first_no_match(self) -> None:
        # Test with a valid regex pattern and a string with no match
        get_first_digit = make_get_first(r"\d+")
        with self.assertRaises(AttributeError):
            _ = get_first_digit("abc def")

    def test_get_first_no_match_with_process_match(self) -> None:
        # Test with a valid regex pattern, a string with no match, and a process_match function
        def process_match(match):
            return int(match)

        get_first_digit = make_get_first(r"\d+", process_match=process_match)
        with self.assertRaises(AttributeError):
            _ = get_first_digit("abc def")

    def test_get_first_empty_string(self) -> None:
        # Test with an empty string as input
        get_first_digit = make_get_first(r"\d+")
        with self.assertRaises(AttributeError):
            _ = get_first_digit("")

    def test_get_first_empty_string_with_process_match(self) -> None:
        # Test with an empty string as input and a process_match function
        def process_match(match):
            return int(match)

        get_first_digit = make_get_first(r"\d+", process_match=process_match)
        with self.assertRaises(AttributeError):
            _ = get_first_digit("")

    def test_get_first_invalid_regex(self) -> None:
        # Test with an invalid regex pattern
        with self.assertRaises(re.error):
            get_first_digit = make_get_first(r"(\d+")
            _ = get_first_digit("abc 123 def 456")

    def test_get_first_invalid_process_match(self) -> None:
        # Test with an invalid process_match function
        get_first_digit = make_get_first(r"\d+")
        with self.assertRaises(TypeError):
            _ = get_first_digit(
                "abc 123 def 456", process_match="invalid_function"  # NOQA
            )


if __name__ == "__main__":
    unittest.main()
