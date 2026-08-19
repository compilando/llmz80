"""Tests for utility helper functions."""

from llmz80.utils.helpers import slugify


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
        """A design's title is Spanish by default, so this is the common case.

        `Metadata.language` defaults to "es" and `studio/samples.py` slugs the
        title straight into a directory name, so accents and enyes have to
        transliterate rather than be dropped -- "ni-o-espa-ol" is what an
        ascii-only filter produced before this.
        """
        assert slugify("Niño español") == "nino-espanol"
