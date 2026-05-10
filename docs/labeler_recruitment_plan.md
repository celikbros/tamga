# Labeler Recruitment Plan

Status: operational plan  
Date: 2026-05-10  
Scope: hidden eval labeling only

## Goal

Find one suitable annotator for the first hidden eval round and start the
calibration workflow without exposing hidden examples to the implementer.

This is a process document, not a tokenizer design document.

## Who Is Suitable?

Preferred profile:

- native Turkish speaker
- has not read the project design docs
- preferably has linguistics, Turkish language, morphology, or NLP background
- comfortable editing TSV or spreadsheet-like files
- willing to follow a privacy protocol

Acceptable first-round candidates:

- Turkish linguistics student
- Turkish language/literature student with morphology awareness
- NLP researcher/student familiar with Turkish
- professional annotator with Turkish morphology guidance
- advisor-recommended reviewer

Avoid:

- someone who has already read the tokenizer rules in detail
- someone who will discuss hidden examples directly with the implementer
- someone unavailable for calibration review

## Estimated Time

```text
guideline reading:     ~30 minutes
5-item calibration:    ~30 minutes
40 hidden examples:    ~120 minutes
total:                 ~3 hours
```

The task should not be framed as a tiny favor.

## Recruitment Channels

Practical order:

1. Advisors' university contacts.
2. Turkish linguistics or NLP students.
3. NLP/Turkish language community contacts.
4. Freelance annotation only if an advisor can still review calibration.

For the first round, one annotator is enough. v1.5 can add a second annotator
and inter-annotator agreement.

## What To Send First

Send:

- `docs/hidden_eval_request_message.md`
- `docs/hidden_eval_labeler_packet.md`
- `docs/hidden_eval_labeling_guideline.md`
- `data/eval/templates/tr_hidden_eval_template.tsv`

Do not send:

- tokenizer implementation details
- private hidden rows from another annotator
- challenge mismatch examples as labeling targets

## First Contact Message

```text
Merhaba,

Turkce merkezli bir tokenizer arastirma prototipi icin kucuk bir hidden eval
etiketleme calismasi baslatmak istiyoruz.

Isin amaci, tokenizer'a yeni kural eklemeden once sistemin daha once gormedigi
Turkce orneklerde nasil davrandigini olcmek.

Beklenen is:

- Once hidden setten ayri 5 kalibrasyon ornegi etiketlenecek.
- Kalibrasyon bir danisman/ikinci goz tarafindan kontrol edilecek.
- Kalibrasyon uygunsa ayrica 40 hidden ornek hazirlanacak.
- Hidden ornekler public GitHub reposuna konmayacak.
- Gelistirici hidden cumleleri gormeyecek.
- Mumkunse sadece aggregate metrikler paylasilacak.

Tahmini sure: yaklasik 3 saat.

Eger uygunsa once kisa yonerge ve template dosyalarini paylasip 5 kalibrasyon
ornegiyle baslamak isteriz.
```

## Screening Questions

Before starting, ask:

1. Are you a native Turkish speaker?
2. Have you read the tokenizer implementation or design docs? If yes, tell us
   which parts.
3. Do you have linguistics, Turkish morphology, or NLP annotation experience?
4. Are you comfortable working with TSV/JSON-list fields?
5. Can you keep the hidden examples private and avoid sharing them with the
   implementer?

If the answer to question 2 is "yes, in detail", prefer another annotator for
the hidden set.

## Calibration Workflow

1. Annotator prepares 5 separate calibration rows.
2. Advisor or second reviewer checks them privately.
3. Apply the threshold:

| Calibration result | Action |
| --- | --- |
| 5/5 accepted | Proceed to the 40 hidden examples. |
| 3-4/5 accepted | Discuss failed rows privately, correct the issue, then proceed if the reviewer is satisfied. |
| 0-2/5 accepted | Revise the guideline or examples, then request a fresh 5-example calibration batch. |

Calibration examples must not enter the 40 hidden examples.

## Deliverables

Private deliverable:

```text
data/eval/private/tr_hidden_eval.tsv
```

Public/implementer-facing deliverable:

```text
artifacts/v1_3_hidden_eval_report.md
```

The public report must be aggregate-only. It should include:

- overall policy exact/F1
- overall independent exact/F1
- category-level policy F1
- category-level independent F1
- high-level concerns without hidden examples

It must not include:

- hidden sentences
- expected token lists
- mismatch examples
- screenshots that reveal rows

## Compensation / Credit Options

Choose one before asking the annotator:

- paid annotation
- advisor/internal project contribution
- acknowledgement in future report
- co-author discussion only if contribution grows beyond annotation

Do not leave this ambiguous if the annotator is outside the immediate team.

## Next Operational Step

Select one candidate and send `docs/hidden_eval_request_message.md`.

If no candidate is available, ask advisors for one Turkish linguistics/NLP
student who can do a 3-hour private annotation task with calibration review.
