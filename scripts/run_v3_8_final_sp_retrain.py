from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any

# Consumer (LLM-team) environment root; see run_v3_8_final_release_gates.py.
GARDASH_ROOT = os.environ.get("GARDASH_ROOT", "C:/CELIK-GARDASH")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.train_sentencepiece_baselines import train_sentencepiece  # noqa: E402


DEFAULT_TOML_ROUTES = [
    "url",
    "technical_comparator",
    "file_like",
    "apostrophe_surface",
    "non_turkish_latin_word",
    "greek_word",
    "uzbek_apostrophe_word",
    "cyrillic_word",
    "arabic_word",
    "percent_encoded",
    "azerbaijani_word",
]

DEFAULT_JSON_ROUTES = ["numeric_like", *DEFAULT_TOML_ROUTES]

DEFAULT_CONTROL_TOKENS = {
    "<pad>": 64256,
    "<system>": 64257,
    "<user>": 64258,
    "<assistant>": 64259,
    "<thinking>": 64260,
    "</thinking>": 64261,
    "<answer>": 64262,
    "</answer>": 64263,
    "<tool_call>": 64264,
    "<tool_result>": 64265,
}


@dataclass(frozen=True)
class RetrainPlan:
    corpus_text: Path
    model_prefix: Path
    tokenizer_name: str
    toml_out: Path
    tokenizer_config_out: Path
    report_out: Path
    template_config: Path | None
    vocab_size: int
    model_type: str
    max_sentence_length: int
    num_threads: int
    input_sentence_size: int
    shuffle_input_sentence: bool
    train_extremely_large_corpus: bool
    effective_vocab_size: int
    train: bool
    force: bool
    status: str

    @property
    def model_path(self) -> Path:
        return self.model_prefix.with_suffix(".model")

    @property
    def vocab_path(self) -> Path:
        return self.model_prefix.with_suffix(".vocab")


def posix(path: Path) -> str:
    return path.as_posix()


def normalize_prefix(path: Path) -> Path:
    if path.suffix in {".model", ".vocab"}:
        return path.with_suffix("")
    return path


def load_template(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"template config must be a JSON object: {path}")
    return raw


