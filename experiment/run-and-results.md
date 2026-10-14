# Run, metrics, and result reporting

## 1. A reproducible run

Each run needs an immutable run ID, experiment ID, dataset/split versions, gallery version, exact model/checkpoint hashes, preprocessing and orientation settings, image resolution, score aggregation, OCR/fusion rules, rejection thresholds, software versions, device, and seed. Store these alongside predictions, not just in a notebook's current state.

Proposed layout when experiments are implemented:

```text
experiment/
  README.md
  experiment-plan.md
  data-protocol.md
  run-and-results.md
  templates/
  runs/<run_id>/
    config.json
    predictions.csv
    metrics.json
    confusion-matrix.csv
    condition-metrics.csv
    error-review.md
```

The `runs` files above are future outputs; they are not created results. Use three seeds for training finalists. Frozen inference usually needs one deterministic accuracy run; repeat timings to characterize runtime variance. Do not treat training seeds as independent test bags.

## 2. Sequence and model selection

1. Lock raw inventory, labels, SKU roles, and grouped image splits.
2. Run the baseline and ablations on validation only. Save per-image predictions so comparisons are paired.
3. Inspect validation errors: wrong crop/orientation; shared logo; text difference; illumination/noise; blur/resolution; occlusion; wrong artwork revision; bad label; unknown SKU; or unexplained failure.
4. Choose the simplest pipeline with the best validation all-bag identification and acceptable unknown false acceptance/runtime. Set a proposed practical tie rule before selection: prefer the simpler/faster method if the gain is under 0.5 percentage points and paired uncertainty includes zero. The 0.5-point rule is an engineering preference, not the project target.
5. Freeze all settings, including thresholds and OCR fallback. Record hashes.
6. Execute pre/post artwork enrollment, the full final test, robustness challenges, and runtime replay. Do not choose a different winner after inspecting final errors.
7. Report conclusions and unresolved limits. A changed model after final-test inspection needs a new untouched test set for a new acceptance claim.

Score threshold and top-two distinct-SKU margin should be selected together. Use validation known/withheld-SKU queries and report the tradeoff between coverage and false acceptance. A proposed development goal is unknown-SKU false acceptance at most 1%; this is an additional experimental criterion, not a requirement stated in the original scope. When unknown data is too limited, report counts and uncertainty instead of claiming that goal is established.

## 3. Primary metrics and denominators

Let `N` be the number of independent final bag queries whose true SKU is enrolled in the gallery for that pass. Retain unreadable, partial, or rejected eligible bag captures in `N`. Corrupt/missing images count as processing failures if they are part of the agreed production capture contract; report data-ingestion errors separately too. No-bag queries belong in their own negative-input category.

| Metric | Definition |
|---|---|
| Automatic identification accuracy | Correct accepted SKU decisions / `N`; uncertainty and unusable outputs contribute no correct identification |
| Forced top-1 retrieval accuracy | Correct highest-ranked SKU / `N`, irrespective of acceptance; pipeline failures count as wrong |
| Top-3 candidate recall | Queries with correct SKU among three distinct candidates / `N` |
| Accepted-only accuracy | Correct accepted decisions / all accepted enrolled-bag decisions; undefined if none accepted |
| Coverage | Accepted enrolled-bag decisions / `N` |
| Wrong acceptance rate | Incorrect accepted enrolled-bag decisions / `N` |
| Per-SKU recall | Correct accepted decisions for that SKU / its eligible bag queries |
| Macro recall | Mean per-SKU recall across evaluated SKUs |
| Unknown false acceptance rate | Unenrolled-SKU queries accepted as any enrolled SKU / all unenrolled-SKU queries |
| No-bag false acceptance | No-bag inputs assigned a SKU / all no-bag inputs; separate from unknown-SKU rate |

Do not call a top-3 match or a correct uncertainty output successful enrolled-SKU identification. Unknown queries are not mixed into the enrolled accuracy denominator. Separately report `recognized`, `uncertain`, `unusable_image`, and processing-error counts.

Produce a confusion matrix with uncertainty/unusable/error output columns, not just accepted predictions. Report balanced overall, per-SKU, known identity, final unseen identity, and real-condition subgroup results. Show before/after gallery expansion for existing SKUs. Also include raw counts; percentages on tiny groups can mislead.

## 4. OCR metrics

