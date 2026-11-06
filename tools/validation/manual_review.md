# Manual review, 2026-11-05

Selection: `random.Random(20261105)`, 20 SQL IDs then 20 theory IDs,
recorded before reading the sample in `manual_sample.json`. Review compares
question, both formulations, explanation, schema and the observed dump limitations.
Execution agreement alone is not treated as semantic proof.

## SQL sample

| ID | Semantic finding |
| --- | --- |
| SQL3-017 | Correct: distinct categories, Beverages existence, >=2; NULL categories excluded from the count. |
| SQL3-088 | Correct: separately aggregates On Hold and unallocated sales lines; does not assert reconciliation. |
| SQL3-020 | Final review found incomplete lines could dilute the weighted rate. Excluded unknown quantity/price/discount from both sums; added an adversarial fixture. Now uses gross-value weighting, guarded denominator and final rounding. |
| SQL3-078 | Correct after pre-round-1 correction: empty invoice table produces one row of zeros; NULL due dates do not imply overdue. |
| SQL3-013 | Correct for dump: active suppliers only, minimum purchase-order count, all ties. No dangling supplier references observed. |
| SQL3-053 | Correct: reference set comes from lowest detail-bearing purchase order; coverage spans supplier history, ignores duplicate products. |
| SQL3-079 | Correct: invoice-weighted calendar delay, not order-weighted average; includes negative intervals if recorded. |
| SQL3-082 | Correct under explicit sign policy: Purchased positive, Sold/Waste negative, On Hold zero; not claimed as stock on hand. |
| SQL3-022 | Correct: needs sales details and no Waste. Same dump result as an ordered-only question, but a different predicate/intent. |
| SQL3-055 | Correct: empty ALL is TRUE including NULL left operands. Adversarial absent/nonempty reference fixtures pass. |
| SQL3-039 | Correct: price-sum share, not revenue share; category grouping and zero denominator are explicit. |
| SQL3-085 | Correct after pre-round-1 correction: sales links are all NULL; optional joins retain Sold movements rather than fabricate links. |
| SQL3-096 | Correct: distinct year-months, not months numbered 1-12; months need not be consecutive. |
| SQL3-098 | DEFECT FOUND: an employee with an in-quarter order without details could get NULL rather than zero. Adversarial fixture reproduced it. Fixed main with COALESCE around conditional sums; fixture rerun passes. Dump-only comparison had hidden it. |
| SQL3-059 | Correct: compares Standard Cost to unrounded own-category average, not List Price; ignores unknown costs. |
| SQL3-041 | Correct: fixed 2006-07-01 reference date, unshipped as NULL date, calendar age; reproducible rather than CURDATE. |
| SQL3-024 | Correct: missing invoice by NOT EXISTS or NULL nonnullable invoice ID, independent of payment or shipment. |
| SQL3-004 | Correct: supplier comes from purchase header, cost from details; window alternative retains same supplier/product grain. |
| SQL3-040 | Correct: previous dated order by date/ID; same-date gap zero; first gap NULL. MAX preceding timestamp agrees with LAG date. |
| SQL3-035 | Correct: shipping summed once per order, ROWS frame, date/ID tie-break, NULL fee zero. |

## Theory sample

