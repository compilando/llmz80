"""Tests for utility helper functions."""

import pytest
from llmz80.utils.helpers import clean_api_response, slugify


class TestCleanApiResponse:
    """Tests for clean_api_response function."""

    def test_remove_markdown_fences(self):
        """Test removal of markdown code fences."""
        input_text = "```c\n#include <stdio.h>\nvoid main() {}\n```"
        expected = "#include <stdio.h>\nvoid main() {}"
        assert clean_api_response(input_text).strip() == expected

    def test_remove_explanatory_text(self):
        """Test removal of explanatory text before code."""
        input_text = "Here's the code:\n\n#include <stdio.h>\nvoid main() {}"
        result = clean_api_response(input_text)
        assert "#include <stdio.h>" in result

    def test_preserve_code_only(self):
        """Test that only code is preserved."""
        input_text = "#include <stdio.h>\nvoid main() {}"
        assert clean_api_response(input_text).strip() == input_text


class TestSlugify:
    """Tests for slugify function."""

    def test_basic_slugify(self):
        """Test basic string to slug conversion."""
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        """Test removal of special characters."""
        assert slugify("Hello, World!") == "hello-world"

    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        assert slugify("Hello   World") == "hello-world"

    def test_max_length(self):
        """Test slug length limiting."""
        long_text = "a" * 100
        slug = slugify(long_text, max_length=40)
        assert len(slug) <= 40

    def test_spanish_characters(self):
        """Test handling of Spanish characters."""
        assert slugify("Niño español") == "nino-espanol"