- **Identifying-text detection recall:** matched annotated identifying text regions / all eligible identifying regions. Fix polygon-IoU matching, initially `0.5`, and one-to-one assignment on validation. Report detection precision as well so large boxes are not rewarded indiscriminately.
- **Character error rate:** `(substitutions + deletions + insertions) / ground-truth character count`, with fixed Unicode normalization. Aggregate edit counts rather than averaging strings of different lengths blindly. CER can exceed 100%. State whether a character means Unicode code point or grapheme cluster; use NFC code-point CER plus exact field accuracy initially, and optionally add Thai grapheme analysis.
- **Exact field accuracy:** correctly recovered product name/grade/code / eligible verified fields, under the documented normalization. Missing detections count as failed recovery. Keep readable-field analysis separate from all-bag field recovery.
- **Critical code errors:** report incorrect digits/grades separately, since a small string error can change SKU identity.
- **Final SKU gain:** combined automatic identification accuracy minus visual-only accuracy on the identical bags, with counts of visual errors fixed and new errors introduced.

Publish diagnostic recognition on verified crops separately from the automatic detector+recognizer result. Report OCR invocation frequency and added latency for selective OCR. Keep untranscribable text out of CER, but report how many bags contain it and whether the complete system identifies those bags.

## 5. Uncertainty and statistical reporting

Report 95% confidence intervals for key proportions and paired accuracy differences. For genuinely independent bag outcomes, Wilson intervals are a reasonable descriptive starting point. Factory images often share session effects; use paired session-cluster bootstrap intervals for method comparisons when enough sessions exist, and keep all outcomes of one bag together. Report the number of sessions and bags. With very few sessions, avoid strong significance/generalization claims regardless of image count.

Synthetic variants are paired stress probes, not extra independent test samples. Compare methods using the same underlying bags, transformations, and seeds. For trained models, report mean/range across seeds separately from sampling uncertainty. Do not select the best test seed.

## 6. Acceptance and conclusions

| Claim | Evidence required |
|---|---|
| Meets the project's recognition target on the tested population | At least 98% automatic identification accuracy over all eligible enrolled test bags, with coverage/counts and confidence intervals |
| Strong evidence that accuracy exceeds the target | Predeclared one-sided 95% lower confidence bound above 98%, using an analysis appropriate to grouping; this is stronger than the scope's point target |
| Supports artwork-only new-SKU enrollment | Separate final-unseen accuracy; no final identity training/calibration; fixed weights/config before gallery update |
| Handles current low-light conditions | Performance and failures on real low-light bags across SKUs/sessions; synthetic results reported separately |
| Meets end-to-end latency limit | Reliable capture-to-result measurement within the scope's 60-second limit; mean, p95, p99, maximum, and fraction over 60 seconds |
| Keeps up with production | Sustainable throughput at measured production arrival rate and acceptable queue behavior |
| Works across factories | Independent factory/camera holdouts; a single-camera study cannot establish this |

The original scope does not specify a confidence-bound acceptance rule or a separate 98% threshold for unseen/low-light subgroups. Still report those subgroup results, since strong overall performance can hide failures central to this module. Label additional criteria as proposed, and state the tested population precisely.

If the target is missed, classify the cause using observed errors and estimate the benefit of the next software experiment. If only rejection makes accepted-only accuracy high, report the resulting coverage and all-bag shortfall. Do not declare success by removing difficult cases after the run.

## 7. Runtime metrics

Report crop/preprocessing, visual encoding, search, OCR, fusion, queue delay, worker processing, and end-to-end times. Include device, batch size, memory, cold-start behavior, and invocation mix. For an arrival rate `lambda` images/second, a sustainable service rate must exceed `lambda`; average service time alone is insufficient when bursts or conditional OCR create queues. State any simulated input-rate assumption.

Image IDs/event IDs must map correctly to results. Duplicate-trigger identification is an integration observation, not a claimed counting solution. No timestamps means no verified capture-to-result measurement; report the timing portions actually observed.

## 8. Report outline

For each experiment, record: question; data and split; control and changed factor; config/version; accuracy with denominator; subgroup results; uncertainty; runtime; representative errors; and decision. Use the blank [run summary template](/Users/airadajitauleeruk/Desktop/capstone/experiment/templates/run-summary.csv).

The final comparison should show at least:

| Method | Enrollment | All-bag accuracy | Unseen-SKU accuracy | Real low-light accuracy | Coverage | Unknown false acceptance | p95 latency |
|---|---|---|---|---|---|---|---|
| Frozen visual baseline | Artwork only | Not run | Not run | Not run | Not run | Not run | Not run |
| Selected visual + preprocessing | Artwork only | Not run | Not run | Not run | Not run | Not run | Not run |
| Visual + OCR | Artwork + verified artwork text | Not run | Not run | Not run | Not run | Not run | Not run |
| Adapted encoder, if required | Artwork only after one-time development training | Not run | Not run | Not run | Not run | Not run | Not run |
| Photo-assisted, optional | Artwork + 1/5 separate photos | Not run | Not run | Not run | Not run | Not run | Not run |

Include all unsuccessful ablations in an appendix so the report explains why the final architecture was chosen.