| ID | Factual finding |
| --- | --- |
| TH3-058 | Checked dump type lookup: IDs map to Purchased, Sold, On Hold, Waste; inventory has no Status column. |
| TH3-022 | Midnight example produces calendar day 1 versus elapsed full days 0; business days explicitly excluded. |
| TH3-056 | Correct set-difference emulation needs DISTINCT and NULL-safe matching; EXCEPT unavailable on 8.0.28. |
| TH3-004 | NULL-safe equality truth table executes as stated. |
| TH3-032 | Correct: GROUP_CONCAT NULL omission, internal ORDER BY and length limit; not a lossless encoding. |
| TH3-053 | No fictitious version column added; optimistic concurrency is a design explanation, no executable schema mutation claimed. |
| TH3-005 | Corrected blanket NOT IN misconception: matching value is FALSE, unmatched plus NULL is UNKNOWN. Executed truth table. |
| TH3-031 | Correct token boundaries for semicolon supplier IDs; purchase history explicitly not substituted for catalogue relationships. |
| TH3-037 | Correct: nullable requirement semantics can differ between COUNT DISTINCT and double NOT EXISTS; exclusion/NULL-safe options stated. |
| TH3-012 | 8.0 documentation: IGNORE NULLS unsupported; LAG default applies to missing row, not an existing NULL value. Valid LAG example executed on 9.7.2, not 8.0.28. |
| TH3-055 | ROW_COUNT is connection-local/immediate-statement state; no-op UPDATE and rollback example executed without persistent writes. |
| TH3-011 | Correct anchor type-width and bounded recursion; tiny example executed, configured recursion limit independently queried. |
| TH3-036 | Correct first-branch names and final UNION ordering; runnable query executed. |
| TH3-025 | Correct distinction between empty input and all-NULL measures; counts accompany the example. |
| TH3-008 | Equal amounts example demonstrates SUM DISTINCT loses legitimate repeated observations. |
| TH3-060 | Correctly limits dump equivalence claims; empty results and server-version mismatch explicitly acknowledged. |
| TH3-018 | Keyset pagination needs unique tuple ordering and explicit NULL/update policy; does not claim snapshot isolation. |
| TH3-035 | JSON_TABLE available on 8.0.28; JSON null mapping changed in 8.0.21. Runnable null-element fixture passes on 9.7.2. |
| TH3-028 | PAD SPACE vs NO PAD comparison executes as 1 vs 0 for the named collations. |
| TH3-003 | Window rank filtered in outer query; no QUALIFY on 8.0.28. Example executed on 9.7.2. |

## Additional pre-round-1 review corrections

- Replaced a draft SQL3-045 average-delay exercise (overlapped A4-19) with median delay using independent order-statistic techniques.
- Replaced draft SQL3-048 prefix-count and SQL3-049 short-name exercises (overlapped LAB-23/A3-17) with suffix/ID diagnostics and final-word extraction.
- Replaced draft TH3-023 generic date-range advice (overlapped TH-21) with fractional-seconds precision.
- SQL3-025 changed April to May: April had no anti-join matches, May has one; no held-out case references this ID.
- SQL3-085/086 changed required header links to explicitly optional links because every inventory header link is NULL in this dump.
- TH3-015 renamed FIRST_VALUE/SECOND_VALUE draft column aliases after the server rejected them; examples now execute.
- SQL3-027 alternative changed from a near-mechanical pair join to grouped JSON_TABLE expansion, tested at a 10% boundary.
- The fixture runner initially compared Decimal repr strings (scale-sensitive). Fixed its comparison to numeric multisets before reproducing the genuine SQL3-098 defect; both initial outputs are retained.

No original bank question, answer, source text or held-out expectation was rewritten.

## Post-round-2 NULL follow-up

Schema inspection confirmed quantity, price and discount columns are nullable.
Added six paired fixtures before the final fresh build: SQL3-016/064 now
consistently display all-unknown quantity totals as zero under an explicit
diagnostic policy; SQL3-020/069 omit incomplete weighted observations;
SQL3-092 excludes unknown totals from the winner competition; SQL3-093 handles
unknown-revenue trailing rows without losing the accumulated known revenue.
TH3-053/054 now explicitly say no runnable example rather than implying examples
were executed. The prior dump-only passes did not expose these NULL edge cases.

The new SQL3-069 fixture also observed 5 rather than the expected 10 for a window
SUM ratio nested directly in NULLIF on this 9.7.2 server, while the unguarded
denominator returned 10. No upstream root cause or 8.0.28 behavior is claimed.
Computing window totals in a CTE before guarding/dividing them resolved the
fixture; SQL3-020 uses the same explicit two-stage evaluation.
