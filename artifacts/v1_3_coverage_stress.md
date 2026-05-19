# Coverage Telemetry Report

Tokenizer behavior is not changed by this report.

## SUMMARY

- examples: 28
- tokens: 304
- avg_tokens_per_example: 10.8571

## TOKEN KIND COUNTS

| token_kind | count | share |
| --- | ---: | ---: |
| suffix | 43 | 0.1414 |
| apostrophe | 10 | 0.0329 |
| protected_url | 2 | 0.0066 |
| protected_file | 7 | 0.0230 |
| protected_number | 8 | 0.0263 |
| word | 86 | 0.2829 |
| punctuation_symbol | 54 | 0.1776 |
| other | 94 | 0.3092 |

## CATEGORY SUMMARY

| category | examples | tokens | avg_tokens | suffix | protected | word | punctuation_symbol | other |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 1 | 7 | 7.00 | 3 | 0 | 3 | 1 | 0 |
| azerbaijani | 2 | 34 | 17.00 | 5 | 0 | 17 | 5 | 7 |
| code_like | 1 | 13 | 13.00 | 0 | 2 | 5 | 6 | 0 |
| code_mixed | 1 | 9 | 9.00 | 4 | 0 | 3 | 1 | 0 |
| english_apostrophe | 1 | 9 | 9.00 | 2 | 0 | 4 | 1 | 0 |
| english_passthrough | 1 | 9 | 9.00 | 0 | 2 | 6 | 1 | 0 |
| european_apostrophe | 1 | 6 | 6.00 | 1 | 0 | 3 | 1 | 0 |
| informal | 2 | 9 | 4.50 | 4 | 0 | 3 | 2 | 0 |
| kazakh_cyrillic | 1 | 35 | 35.00 | 0 | 0 | 0 | 2 | 33 |
| kyrgyz_cyrillic | 1 | 31 | 31.00 | 0 | 0 | 0 | 6 | 25 |
| negative_word | 1 | 5 | 5.00 | 0 | 0 | 4 | 1 | 0 |
| numbers_dates | 3 | 23 | 7.67 | 8 | 4 | 7 | 3 | 0 |
| protected_file | 2 | 16 | 8.00 | 7 | 2 | 4 | 2 | 0 |
| protected_file_date | 1 | 6 | 6.00 | 1 | 2 | 2 | 1 | 0 |
| protected_url | 1 | 7 | 7.00 | 1 | 1 | 4 | 1 | 0 |
| punctuation_mixed | 1 | 7 | 7.00 | 1 | 0 | 4 | 2 | 0 |
| punctuation_unicode | 1 | 7 | 7.00 | 1 | 0 | 2 | 4 | 0 |
| tatar_cyrillic | 1 | 36 | 36.00 | 0 | 0 | 0 | 7 | 29 |
| turkish_apostrophe | 1 | 9 | 9.00 | 3 | 1 | 2 | 1 | 0 |
| turkish_i_case | 1 | 10 | 10.00 | 2 | 0 | 5 | 1 | 0 |
| url_code_mixed | 1 | 4 | 4.00 | 0 | 3 | 1 | 0 | 0 |
| uzbek_apostrophe | 2 | 12 | 6.00 | 0 | 0 | 7 | 5 | 0 |

## OTHER TOKEN EXAMPLES

- category: `azerbaijani`
  text: `Mənim adım Əli, Bakıda yaşayıram.`
  other_tokens: `['ə', 'Ə']`
- category: `azerbaijani`
  text: `Xəbər: qız məktəbə gedir, dağ yolu uzundur.`
  other_tokens: `['ə', 'ə', 'ə', 'ə', 'ə']`
- category: `kazakh_cyrillic`
  text: `Қазақстан Республикасы — Алматы қаласы.`
  other_tokens: `['Қ', 'а', 'з', 'а', 'қ', 'с', 'т', 'а', 'н', 'Р', 'е', 'с', 'п', 'у', 'б', 'л', 'и', 'к', 'а', 'с', 'ы', 'А', 'л', 'м', 'а', 'т', 'ы', 'қ', 'а', 'л', 'а', 'с', 'ы']`
- category: `kyrgyz_cyrillic`
  text: `Кыргызча: тоо, суу, өң, үн, жаңы күн.`
  other_tokens: `['К', 'ы', 'р', 'г', 'ы', 'з', 'ч', 'а', 'т', 'о', 'о', 'с', 'у', 'у', 'ө', 'ң', 'ү', 'н', 'ж', 'а', 'ң', 'ы', 'к', 'ү', 'н']`
- category: `tatar_cyrillic`
  text: `Татарча: әни, җил, күңел, өч, үрдәк, һава.`
  other_tokens: `['Т', 'а', 'т', 'а', 'р', 'ч', 'а', 'ә', 'н', 'и', 'җ', 'и', 'л', 'к', 'ү', 'ң', 'е', 'л', 'ө', 'ч', 'ү', 'р', 'д', 'ә', 'к', 'һ', 'а', 'в', 'а']`
