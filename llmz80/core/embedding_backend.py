"""Where embeddings come from, in one place.

They used to come from `client.embeddings.create` on an OpenAI client, called
from three modules, with the vector's width written out as the literal 1536
in a dozen places across four files. That made the provider impossible to
change without finding every one of them, and made the one thing a caller
most needs to agree on -- how wide a vector is -- the thing most likely to
drift.

They now come from a model that runs on this machine. That is a real change
in kind, not just in vendor: there is no API key, no network call, no
per-token cost and no rate limit, which for a corpus that is re-indexed
whenever the example set changes is the difference between a chore and a
non-event. The cost is a one-off ~67MB model download on first use and a
process that holds it in memory.

**Vectors from this backend are 384 wide, not 1536.** Any Qdrant collection
built by the old backend is therefore unreadable here, and so is any cached
vector under `local/embeddings`. Both have to be rebuilt rather than
migrated -- see `scripts/init_qdrant.py` and `init_embeddings.py`.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

#: Small, fast and good enough for retrieving C examples by description. The
#: corpus is a few hundred short programs, not a search engine, and a larger
#: model would cost startup time and memory on every run to rank the same
#: handful of examples the same way.
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

#: How wide a vector from `embed` is. Every caller reads it from here rather
#: than writing the number out, because the number changing is exactly what
#: happens when the model does.
EMBEDDING_DIM = 384

_model = None


def _load():
    """The model, loaded once per process and only if something asks.

    Deliberately lazy: importing this module must stay free, because
    `llmz80/api/generator.py` imports the manager that uses it on a path
    that often never embeds anything at all -- and loading the model means
    reading ~67MB off disk, or downloading it the very first time.
    """
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        logger.info(f"Cargando modelo de embeddings local: {EMBEDDING_MODEL}")
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def zero_vector() -> np.ndarray:
    """The vector a caller substitutes when it has nothing to embed.

    Every caller used to spell this `np.zeros((1536,), dtype=float)` inline.
    It is here so that the width can only ever be wrong in one place.
    """
    return np.zeros((EMBEDDING_DIM,), dtype=float)


def embed(texts: list[str]) -> list[np.ndarray]:
    """`texts` as vectors, in the same order.

    Returns float64 arrays because that is what every caller already
    expects: `EmbeddingsManager` averages chunk vectors with `np.mean` and
    compares them with a cosine written against `numpy.linalg.norm`, and
    fastembed hands back float32.
    """
    if not texts:
        return []
    return [np.asarray(vector, dtype=float) for vector in _load().embed(texts)]
