"""Reading config.yml, and the one API key Studio needs.

What used to live here besides that -- an OpenAI key, an OpenAI model default,
a temperature, a token ceiling, an embedding model name, and
`initialize_global_vars`, which flattened the whole file into one dictionary of
run parameters -- went with the legacy generator. Studio reads the two or three
keys it wants where it wants them, so there is nothing left to flatten.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

#: Where this project's own files live, whatever directory the command was
#: run from. Every path below used to be resolved against the caller's cwd,
#: which is why `llmz80` on the PATH failed anywhere but the checkout: a
#: console script is expected to work from a user's home directory, and this
#: one died on `resources/platforms.yml` before it printed anything.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_file(path: str | Path) -> Path:
    """`path` as given if it exists, else the same name under the project.

    Tried in that order rather than the other way round so a caller standing
    in a directory with its own `config.yml` still gets theirs -- the point is
    to stop relative paths failing away from the checkout, not to stop them
    working inside it.
    """
    candidate = Path(path)
    if candidate.exists():
        return candidate
    return PROJECT_ROOT / candidate


def load_config(config_path: str) -> Dict[str, Any]:
    """The YAML at `config_path` as a dictionary, or an empty one.

    A missing file is not an error: every caller reads keys with a default
    beside them, so a checkout with no config.yml runs on those defaults
    rather than refusing to start. A file that exists and cannot be parsed
    *is* an error -- that is a typo somebody wants to hear about, not a
    reason to silently ignore everything they configured.
    """
    resolved = resolve_project_file(config_path)
    try:
        with open(resolved, "r", encoding="utf-8") as handle:
            config_data = yaml.safe_load(handle)
    except FileNotFoundError:
        logger.warning("no configuration at %s; using defaults", resolved)
        return {}
    except Exception as error:
        logger.error("could not read the configuration at %s: %s", resolved, error)
        raise
    logger.info("configuration read from %s", resolved)
    return config_data if config_data else {}


#: The kinds of question Studio asks, each of which may be worth a different
#: model. A *kind*, not a call site: `exam` covers the brief examiner, the
#: coherence examiner and the runtime examiner, so a fourth one added later
#: joins a role instead of adding a key nobody sets.
#:
#: They exist because one model for everything is one decision for two very
#: different jobs. Deciding what a game is and writing its C is worth the best
#: model there is. Transcribing an 8x8 tile into eight rows of pen characters
#: and answering `coherent: true` was being charged at the same rate, which is
#: what a survey of `studio-projects/*/studio.log` was looking for.
ROLES = ("research", "design", "art", "exam", "program")

#: What a role falls back to when neither `anthropic.models.<role>` nor
#: `anthropic.model` is set. The best model, deliberately: an unconfigured
#: checkout should produce the best game it can, and the cheaper choices are
#: something somebody opts into with the bill in front of them.
DEFAULT_MODEL = "claude-opus-5"


def model_for(role: str, config: Dict[str, Any] | None = None) -> str:
    """The model to ask `role`'s questions of.

    `anthropic.models.<role>` when it is set, `anthropic.model` when it is
    not. Both, rather than only the specific one, so a checkout that names a
    single model in the way this project always has goes on working unchanged.

    An unknown role raises rather than falling back. A fallback would answer a
    typo with the most expensive model in the table and never mention it,
    which is precisely the failure mode this function was added to close.
    """
    if role not in ROLES:
        raise ValueError(f"unknown model role {role!r}: expected one of {', '.join(ROLES)}")
    section = (config or load_config("config.yml")).get("anthropic") or {}
    by_role = section.get("models") or {}
    return str(by_role.get(role) or section.get("model") or DEFAULT_MODEL)


def load_anthropic_api_key() -> str:
    """The Anthropic key, from the environment or a .env beside the checkout.

    Named for its provider rather than taking one as an argument, which is
    what it was when an OpenAI key lived beside it: a failure then says which
    key is missing instead of naming a provider the caller may not have meant.
    Only one of the pair is left -- Studio calls Anthropic and nothing calls
    OpenAI any more -- but the naming stays, because the next provider added
    should get its own function rather than a parameter here.
    """
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY is not set, in the environment or in .env")
        raise ValueError("ANTHROPIC_API_KEY is required.")
    return api_key