def build_tokenizer_config(plan: RetrainPlan) -> dict[str, Any]:
    raw = load_template(plan.template_config)
    config: dict[str, Any] = dict(raw)
    config["schema_version"] = "tokenizer-config-v3.8-final-sp64k-1"
    config["status"] = plan.status
    config["tokenizer_name"] = plan.tokenizer_name
    config["description"] = (
        "SP64K final-corpus retrain candidate for CELIK-GARDASH. "
        "This config is valid only after the final corpus manifest, SP retrain, "
        "tokenized package gates, and LLM-engine smoke pass."
    )
    config["model"] = {
        "type": "sentencepiece_unigram",
        "sp_model_path": posix(plan.model_path),
        "sp_vocab_path": posix(plan.vocab_path),
        "sp_vocab_size": plan.vocab_size,
        "normal_text_flow": "sentencepiece",
        "trained_on_full_gardash_corpus": True,
        "training_sample": "v3.8 frozen final corpus text",
    }
    config["id_space"] = {
        "sp_id_start": 0,
        "sp_id_end_exclusive": plan.vocab_size,
        "byte_fallback_start": plan.vocab_size,
        "byte_fallback_size": 256,
        "byte_fallback_end_exclusive": plan.vocab_size + 256,
        "control_token_start": plan.vocab_size + 256,
        "control_token_reserved_size": plan.effective_vocab_size - (plan.vocab_size + 256),
        "control_token_end_exclusive": plan.effective_vocab_size,
        "current_effective_vocab_size": plan.effective_vocab_size,
    }
    config["sentencepiece_meta_tokens"] = {
        "unk": {"piece": "<unk>", "id": 0},
        "bos": {"piece": "<s>", "id": 1, "alias": "<bos>"},
        "eos": {"piece": "</s>", "id": 2, "alias": "<eos>"},
        "pad": {
            "piece": None,
            "id": -1,
            "status": "not_defined_in_current_sp_model; wrapper control id is defined in special_token_registry.assigned",
        },
    }
    config["special_token_registry"] = {
        "status": "frozen",
        "policy": "Control tokens are wrapper-level ids after byte fallback. Raw text tokenization never activates them.",
        "known_conflict": "<pad> is intentionally not id 0 because SP <unk> is id 0; do not remap <unk> in the wrapper.",
        "aliases": {"<bos>": 1, "<eos>": 2},
        "assigned": DEFAULT_CONTROL_TOKENS,
        "reserved_unassigned_range": {
            "start": max(DEFAULT_CONTROL_TOKENS.values()) + 1,
            "end_exclusive": plan.effective_vocab_size,
        },
    }
    config["sidecar"] = {
        "schema_version": "v2.2-sidecar-jsonl-1",
        "contract": "byte_offset_passthrough_sidecar",
        "token_boundary_alignment": False,
        "route_labels": DEFAULT_JSON_ROUTES,
        "sp_passthrough_routes": DEFAULT_JSON_ROUTES,
        "required_route_invariants": [
            "percent_encoded",
            "azerbaijani_word",
            "url",
            "technical_comparator",
        ],
    }
    config["training_preprocessing"] = {
        "recommended_hot_path": "binary_tokens_plus_optional_binary_loss_mask",
        "jsonl_sidecar_hot_path": "not_recommended",
        "token_dtype": "uint32_le",
        "loss_mask_dtype": "uint8",
        "default_line_separator": "eos_id_2",
        "control_token_injection": "outside_raw_text_tokenization",
    }
    config["evidence"] = {
        "source": "generated by scripts/run_v3_8_final_sp_retrain.py",
        "corpus_text": posix(plan.corpus_text),
        "open_gate": "must pass v3.8 final gates before irreversible main pretraining",
    }
    config["open_gates_before_training_final"] = [
        "final corpus preflight already passed",
        "SP model and vocab exist at the configured paths",
        "tokenizer config validation passes",
        "route/fertility/canary reports reviewed",
        "production tokenized package gates pass",
        "LLM-engine smoke passes",
    ]
    return config


def build_sidecar_toml(plan: RetrainPlan) -> str:
    route_lines = "\n".join(f'  "{route}",' for route in DEFAULT_TOML_ROUTES)
    return f"""[settings]
split_dir = "{GARDASH_ROOT}/datasets/pretraining_final/split"
output_dir = "{GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_tiny_lm"
report_out = "{GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_tiny_lm.md"
seed = 20260620
encode_progress = 5000

[model]
seq_len = 128
batch_size = 4
max_steps = 300
eval_interval = 100
learning_rate = 0.0003
d_model = 256
n_layers = 4
n_heads = 4
ff_mult = 4
dropout = 0.1
device = "auto"

[[tokenizers]]
name = "{plan.tokenizer_name}"
kind = "finite_protected_marker_stripped_numeric_sp"
path = "{posix(plan.model_path)}"
sp_passthrough_routes = [
{route_lines}
]
enabled = true
"""


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def train_if_requested(plan: RetrainPlan) -> list[str]:
    warnings: list[str] = []
    if not plan.train:
        return warnings
    if plan.model_path.exists() and plan.vocab_path.exists() and not plan.force:
        warnings.append(
            f"model already exists and --force was not set: {plan.model_path}"
        )
        return warnings
    train_sentencepiece(
        plan.corpus_text,
        plan.model_prefix,
        vocab_size=plan.vocab_size,
        model_type=plan.model_type,
        max_sentence_length=plan.max_sentence_length,
        num_threads=plan.num_threads,
        input_sentence_size=plan.input_sentence_size,
        shuffle_input_sentence=plan.shuffle_input_sentence,
        train_extremely_large_corpus=plan.train_extremely_large_corpus,
    )
    return warnings


