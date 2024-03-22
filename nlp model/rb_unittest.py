import unittest
from unittest.mock import patch
from rbmodel import get_response

class TestChatbot(unittest.TestCase):
    # Test case for empty input
    def test_empty_input(self):
        response = get_response("")
        self.assertEqual(response, "Please type something so we can chat :(")

    # Test case for matching predefined response
    def test_matching_response(self):
        input_string = "Tell me a joke"
        expected_response = "Why don't scientists trust atoms? Because they make up everything!"
        response = get_response(input_string)
        self.assertEqual(response, expected_response)

if __name__ == "__main__":
    unittest.main()
