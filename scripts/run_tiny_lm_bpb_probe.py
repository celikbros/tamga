from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.report_baseline_matrix import _load_toml  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

PAD_ID = 0
UNK_ID = 1
EOS_ID = 2
BYTE_OFFSET = 3
BYTE_VOCAB_SIZE = 256


@dataclass(frozen=True)
class TokenizerConfig:
    name: str
    kind: str
    path: Path | None = None
    max_vocab_size: int | None = None


@dataclass(frozen=True)
class ModelConfig:
    seq_len: int
    batch_size: int
    max_steps: int
    eval_interval: int
    learning_rate: float
    d_model: int
    n_layers: int
    n_heads: int
    ff_mult: int
    dropout: float
    device: str


@dataclass(frozen=True)
class ProbeConfig:
    path: Path
    split_dir: Path
    output_dir: Path
    report_out: Path
    seed: int
    model: ModelConfig
    tokenizers: list[TokenizerConfig]


@dataclass(frozen=True)
class SplitText:
    name: str
    lines: list[str]

    @property
    def bytes(self) -> int:
        return sum(len(line.encode("utf-8")) for line in self.lines)


@dataclass
class EncodedSplit:
    name: str
    ids: list[int]
    bytes: int
    lines: int
    oov_tokens: int = 0

    @property
    def tokens(self) -> int:
        return len(self.ids)

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def oov_rate(self) -> float:
        return self.oov_tokens / self.tokens if self.tokens else 0.0


@dataclass
class EncodedTokenizer:
    config: TokenizerConfig
    vocab_size: int
    status: str
    reason: str = ""
    splits: dict[str, EncodedSplit] = field(default_factory=dict)


@dataclass
class TrainMetrics:
    tokenizer: str
    status: str
    vocab_size: int
    total_params: int = 0
    embedding_params: int = 0
    non_embedding_params: int = 0
    steps: int = 0
    tokens_seen: int = 0
    approx_bytes_seen: float = 0.0
    best_valid_bpb: float | None = None
    final_valid_bpb: float | None = None
    test_bpb: float | None = None
    reason: str = ""


def _string_field(item: dict[str, Any], field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} requires string field {field!r}")
    return value


def _int_field(item: dict[str, Any], field: str, *, context: str) -> int:
    value = item.get(field)
    if not isinstance(value, int):
        raise ValueError(f"{context} requires integer field {field!r}")
    return value


def _float_field(item: dict[str, Any], field: str, *, context: str) -> float:
    value = item.get(field)
    if not isinstance(value, (float, int)):
        raise ValueError(f"{context} requires numeric field {field!r}")
    return float(value)


