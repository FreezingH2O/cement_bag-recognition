# Dataset and split protocol

## 1. Current evidence and what is missing

The supplied `data/SampleMortarBag.zip` contains 592 JPEGs at 1408 x 1024. The reviewed subset appears to show a single blue/yellow DURA ONE design with consistent top-down framing. Exact SKU labels, physical-bag identities, trustworthy capture times, and coverage of other SKUs are not yet established. Do not assume that 592 files equal 592 independent bags, or that every file shows the same SKU.

Required for multi-SKU recognition: verified image-to-SKU labels, artwork for each enrolled SKU, and independent physical-bag/session groups. Required for OCR analysis: identifying-text regions and verified transcriptions. The existing camera and lighting remain in use for any additional data collection.

## 2. Two dataset levels

| Level | Proposed amount | Purpose and limit |
|---|---|---|
| Current-archive audit | All 592 files inventoried; inspect representative and difficult images | Crop, quality, deduplication, OCR feasibility; no unsupported multi-SKU accuracy |
| Small multi-SKU pilot | Prefer 6–8 SKUs including at least two visually similar pairs; target 50 independent test bags per SKU across at least 3 sessions | Compare approaches and find dominant failures; insufficient for broad factory acceptance |
| Full evaluation | Approximately 40 SKUs; target 100 independent final test bags per SKU across at least 3 later sessions | About 4,000 final queries, with additional independent development and validation data |

These are starting targets, not proof of statistical sufficiency. Count actual independent bags and sessions. If a SKU or adverse condition has few examples, report its sample size and wide uncertainty. One hundred examples per SKU provide a useful confusion analysis but weak precision around a 98% per-SKU result. Multiple factories/cameras are necessary before making cross-factory claims; the initial experiment can remain a single-camera study.

Proposed development data for a full study: 100 independent photos per training SKU for optional adaptation and 50 additional validation photos per training SKU; 50 validation photos per validation-only SKU. Final queries are separate from all these. For frozen-only experiments, a smaller development set can be sufficient to define cropping and validation policies, but final testing still needs broad coverage.

The pilot should withhold at least two identities for enrollment validation or testing when possible. With very few SKUs, use separate validation/test identities and label estimates exploratory. Never tune on all identities and then call them unseen.

## 3. Identity split for approximately 40 SKUs

| SKU group | Proposed count | Allowed use |
|---|---|---|
| `development_sku` | 24 | Training optional models; development artwork/photo analysis; separate validation and final sessions |
| `validation_only_sku` | 8 | Tune unseen-SKU enrollment behavior, OCR fusion, and rejection; never train model weights on their images/artwork |
| `final_unseen_sku` | 8 | Final artwork-only enrollment after pipeline freeze; camera photos withheld from development |

Assign groups using verified SKU metadata/artwork before inspecting final query results. Represent color/text variants in every group. Include a deliberate difficult subset where an unseen SKU has a visually similar enrolled neighbor; also report identities whose entire design family is held out when enough families exist. Record the grouping rationale and seed. A single 24/8/8 split is a starting design, not the only valid one.

Final evaluation includes fresh-session photos of all 40 SKUs. The eight final-unseen identities assess new-SKU generalization; fresh queries of the other 32 assess known identities and interference after gallery expansion. Validation-only identities remain unseen during weight training but have influenced policy selection, so they are not final-unseen identities.

## 4. Image/session split

Use `image_split` values `development_train`, `validation`, `final_test`, or `quarantine`. SKU roles are recorded separately. Example allowed combinations:

- Development SKU + development training session: `development_train`.
- Development SKU + separate validation session: `validation`.
- Validation-only SKU + validation session: `validation`.
- Any of the 40 SKUs + withheld later test session: `final_test`.
- Unverified identity, ambiguous duplicates, or corrupt file: `quarantine` until resolved.

Keep physical-bag groups and duplicate groups within one split. Also keep a production session within one split, including images of different SKUs in that session. If bag IDs are unavailable, conservatively group sequence blocks and near duplicates; document residual uncertainty. Missing metadata must remain missing rather than inventing factory/session IDs. An unresolved archive may be useful for smoke tests but not defensible independent evaluation.

