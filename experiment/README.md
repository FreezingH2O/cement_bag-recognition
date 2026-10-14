# Cement-bag recognition experiments

Designed on 11 October 2026 from the project scope, reviewed sample images, research review, and the user's software-first decision. This is an experiment design; no models have been trained or evaluated under this plan yet.

**Main question:** Can an auto-captured cement-bag photo be matched to the correct SKU, including a newly enrolled SKU represented only by artwork, under the existing camera and lighting conditions?

The input is the current camera's JPEG image. The output is a SKU with supporting evidence, or `uncertain` / `unusable_image`. Additional lighting and new camera hardware are outside this phase. Counting, defect detection, production control, and deployment are outside this recognition experiment, except for checking that recognition outputs preserve image/event identity.

## Read these files in order

1. [Experiment plan](/Users/airadajitauleeruk/Desktop/capstone/experiment/experiment-plan.md): hypotheses, architecture, experiment matrix, and decision gates.
2. [Data protocol](/Users/airadajitauleeruk/Desktop/capstone/experiment/data-protocol.md): pilot and full datasets, labels, splits, and artwork-only enrollment rules.
3. [Run and results protocol](/Users/airadajitauleeruk/Desktop/capstone/experiment/run-and-results.md): reproducibility, metrics, reporting, and acceptance criteria.

The editable CSV templates are in [templates](/Users/airadajitauleeruk/Desktop/capstone/experiment/templates/README.md). They contain headers only; no sample rows should be mistaken for collected data or measured results.

## Recommended starting point

Audit the supplied 592-image ZIP and obtain verified matching artwork and SKU labels. Establish a fixed bag crop and a frozen DINOv2 artwork-gallery baseline. Compare DINOv3 and a SIFT baseline on the same validation images. Add pretrained Thai OCR only after measuring the visual baseline's actual confusions. Compare original images with simple software exposure correction before trying learned enhancement.

Use the smallest experiment that answers the current failure: do not implement every reviewed paper. MAET and FeatEnHancer supply ideas for an optional development-training experiment; their detection networks are not assumed to be ready-made SKU recognizers.

## The decisive evaluation

Select the pipeline using development and validation data. Freeze its weights, preprocessing, fusion rules, and acceptance thresholds. Then add held-out SKU artwork and verified text metadata to the gallery, without training on their camera photos. Evaluate on unseen real bags. Report all-bag recognition accuracy, uncertainty coverage, unknown-SKU false acceptance, and latency together.

The project's SKU accuracy target is **at least 98%**. This plan counts rejected or unusable enrolled bags as failures to identify a bag automatically. Accepted-only accuracy is reported separately. The target is a requirement to test, not a performance prediction.

Research background: [cement-bag recognition review](/Users/airadajitauleeruk/Desktop/capstone/output/research/cement-bag-recognition-research.md). All dataset sizes, tuning grids, and optional acceptance criteria in this folder are proposed engineering choices, not findings from the papers or an imposed project timeline.
