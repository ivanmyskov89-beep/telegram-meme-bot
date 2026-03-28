import pytest
from PIL import Image
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import load_captions, get_random_caption, add_text_to_image

def test_load_captions():
    captions = load_captions()
    assert isinstance(captions, list)
    assert len(captions) > 0

def test_add_text_to_image():
    img = Image.new('RGB', (500, 500), color='white')
    result = add_text_to_image(img, "Test")
    assert result.size == (500, 500)
