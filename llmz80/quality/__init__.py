"""Quality evaluation primitives for generated retro programs."""

from .benchmark import evaluate_corpus, load_corpus, write_scorecard

__all__ = ["evaluate_corpus", "load_corpus", "write_scorecard"]
