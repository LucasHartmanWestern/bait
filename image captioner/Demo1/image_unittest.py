import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from ImageCaptioningDemo import caption_image

class TestImageCaptioning(unittest.TestCase):
    @patch("your_module.processor")
    @patch("your_module.model")
    def test_caption_image(self, mock_model, mock_processor):
        # Mocking the processor and model
        mock_processor.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()

        # Sample input image (you may need to adjust the dimensions)
        input_image = np.zeros((256, 256, 3), dtype=np.uint8)

        # Mocking the generate method of the model
        mock_model.generate.return_value = [[5, 2, 3, 0, 0]]  # Mock generated tokens

        # Call the function
        caption = caption_image(input_image)

        # Assert that the mock model's generate method was called with the expected input
        mock_model.generate.assert_called_once()

        # Assert that the caption is a string
        self.assertIsInstance(caption, str)

if __name__ == "__main__":
    unittest.main()