def format_report(plan: RetrainPlan, *, warnings: list[str], failures: list[str]) -> str:
    status = "FAIL" if failures else ("TRAINED" if plan.train else "PLANNED")
    train_flag = "yes" if plan.train else "no"
    model_exists = "yes" if plan.model_path.exists() else "no"
    vocab_exists = "yes" if plan.vocab_path.exists() else "no"
    lines = [
        "# v3.8 Final SP64K Retrain Plan",
        "",
        f"Status: `{status}`",
        f"Train requested: `{train_flag}`",
        "",
        "## Inputs",
        "",
        f"- Corpus text: `{plan.corpus_text}`",
        f"- Template config: `{plan.template_config or 'none'}`",
        "",
        "## Planned Outputs",
        "",
        f"- SP model: `{plan.model_path}` (exists: `{model_exists}`)",
        f"- SP vocab: `{plan.vocab_path}` (exists: `{vocab_exists}`)",
        f"- Sidecar TOML: `{plan.toml_out}`",
        f"- Tokenizer config JSON: `{plan.tokenizer_config_out}`",
        "",
        "## SP Settings",
        "",
        "| Setting | Value |",
        "| --- | ---: |",
        f"| model_type | `{plan.model_type}` |",
        f"| vocab_size | {plan.vocab_size} |",
        f"| max_sentence_length | {plan.max_sentence_length} |",
        f"| num_threads | {plan.num_threads} |",
        f"| input_sentence_size | {plan.input_sentence_size} |",
        f"| shuffle_input_sentence | `{str(plan.shuffle_input_sentence).lower()}` |",
        f"| train_extremely_large_corpus | `{str(plan.train_extremely_large_corpus).lower()}` |",
        f"| normalizer | `identity` |",
        f"| remove_extra_whitespaces | `false` |",
        f"| byte_fallback | `wrapper-managed, ids {plan.vocab_size}..{plan.vocab_size + 255}` |",
        "",
        "## Failures",
        "",
    ]
    lines.extend(f"- {failure}" for failure in failures) if failures else lines.append("None.")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("None.")
    lines.extend(
        [
            "",
            "## Next Commands",
            "",
            "After a successful final retrain, run:",
            "",
            "```powershell",
            "python tokenizer_v3_0_repo_snapshot\\scripts\\validate_v3_1_tokenizer_config.py `",
            f"  --config {plan.tokenizer_config_out} `",
            f"  --report-out {GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_config_validation.md",
            "",
            "python tokenizer_v3_0_repo_snapshot\\scripts\\tokenize_corpus.py `",
            f"  --config {plan.toml_out} `",
            f"  --tokenizer {plan.tokenizer_name} `",
            f"  --input {plan.corpus_text} `",
            f"  --out-dir {GARDASH_ROOT}/datasets/tokenizer_v3_8_final_full `",
            f"  --report-out {GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_tokenize_corpus.md `",
            "  --max-lines 0 `",
            "  --workers 8 `",
            "  --chunk-lines 256 `",
            "  --progress 10000",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def run_plan(plan: RetrainPlan) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    if not plan.corpus_text.exists():
        failures.append(f"corpus text does not exist: {plan.corpus_text}")
    elif plan.corpus_text.stat().st_size == 0:
        failures.append(f"corpus text is empty: {plan.corpus_text}")
    if plan.vocab_size <= 0:
        failures.append("--vocab-size must be positive")
    if plan.vocab_size != 64000:
        failures.append("v3.8 final retrain launcher is locked to SP64K vocab_size=64000")
    if plan.effective_vocab_size < plan.vocab_size + 256:
        failures.append("--effective-vocab-size must be at least vocab_size + 256")
    if plan.effective_vocab_size != 64384:
        failures.append(
            "v3.8 final retrain launcher is locked to effective_vocab_size=64384"
        )
    if plan.effective_vocab_size <= max(DEFAULT_CONTROL_TOKENS.values()):
        failures.append("--effective-vocab-size does not cover assigned control tokens")
    if plan.model_type not in {"unigram", "bpe"}:
        failures.append("--model-type must be unigram or bpe")
    if plan.max_sentence_length <= 0:
        failures.append("--max-sentence-length must be positive")
    if plan.num_threads <= 0:
        failures.append("--num-threads must be positive")
    if plan.input_sentence_size < 0:
        failures.append("--input-sentence-size must be non-negative")

    if not failures:
        try:
            warnings.extend(train_if_requested(plan))
        except Exception as exc:  # pragma: no cover - depends on local SP runtime
            failures.append(f"training failed: {exc}")

    if not failures:
        write_text(plan.toml_out, build_sidecar_toml(plan))
        write_json(plan.tokenizer_config_out, build_tokenizer_config(plan))

    write_text(plan.report_out, format_report(plan, warnings=warnings, failures=failures))
    return failures, warnings


def parse_args(argv: list[str] | None = None) -> RetrainPlan:
    parser = argparse.ArgumentParser(
        description="Plan or run the v3.8 final SP64K retrain and write canonical configs."
    )
    parser.add_argument("--corpus-text", required=True)
    parser.add_argument(
        "--model-prefix",
        default=f"{GARDASH_ROOT}/models/tokenizer_v3_8/sp_unigram_64000_final",
    )
    parser.add_argument(
        "--tokenizer-name",
        default="sp64k_final_protected_passthrough_sidecar_controls128",
    )
    parser.add_argument(
        "--toml-out",
        default=f"{GARDASH_ROOT}/configs/tokenizer_v3_0/v3_8_final_sidecar_sp64k.toml",
    )
    parser.add_argument(
        "--tokenizer-config-out",
        default=f"{GARDASH_ROOT}/configs/tokenizer_v3_0/tokenizer_config.json",
    )
    parser.add_argument(
        "--report-out",
        default=f"{GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_sp_retrain_plan.md",
    )
    parser.add_argument(
        "--template-config",
        default="configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json",
    )
    parser.add_argument("--vocab-size", type=int, default=64000)
    parser.add_argument("--effective-vocab-size", type=int, default=64384)
    parser.add_argument("--model-type", choices=("unigram", "bpe"), default="unigram")
    parser.add_argument("--max-sentence-length", type=int, default=16384)
    parser.add_argument("--num-threads", type=int, default=16)
    parser.add_argument(
        "--input-sentence-size",
        type=int,
        default=0,
        help="SentencePiece input_sentence_size. 0 means use all sentences.",
    )
    parser.add_argument(
        "--shuffle-input-sentence",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--train-extremely-large-corpus",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--status", default="training_final_candidate_pending_gates")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    return RetrainPlan(
        corpus_text=Path(args.corpus_text),
        model_prefix=normalize_prefix(Path(args.model_prefix)),
        tokenizer_name=args.tokenizer_name,
        toml_out=Path(args.toml_out),
        tokenizer_config_out=Path(args.tokenizer_config_out),
        report_out=Path(args.report_out),
        template_config=Path(args.template_config) if args.template_config else None,
        vocab_size=args.vocab_size,
        model_type=args.model_type,
        max_sentence_length=args.max_sentence_length,
        num_threads=args.num_threads,
        input_sentence_size=args.input_sentence_size,
        shuffle_input_sentence=bool(args.shuffle_input_sentence),
        train_extremely_large_corpus=bool(args.train_extremely_large_corpus),
        effective_vocab_size=args.effective_vocab_size,
        train=bool(args.train),
        force=bool(args.force),
        status=str(args.status),
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    plan = parse_args(argv)
    failures, _warnings = run_plan(plan)
    print(plan.report_out.read_text(encoding="utf-8"))
    print(f"wrote_report: {plan.report_out}")
    if not failures:
        print(f"wrote_toml: {plan.toml_out}")
        print(f"wrote_tokenizer_config: {plan.tokenizer_config_out}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
