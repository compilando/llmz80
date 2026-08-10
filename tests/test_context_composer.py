from llmz80.api.generator import LLMZ80Generator, MAX_PROMPT_EXAMPLE_CHARS


def test_context_composer_never_truncates_programs():
    generator = object.__new__(LLMZ80Generator)
    complete = "void main(void) { while (1) { } }"
    oversized = "void main(void) {\n" + ("x++;\n" * MAX_PROMPT_EXAMPLE_CHARS) + "}\n"
    result = generator._fit_examples_for_prompt([
        {"path": "complete.c", "content": complete, "score": 1.0},
        {"path": "huge.c", "content": oversized, "score": 0.5},
    ])
    assert [item["content"] for item in result] == [complete]
    assert "truncated" not in result[0]["content"]
    assert generator.last_context_manifest["selected"][0]["path"] == "complete.c"
    assert generator.last_context_manifest["dropped"][0]["path"] == "huge.c"


def test_context_manifest_has_stable_provenance_hash():
    generator = object.__new__(LLMZ80Generator)
    examples = [{"path": "one.c", "content": "void main(void){}", "score": 0.3}]
    generator._fit_examples_for_prompt(examples)
    first = generator.last_context_manifest
    generator._fit_examples_for_prompt(examples)
    assert generator.last_context_manifest == first
    assert len(first["selected"][0]["sha256"]) == 64


def test_context_keeps_one_high_relevance_example_above_standard_cap():
    generator = object.__new__(LLMZ80Generator)
    relevant = "void main(void) {\n" + ("x++;\n" * 1900) + "}\n"
    small = "void main(void){}"
    result = generator._fit_examples_for_prompt([
        {"path": "movement.c", "content": relevant, "score": 0.95},
        {"path": "base.c", "content": small, "score": 0.4},
    ])
    assert [item["content"] for item in result] == [relevant, small]
    assert generator.last_context_manifest["selected"][0]["selection"] == "primary_large_example"


def test_context_keeps_certified_spectrum_example_size():
    generator = object.__new__(LLMZ80Generator)
    spectrum_example = "void main(void){" + ("x++;" * 4540) + "}"
    assert 18000 < len(spectrum_example) < 20000
    result = generator._fit_examples_for_prompt([
        {"path": "05_sprites.c", "content": spectrum_example, "score": 0.9},
    ])
    assert [item["content"] for item in result] == [spectrum_example]
