"""Pytest configuration and fixtures for LLMZ80 tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


class FakeMessageStream:
    """What `client.messages.stream` returns, for tests that fake a model.

    `llmz80.studio.llm.structured` streams every request -- the SDK refuses a
    non-streaming call whose `max_tokens` could outlast ten minutes -- so a
    fake client answers with this rather than with a message directly. It is
    the whole contract `structured` uses: a context manager whose
    `get_final_message` hands back the response (or raises what it was given,
    the way the SDK's own post-parse validation does).
    """

    def __init__(self, outcome) -> None:
        self.outcome = outcome

    def __enter__(self) -> "FakeMessageStream":
        return self

    def __exit__(self, *_) -> bool:
        return False

    def get_final_message(self):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def fake_message(parsed, **extra):
    """A stand-in response carrying `parsed` as its `parsed_output`."""
    return type("Response", (), {"parsed_output": parsed, **extra})()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    
    # Mock chat completions
    client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content='#include <stdio.h>\n\nvoid main(void) {\n    // Test code\n}'
                )
            )
        ]
    )
    
    # Mock embeddings
    client.embeddings.create.return_value = Mock(
        data=[
            Mock(embedding=[0.1] * 1536)
        ]
    )
    
    return client


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    client = Mock()
    
    # Mock search results
    client.search.return_value = [
        Mock(
            payload={
                'file_path': 'examples/test.c',
                'description': 'Test example',
                'source_code': '// Test code'
            },
            score=0.95
        )
    ]
    
    return client


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary configuration directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create basic config.yml
    config_file = config_dir / "config.yml"
    config_file.write_text("""
openai:
  model: gpt-4o
  temperature: 0.3
  max_tokens: 8096
  embedding_model: text-embedding-3-small

examples:
  max_examples: 15
  truncate_size: 50000

embeddings:
  cache_dir: "local/embeddings"
  max_chunk_size: 15000
""")
    
    return config_dir


@pytest.fixture
def sample_spectrum_code():
    """Sample ZX Spectrum C code for testing."""
    return """// Description: Test program that changes border color
// Descripcion: Programa de prueba que cambia el color del borde

#include <spectrum.h>

void main(void) {
    zx_border(INK_RED);
    for(;;);
}
"""


@pytest.fixture
def sample_amstrad_code():
    """Sample Amstrad CPC C code for testing."""
    return """// Description: Test program that clears screen
// Descripcion: Programa de prueba que limpia la pantalla

#include <cpctelera.h>

void main(void) {
    cpct_disableFirmware();
    cpct_clearScreen(0x00);
    while(1);
}
"""


@pytest.fixture
def global_vars():
    """Mock global variables for testing."""
    return {
        'model': 'gpt-4o',
        'temperature': 0.3,
        'max_tokens': 8096,
        'max_examples': 15,
        'system_prompt_file': 'resources/system_prompt_spectrum.txt',
        'base_output_dir': 'local',
        'slug_max_length': 40,
        'embeddings_cache_dir': 'local/embeddings',
        'example_dir_template': 'examples/{platform}',
        'max_example_size': 50000,
        'log_dir': 'local/logs'
    }
