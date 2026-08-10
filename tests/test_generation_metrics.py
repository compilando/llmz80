from types import SimpleNamespace

from llmz80.api.generator import LLMZ80Generator


def test_api_metrics_accumulate_real_usage_and_latency(tmp_path):
    generator = object.__new__(LLMZ80Generator)
    generator.generation_metrics = {
        "schema_version": 1, "calls": 0, "latency_ms": 0,
        "input_tokens": 0, "output_tokens": 0, "model": "fixture",
    }
    response = SimpleNamespace(usage=SimpleNamespace(prompt_tokens=12, completion_tokens=7))
    generator._capture_response_metrics(response, 0.125, "prompt")
    generator._capture_response_metrics(response, 0.075, "prompt")
    generator.save_generation_metrics(tmp_path)
    assert generator.generation_metrics["calls"] == 2
    assert generator.generation_metrics["latency_ms"] == 200
    assert generator.generation_metrics["input_tokens"] == 24
    assert (tmp_path / "generation_metrics.json").exists()
