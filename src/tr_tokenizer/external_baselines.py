from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import importlib
from pathlib import Path


@dataclass(frozen=True)
class BaselineEncoding:
    name: str
    tokens: list[str]
    status: str = "ok"
    reason: str = ""

    @property
    def available(self) -> bool:
        return self.status == "ok"


def _missing_package(name: str) -> str:
    return f"optional dependency not installed: {name}"


def encode_unicode_chars(text: str, *, name: str = "unicode_char") -> BaselineEncoding:
    tokens: list[str] = []
    at_word_start = True

    for char in text:
        if char.isspace():
            at_word_start = True
            continue

        if at_word_start and (char.isalnum() or char == "_"):
            tokens.append(f"▁{char}")
        else:
            tokens.append(char)
        at_word_start = False

    return BaselineEncoding(name=name, tokens=tokens)


def encode_huggingface(
    text: str,
    *,
    model_id: str,
    name: str,
    local_files_only: bool = True,
) -> BaselineEncoding:
    transformers = importlib.util.find_spec("transformers")
    if transformers is None:
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=_missing_package("transformers"),
        )

    try:
        tokenizer = _load_huggingface_tokenizer(model_id, local_files_only)
    except Exception as exc:  # pragma: no cover - depends on local model cache.
        scope = "local cache" if local_files_only else "remote download"
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=f"could not load {model_id!r} from {scope}: {exc}",
        )

    tokens = tokenizer.tokenize(text)
    return BaselineEncoding(name=name, tokens=list(tokens))


def encode_tokenizers_json(
    text: str,
    *,
    tokenizer_path: str | Path,
    name: str,
) -> BaselineEncoding:
    tokenizers = importlib.util.find_spec("tokenizers")
    if tokenizers is None:
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=_missing_package("tokenizers"),
        )

    try:
        tokenizer = _load_tokenizers_json(str(tokenizer_path))
    except Exception as exc:  # pragma: no cover - depends on local model file.
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=f"could not load tokenizers JSON {tokenizer_path!r}: {exc}",
        )

    return BaselineEncoding(name=name, tokens=list(tokenizer.encode(text).tokens))


@lru_cache(maxsize=16)
def _load_huggingface_tokenizer(model_id: str, local_files_only: bool):
    from transformers import AutoTokenizer  # type: ignore[import-not-found]

    return AutoTokenizer.from_pretrained(
        model_id,
        local_files_only=local_files_only,
        trust_remote_code=False,
    )


@lru_cache(maxsize=16)
def _load_tokenizers_json(tokenizer_path: str):
    from tokenizers import Tokenizer  # type: ignore[import-not-found]

    return Tokenizer.from_file(tokenizer_path)


def encode_sentencepiece(
    text: str,
    *,
    model_path: str | Path,
    name: str,
) -> BaselineEncoding:
    sentencepiece = importlib.util.find_spec("sentencepiece")
    if sentencepiece is None:
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=_missing_package("sentencepiece"),
        )

    try:
        processor = _load_sentencepiece_processor(str(model_path))
    except Exception as exc:  # pragma: no cover - depends on local model file.
        return BaselineEncoding(
            name=name,
            tokens=[],
            status="skipped",
            reason=f"could not load sentencepiece model {model_path!r}: {exc}",
        )

    return BaselineEncoding(name=name, tokens=list(processor.encode(text, out_type=str)))


@lru_cache(maxsize=16)
def _load_sentencepiece_processor(model_path: str):
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm.SentencePieceProcessor(model_file=model_path)


def parse_named_spec(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise ValueError(f"expected NAME=VALUE, got {spec!r}")
    name, value = spec.split("=", 1)
    name = name.strip()
    value = value.strip()
    if not name or not value:
        raise ValueError(f"expected NAME=VALUE, got {spec!r}")
    return name, value
