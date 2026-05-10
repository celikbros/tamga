# How To Interpret Reviewer Responses

This guide shows how to convert professor/student responses into project
actions without overreacting.

## Response Types

| Response type | Meaning | Action |
| --- | --- | --- |
| Confirms current strategy | The layer order and non-goals are reasonable. | Keep docs, record reviewer signal. |
| Flags v2.0 risk | A future decision may become costly if delayed. | Add to v2.0 backlog or irreversibility flags. |
| Provides smoke examples | Reviewer gives public examples. | Add later to multilingual smoke candidates, not hidden eval. |
| Requests v1.x fix | Reviewer wants current behavior fixed. | Usually defer unless it is a Turkish regression. |
| Contradicts another reviewer | Different language/script needs conflict. | Keep decision open; do not freeze vocabulary/normalization. |

## What To Update

If a reviewer gives useful multilingual/Turkic feedback, update one or more:

```text
docs/multilingual_strategy.md
docs/multilingual_observations.md
docs/multilingual_reviewer_response_form.md
docs/advisor_brief.md
```

For actual public smoke examples, create a future file such as:

```text
data/eval/multilingual_smoke_candidates.tsv
```

Only do this after confirming that examples are public and not from a restricted
corpus.

## What Not To Do

- Do not treat multilingual smoke issues as v1.x regressions.
- Do not add language detection immediately.
- Do not generalize Turkish apostrophe rules to all Turkic languages.
- Do not lock vocabulary allocation because one reviewer suggested examples.
- Do not mix Turkish hidden eval rows with multilingual smoke examples.

## Example Interpretation

Reviewer says:

```text
`ə` must be treated as a normal Azerbaijani letter before vocabulary training.
```

Interpretation:

```text
Add to v2.0 irreversibility flags and script-aware pretokenizer backlog.
Do not implement a quick v1.x Azerbaijani morphology rule.
```

Reviewer says:

```text
O'Connor should not be treated as Turkish apostrophe+suffix behavior.
```

Interpretation:

```text
Add to European/multilingual apostrophe observations.
Consider a future guard so Turkish apostrophe logic only fires on Turkish suffix
inventory. Do not make it v1.4 work.
```

Reviewer says:

```text
README.md must be protected before any morphology.
```

Interpretation:

```text
This confirms the cross-language protection layer must come before Turkish or
Turkic morphology.
```

## Minimal Summary To Send Back To Reviewer

```text
Thank you, this is useful. We will record your points as v2.0 architecture
constraints rather than immediate v1.x fixes. In particular, we will keep
vocabulary allocation open until script-aware pretokenization, cross-language
protection, and byte fallback are specified.
```
