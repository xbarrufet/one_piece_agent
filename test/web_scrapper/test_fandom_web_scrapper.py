
from unittest import TestCase
from src.web_scrapper.fandom_web_scrapper import filter_string_references

class Test_web_scrapper(TestCase):

    def test_sample(self):
        """
        Sample test to ensure the test framework is working.
        """
        assert True, "This is a sample test to check if the test framework is working."

    def test_filter_string_references(self):
        """
        from src.web_scrapper.fandom_web_scrapper import filter_string_references
        """

        # Test cases
        test_cases = [
            ("This is a test [1] string [2] with references.", "This is a test string with references."),
            ("No references here.", "No references here."),
            ("[3] Leading reference.", "Leading reference."),
            ("Trailing reference [4].", "Trailing reference."),
            ("[5] Multiple [6] references [7].", "Multiple references."),
            ("[8][9][10]", ""),
            ("", "")
        ]

        for input_text, expected_output in test_cases:
            res = filter_string_references(input_text)
            assert res == expected_output, f"Failed for input: {input_text} res: {res}, expected: {expected_output}"