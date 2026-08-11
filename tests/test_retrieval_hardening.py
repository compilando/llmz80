from llmz80.api.generator import _select_context_examples
from llmz80.core.example_catalog import infer_capabilities


def _example(path, content, score, source, capabilities):
    return {
        "path": path,
        "content": content,
        "score": score,
        "source": source,
        "capabilities": capabilities,
    }


def test_context_selection_deduplicates_content_across_learned_paths():
    examples = [
        _example("learned/one.c", "void main(void){}", 0.4, "learned", ["input"]),
        _example("learned/two.c", "void main(void){}", 0.3, "learned", ["input"]),
        _example("certified/main.c", "void main(void){for(;;){}}", 0.2, "local_catalog", ["input"]),
    ]
    selected = _select_context_examples(examples, 8)
    assert [item["path"] for item in selected] == ["learned/one.c", "certified/main.c"]
    assert len({item["content_sha256"] for item in selected}) == len(selected)


def test_context_selection_caps_learned_examples_for_diversity():
    examples = [
        _example(f"learned/{index}.c", f"void main(void){{int x={index};}}", 1 - index / 10, "learned", ["input"])
        for index in range(5)
    ]
    examples.extend([
        _example("local/a.c", "void main(void){int a;}", 0.1, "local_catalog", ["tiles"]),
        _example("local/b.c", "void main(void){int b;}", 0.09, "local_catalog", ["sprite"]),
    ])
    selected = _select_context_examples(examples, 6)
    assert sum(item["source"] == "learned" for item in selected) == 3
    assert {"local/a.c", "local/b.c"} <= {item["path"] for item in selected}


def test_comecocos_intent_exposes_gameplay_retrieval_capabilities():
    capabilities = set(infer_capabilities("un comecocos llamado IV"))
    assert {"input", "sprite", "tiles", "collision", "collect", "score"} <= capabilities
    assert {"input", "tiles", "collect"} <= set(infer_capabilities("a Pac-Man game"))