def load_probe_config(path: str | Path) -> ProbeConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    model_raw = raw.get("model", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")
    if not isinstance(model_raw, dict):
        raise ValueError("[model] must be a table")

    tokenizers: list[TokenizerConfig] = []
    for item in raw.get("tokenizers", []):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name = _string_field(item, "name", context="tokenizer")
        kind = _string_field(item, "kind", context=f"tokenizer {name}")
        if kind not in {"custom", "sentencepiece", "utf8_byte"}:
            raise ValueError(f"unsupported tokenizer kind for {name}: {kind}")
        tokenizers.append(
            TokenizerConfig(
                name=name,
                kind=kind,
                path=Path(item["path"]) if isinstance(item.get("path"), str) else None,
                max_vocab_size=item.get("max_vocab_size")
                if isinstance(item.get("max_vocab_size"), int)
                else None,
            )
        )

    return ProbeConfig(
        path=config_path,
        split_dir=Path(_string_field(settings, "split_dir", context="settings")),
        output_dir=Path(settings.get("output_dir", "artifacts/private/v1_8_tiny_lm_bpb_probe")),
        report_out=Path(settings.get("report_out", "artifacts/v1_8_tiny_lm_bpb_probe.md")),
        seed=_int_field(settings, "seed", context="settings"),
        model=ModelConfig(
            seq_len=_int_field(model_raw, "seq_len", context="model"),
            batch_size=_int_field(model_raw, "batch_size", context="model"),
            max_steps=_int_field(model_raw, "max_steps", context="model"),
            eval_interval=_int_field(model_raw, "eval_interval", context="model"),
            learning_rate=_float_field(model_raw, "learning_rate", context="model"),
            d_model=_int_field(model_raw, "d_model", context="model"),
            n_layers=_int_field(model_raw, "n_layers", context="model"),
            n_heads=_int_field(model_raw, "n_heads", context="model"),
            ff_mult=_int_field(model_raw, "ff_mult", context="model"),
            dropout=_float_field(model_raw, "dropout", context="model"),
            device=_string_field(model_raw, "device", context="model"),
        ),
        tokenizers=tokenizers,
    )


def load_split_texts(split_dir: str | Path) -> dict[str, SplitText]:
    root = Path(split_dir)
    splits: dict[str, SplitText] = {}
    for name in ("train", "valid", "test"):
        path = root / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        splits[name] = SplitText(
            name=name,
            lines=[line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()],
        )
    return splits


def build_custom_vocab(lines: list[str], *, max_vocab_size: int | None) -> dict[str, int]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    counts: Counter[str] = Counter()
    for line in lines:
        counts.update(tokenizer.encode(line))

    vocab = {"<pad>": PAD_ID, "<unk>": UNK_ID, "<eos>": EOS_ID}
    for byte in range(BYTE_VOCAB_SIZE):
        vocab[f"<byte_{byte:02x}>"] = BYTE_OFFSET + byte

    reserved = len(vocab)
    if max_vocab_size is not None and max_vocab_size < reserved:
        raise ValueError(
            f"custom max_vocab_size={max_vocab_size} is too small; "
            f"needs at least {reserved} for specials plus byte fallback"
        )

    limit = max_vocab_size - reserved if max_vocab_size is not None else None
    for token, _count in counts.most_common(limit):
        if token not in vocab:
            vocab[token] = len(vocab)
    return vocab


def encode_custom_split(lines: list[str], vocab: dict[str, int], byte_count: int, split: str) -> EncodedSplit:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    ids: list[int] = []
    fallback_source_tokens = 0
    for line in lines:
        for token in tokenizer.encode(line):
            token_id = vocab.get(token)
            if token_id is None:
                fallback_source_tokens += 1
                ids.extend(BYTE_OFFSET + byte for byte in token.encode("utf-8"))
            else:
                ids.append(token_id)
        ids.append(EOS_ID)
    return EncodedSplit(
        split,
        ids,
        byte_count,
        len(lines),
        oov_tokens=fallback_source_tokens,
    )


def encode_utf8_byte_split(lines: list[str], byte_count: int, split: str) -> EncodedSplit:
    ids: list[int] = []
    for line in lines:
        ids.extend(line.encode("utf-8"))
        ids.append(256)
    return EncodedSplit(split, ids, byte_count, len(lines))


def encode_sentencepiece_split(model_path: Path, lines: list[str], byte_count: int, split: str) -> EncodedSplit:
    import sentencepiece as spm  # type: ignore[import-not-found]

    processor = spm.SentencePieceProcessor(model_file=str(model_path))
    eos = processor.eos_id()
    ids: list[int] = []
    for line in lines:
        ids.extend(int(piece_id) for piece_id in processor.encode(line, out_type=int))
        if eos >= 0:
            ids.append(int(eos))
    return EncodedSplit(split, ids, byte_count, len(lines))


def encode_tokenizer(config: TokenizerConfig, splits: dict[str, SplitText]) -> EncodedTokenizer:
    try:
        if config.kind == "custom":
            vocab = build_custom_vocab(
                splits["train"].lines,
                max_vocab_size=config.max_vocab_size,
            )
            encoded = {
                name: encode_custom_split(split.lines, vocab, split.bytes, name)
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, len(vocab), "ok", splits=encoded)
        if config.kind == "utf8_byte":
            encoded = {
                name: encode_utf8_byte_split(split.lines, split.bytes, name)
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, 257, "ok", splits=encoded)
        if config.kind == "sentencepiece":
            if config.path is None or not config.path.exists():
                return EncodedTokenizer(config, 0, "skipped", reason=f"missing model: {config.path}")
            import sentencepiece as spm  # type: ignore[import-not-found]

            processor = spm.SentencePieceProcessor(model_file=str(config.path))
            encoded = {
                name: encode_sentencepiece_split(config.path, split.lines, split.bytes, name)
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, int(processor.GetPieceSize()), "ok", splits=encoded)
    except Exception as exc:
        return EncodedTokenizer(config, 0, "skipped", reason=str(exc))
    raise ValueError(f"unsupported tokenizer kind: {config.kind}")


def encode_all(config: ProbeConfig) -> list[EncodedTokenizer]:
    splits = load_split_texts(config.split_dir)
    encoded: list[EncodedTokenizer] = []
    for tokenizer in config.tokenizers:
        print(f"Encoding tokenizer={tokenizer.name} kind={tokenizer.kind}", flush=True)
        result = encode_tokenizer(tokenizer, splits)
        encoded.append(result)
        if result.status == "ok":
            train = result.splits["train"]
            valid = result.splits["valid"]
            test = result.splits["test"]
            print(
                f"Encoded tokenizer={tokenizer.name} vocab={result.vocab_size} "
                f"train_tokens={train.tokens} valid_tokens={valid.tokens} "
                f"test_tokens={test.tokens} "
                f"valid_fallback_source_tokens={valid.oov_tokens} "
                f"test_fallback_source_tokens={test.oov_tokens}",
                flush=True,
            )
        else:
            print(
                f"Skipped tokenizer={tokenizer.name} reason={result.reason}",
                flush=True,
            )
    return encoded


def _require_torch():
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as functional
    except Exception as exc:  # pragma: no cover - depends on optional dependency.
        raise RuntimeError("PyTorch is required to run training") from exc
    return torch, nn, functional


def _device(torch, requested: str):
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def build_model(vocab_size: int, model_config: ModelConfig):
    torch, nn, _functional = _require_torch()

    class TinyTransformerLM(nn.Module):
        def __init__(self):
            super().__init__()
            self.token_emb = nn.Embedding(vocab_size, model_config.d_model)
            self.pos_emb = nn.Embedding(model_config.seq_len, model_config.d_model)
            layer = nn.TransformerEncoderLayer(
                d_model=model_config.d_model,
                nhead=model_config.n_heads,
                dim_feedforward=model_config.d_model * model_config.ff_mult,
                dropout=model_config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.blocks = nn.TransformerEncoder(layer, num_layers=model_config.n_layers)
            self.norm = nn.LayerNorm(model_config.d_model)
            self.lm_head = nn.Linear(model_config.d_model, vocab_size, bias=False)
            self.lm_head.weight = self.token_emb.weight

        def forward(self, input_ids):
            batch, seq_len = input_ids.shape
            positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
            hidden = self.token_emb(input_ids) + self.pos_emb(positions)
            mask = torch.triu(
                torch.ones(seq_len, seq_len, dtype=torch.bool, device=input_ids.device),
                diagonal=1,
            )
            hidden = self.blocks(hidden, mask=mask)
            return self.lm_head(self.norm(hidden))

    return TinyTransformerLM()


def model_param_counts(model) -> tuple[int, int, int]:
    total = sum(parameter.numel() for parameter in model.parameters())
    embedding = model.token_emb.weight.numel() + model.pos_emb.weight.numel()
    return total, embedding, total - embedding


def sample_batch(torch, ids: list[int], *, seq_len: int, batch_size: int, rng: random.Random, device):
    if len(ids) <= seq_len + 1:
        raise ValueError("encoded train split is too short for configured seq_len")
    starts = [rng.randrange(0, len(ids) - seq_len - 1) for _ in range(batch_size)]
    inputs = [ids[start : start + seq_len] for start in starts]
    targets = [ids[start + 1 : start + seq_len + 1] for start in starts]
    return (
        torch.tensor(inputs, dtype=torch.long, device=device),
        torch.tensor(targets, dtype=torch.long, device=device),
    )


def evaluate_bpb(model, encoded: EncodedSplit, *, model_config: ModelConfig, device) -> float:
    torch, _nn, functional = _require_torch()
    model.eval()
    total_nll = 0.0
    total_targets = 0
    ids = encoded.ids
    with torch.no_grad():
        for start in range(0, max(0, len(ids) - model_config.seq_len - 1), model_config.seq_len):
            chunk = ids[start : start + model_config.seq_len + 1]
            if len(chunk) < model_config.seq_len + 1:
                continue
            inputs = torch.tensor([chunk[:-1]], dtype=torch.long, device=device)
            targets = torch.tensor([chunk[1:]], dtype=torch.long, device=device)
            logits = model(inputs)
            loss = functional.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
                reduction="sum",
            )
            total_nll += float(loss.item())
            total_targets += int(targets.numel())
    if total_targets == 0 or encoded.bytes == 0:
        return float("nan")
    evaluated_fraction = total_targets / max(1, len(ids) - 1)
    evaluated_bytes = encoded.bytes * evaluated_fraction
    return total_nll / math.log(2) / evaluated_bytes


def train_one(
    encoded: EncodedTokenizer,
    config: ProbeConfig,
    *,
    output_dir: Path,
) -> TrainMetrics:
    if encoded.status != "ok":
        return TrainMetrics(
            tokenizer=encoded.config.name,
            status=encoded.status,
            vocab_size=encoded.vocab_size,
            reason=encoded.reason,
        )

    torch, _nn, functional = _require_torch()
    torch.manual_seed(config.seed)
    rng = random.Random(config.seed)
    device = _device(torch, config.model.device)
    model = build_model(encoded.vocab_size, config.model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.model.learning_rate)
    total_params, embedding_params, non_embedding_params = model_param_counts(model)

    train_ids = encoded.splits["train"].ids
    train_tokens_per_byte = encoded.splits["train"].tokens_per_byte
    metrics_path = output_dir / encoded.config.name / "metrics.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    best_valid: float | None = None
    final_valid: float | None = None
    tokens_seen = 0

    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        for step in range(1, config.model.max_steps + 1):
            model.train()
            inputs, targets = sample_batch(
                torch,
                train_ids,
                seq_len=config.model.seq_len,
                batch_size=config.model.batch_size,
                rng=rng,
                device=device,
            )
            logits = model(inputs)
            loss = functional.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            tokens_seen += int(targets.numel())

            if step == 1 or step % config.model.eval_interval == 0 or step == config.model.max_steps:
                valid_bpb = evaluate_bpb(model, encoded.splits["valid"], model_config=config.model, device=device)
                final_valid = valid_bpb
                best_valid = valid_bpb if best_valid is None else min(best_valid, valid_bpb)
                approx_bytes = tokens_seen / train_tokens_per_byte if train_tokens_per_byte else 0.0
                row = {
                    "step": step,
                    "train_loss_nats_per_token": float(loss.item()),
                    "valid_bpb": valid_bpb,
                    "tokens_seen": tokens_seen,
                    "approx_bytes_seen": approx_bytes,
                }
                metrics_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                metrics_file.flush()
                print(
                    f"{encoded.config.name}: step={step} "
                    f"tokens_seen={tokens_seen} approx_bytes_seen={approx_bytes:.0f} "
                    f"valid_bpb={valid_bpb:.6f}",
                    flush=True,
                )

    test_bpb = evaluate_bpb(model, encoded.splits["test"], model_config=config.model, device=device)
    return TrainMetrics(
        tokenizer=encoded.config.name,
        status="ok",
        vocab_size=encoded.vocab_size,
        total_params=total_params,
        embedding_params=embedding_params,
        non_embedding_params=non_embedding_params,
        steps=config.model.max_steps,
        tokens_seen=tokens_seen,
        approx_bytes_seen=tokens_seen / train_tokens_per_byte if train_tokens_per_byte else 0.0,
        best_valid_bpb=best_valid,
        final_valid_bpb=final_valid,
        test_bpb=test_bpb,
    )


def _fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    config: ProbeConfig,
    encoded_tokenizers: list[EncodedTokenizer],
    train_metrics: list[TrainMetrics],
    *,
    dry_run: bool,
) -> str:
    lines = [
        "# v1.8 Tiny LM Bits-Per-Byte Probe",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Split dir: `{config.split_dir.as_posix()}`",
        f"Dry run: `{dry_run}`",
        "",
        "This is an early screening probe, not final LLM tokenizer evidence.",
        "",
        "## Model Config",
        "",
        "| Setting | Value |",
        "| --- | ---: |",
        f"| seq_len | {config.model.seq_len} |",
        f"| batch_size | {config.model.batch_size} |",
        f"| max_steps | {config.model.max_steps} |",
        f"| eval_interval | {config.model.eval_interval} |",
        f"| d_model | {config.model.d_model} |",
        f"| n_layers | {config.model.n_layers} |",
        f"| n_heads | {config.model.n_heads} |",
        "",
        "## Encoding Summary",
        "",
        "| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for encoded in encoded_tokenizers:
        if encoded.status != "ok":
            lines.append(
                f"| {encoded.config.name} | {encoded.status} | {encoded.vocab_size} |  | 0 | 0 | 0 | 0.000000 | 0 | 0.000000 | {encoded.reason} |"
            )
            continue
        for split_name in ("train", "valid", "test"):
            split = encoded.splits[split_name]
            lines.append(
                f"| {encoded.config.name} | {encoded.status} | {encoded.vocab_size} | "
                f"{split_name} | {split.lines} | {split.bytes} | {split.tokens} | "
                f"{split.tokens_per_byte:.6f} | {split.oov_tokens} | "
                f"{split.oov_rate:.6f} | {encoded.reason} |"
            )

    lines.extend(
        [
            "",
            "## Training Results",
            "",
            "| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    if dry_run:
        lines.append("| dry_run | skipped | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  | no training run |")
    else:
        for row in train_metrics:
            lines.append(
                f"| {row.tokenizer} | {row.status} | {row.vocab_size} | "
                f"{row.total_params} | {row.embedding_params} | {row.non_embedding_params} | "
                f"{row.steps} | {row.tokens_seen} | {row.approx_bytes_seen:.0f} | "
                f"{_fmt_float(row.best_valid_bpb)} | {_fmt_float(row.final_valid_bpb)} | "
                f"{_fmt_float(row.test_bpb)} | {row.reason} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Compare only byte-normalized validation/test loss, not token perplexity.",
            "- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.",
            "- This script does not make the tokenizer LLM-ready.",
            "- A negative result should be read with the v1.8 protocol caveats.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_encoded_artifacts(config: ProbeConfig, encoded_tokenizers: list[EncodedTokenizer]) -> None:
    target = config.output_dir / "encoded_stats.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for encoded in encoded_tokenizers:
            item = {
                "tokenizer": encoded.config.name,
                "status": encoded.status,
                "reason": encoded.reason,
                "vocab_size": encoded.vocab_size,
                "splits": {
                    name: {
                        "lines": split.lines,
                        "bytes": split.bytes,
                        "tokens": split.tokens,
                        "tokens_per_byte": split.tokens_per_byte,
                        "oov_tokens": split.oov_tokens,
                        "oov_rate": split.oov_rate,
                    }
                    for name, split in encoded.splits.items()
                },
            }
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run or dry-run the v1.8 tiny LM BPB probe.")
    parser.add_argument("config")
    parser.add_argument("--dry-run", action="store_true", help="Only encode splits and write the report.")
    parser.add_argument(
        "--tokenizer",
        action="append",
        default=[],
        help="Restrict to one or more tokenizer names.",
    )
    parser.add_argument("--max-steps", type=int, help="Override configured max_steps.")
    parser.add_argument("--report-out", help="Override configured public report path.")
    parser.add_argument("--output-dir", help="Override configured private output directory.")
    args = parser.parse_args(argv)

    config = load_probe_config(args.config)
    if args.max_steps is not None:
        if args.max_steps <= 0:
            raise ValueError("--max-steps must be positive")
        config = replace(
            config,
            model=replace(config.model, max_steps=args.max_steps),
        )
    if args.report_out:
        config = replace(config, report_out=Path(args.report_out))
    if args.output_dir:
        config = replace(config, output_dir=Path(args.output_dir))
    if args.tokenizer:
        selected = set(args.tokenizer)
        config = ProbeConfig(
            path=config.path,
            split_dir=config.split_dir,
            output_dir=config.output_dir,
            report_out=config.report_out,
            seed=config.seed,
            model=config.model,
            tokenizers=[tokenizer for tokenizer in config.tokenizers if tokenizer.name in selected],
        )
        unknown = selected - {tokenizer.name for tokenizer in config.tokenizers}
        if unknown:
            raise ValueError(f"unknown tokenizer name(s): {', '.join(sorted(unknown))}")

    print(
        f"Starting tiny LM BPB probe: dry_run={args.dry_run} "
        f"tokenizers={len(config.tokenizers)} split_dir={config.split_dir}",
        flush=True,
    )
    encoded_tokenizers = encode_all(config)
    write_encoded_artifacts(config, encoded_tokenizers)

    train_metrics: list[TrainMetrics] = []
    if not args.dry_run:
        for encoded in encoded_tokenizers:
            print(f"Training tokenizer={encoded.config.name}", flush=True)
            train_metrics.append(train_one(encoded, config, output_dir=config.output_dir))

    report = format_report(
        config,
        encoded_tokenizers,
        train_metrics,
        dry_run=args.dry_run,
    )
    config.report_out.parent.mkdir(parents=True, exist_ok=True)
    config.report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {config.report_out}")
    print(f"wrote_private_stats: {config.output_dir / 'encoded_stats.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