Choose the primary query by the real capture contract: one auto-captured image per bag when guaranteed, otherwise the first eligible trigger established without seeing model predictions. Retain alternate captures for a separately reported sensitivity study. Do not choose the sharpest image using ground-truth knowledge. Split real bags before generating crops, augmentations, or synthetic corruptions.

## 5. Gallery and enrollment rules

Store SKU ID, official product name, artwork revision, visible side, visible panel paths, distinguishing text/codes, design-family ID, and SKU role. Different artwork revisions belonging to the same SKU are handled explicitly; a new revision is not automatically a new SKU. Investigate camera photos showing an unregistered artwork revision separately.

Use the same policy for every SKU: all confirmed camera-visible panels up to a declared cap, with a consistent crop/preparation procedure. Record any generated views and their fixed recipe. Reference-count asymmetry can affect max similarity, so do not give difficult test SKUs extra views after seeing failures.

For final unseen SKUs, only artwork and verified metadata are revealed after selection. Their camera photos remain test queries. Their artwork must not be used for contrastive training, augmentation-policy selection, or visual region tuning. Applying an already frozen panel-extraction/view recipe at enrollment is allowed. Verify that model/config hashes stay fixed across pre/post enrollment; only gallery and text-registry versions change.

The pre-enrollment final gallery contains the 32 non-final-unseen SKUs. The expanded gallery contains all 40. Run the same final queries under both gallery states and report their different intended meanings. Validate unknown rejection using analogous withheld validation identities before this challenge; changing final thresholds would invalidate the held-out result.

For the optional 1/5-photo gallery comparison, collect separate enrollment photos from independent bags and sessions. Add them only after the primary artwork-only evaluation is locked. Test query photos never become reference photos.

## 6. Annotation instructions

Verify SKU identity using reliable production/product records where available, rather than a model guess. Have a second reviewer check similar-looking SKUs and disagreements. Record the label source and adjudication status.

Annotate these image attributes independently:

- Bag fully visible, partial bag, multiple bags, or no bag.
- Image unusable/corrupt, with reason; still retain it for relevant end-to-end denominators.
- Visible low brightness and uneven illumination: `normal`, `moderate`, `severe`, or `unknown`, using reference examples defined from development images.
- Noise, blur, small text, folds, glare, airborne haze, lens/window contamination, and print occlusion: separate tags, with `unknown` when cause cannot be established.
- Human readability of SKU-distinguishing print: `readable`, `partly_readable`, `unreadable`, or `unknown`.

Human readability and difficulty tags are for analysis only, not model inputs or automatic acceptance rules. Models must estimate their own quality indicators from pixels.

For OCR, label identifying text polygons in full-image coordinates and mark whether the content is readable. Record language, transcription, SKU-critical field, and whether it is shared-brand or distinguishing text. Preserve Thai marks and meaningful numbers. Use approved artwork to verify intended field content when possible, but do not claim that completely hidden text is visibly readable. Evaluate character accuracy only where transcription can be established; separately report all-bag ability to recover the required identifying field, including unreadable/missing fields.

If camera capture time is unavailable or a filename contains a placeholder clock value, leave it blank. File creation time is not necessarily capture time. Store hashes to detect file changes; raw source files remain read-only.

## 7. Balanced and production-weighted evaluation

Maintain a balanced SKU test for fair comparisons, and report per-SKU recall and macro averages. Also report production-weighted performance only when actual SKU frequencies are known. The balanced set cannot establish real traffic frequencies. Conditions may overlap and must not be summed as though they partition the dataset.

Prefer genuine naturally dark/dusty samples across several SKUs and sessions. Do not create a low-light subset containing only one SKU and then attribute every performance difference to illumination. Report condition × SKU sample counts and acknowledge confounding that cannot be resolved.

## 8. Data files and final checks

Use the [CSV template descriptions](/Users/airadajitauleeruk/Desktop/capstone/experiment/templates/README.md) for the registry, image manifest, and OCR labels. Use project-relative paths in machine-readable records for portability; resolve them against the project root. Store non-ASCII text as UTF-8 and quote CSV fields containing commas or line breaks.

Before a run, confirm that identities/physical bags/session groups do not cross forbidden boundaries, no test query is a reference, final unseen SKUs are absent from all training inputs, and raw/derived images retain their source IDs. Save the split manifest before training and keep it identical across comparative runs.
