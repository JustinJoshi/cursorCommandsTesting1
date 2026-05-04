"""
Evaluation runner for the extraction pipeline.

Usage:
    python -m backend.evals.run_eval --model qwen2.5vl:7b
    python -m backend.evals.run_eval --model gpt-4o --backend openai
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.evals.metrics import aggregate_results, evaluate_listing

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GROUND_TRUTH_DIR = Path(__file__).parent / "ground_truth"
RESULTS_DIR = Path(__file__).parent / "results"


def load_ground_truth() -> list[tuple[Path, list[dict[str, Any]]]]:
    """Load all ground truth pairs (screenshot + expected JSON)."""
    pairs = []
    json_files = sorted(GROUND_TRUTH_DIR.glob("*.json"))

    for json_file in json_files:
        image_file = json_file.with_suffix(".png")
        if not image_file.exists():
            image_file = json_file.with_suffix(".jpg")
        if not image_file.exists():
            logger.warning("No image found for %s, skipping", json_file.name)
            continue

        with open(json_file) as f:
            expected = json.load(f)

        if isinstance(expected, dict):
            expected = [expected]

        pairs.append((image_file, expected))

    return pairs


def match_listings(
    predicted: list[dict[str, Any]], expected: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Match predicted listings to expected listings by best title similarity."""
    from rapidfuzz import fuzz

    matched = []
    used_pred_indices: set[int] = set()

    for exp in expected:
        best_score = 0.0
        best_idx = -1

        for i, pred in enumerate(predicted):
            if i in used_pred_indices:
                continue
            score = fuzz.ratio(
                (pred.get("title") or "").lower(),
                (exp.get("title") or "").lower(),
            )
            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx >= 0 and best_score > 50:
            matched.append((predicted[best_idx], exp))
            used_pred_indices.add(best_idx)
        else:
            matched.append(({}, exp))

    return matched


async def run_evaluation(backend: str = "ollama", model: str | None = None) -> dict[str, Any]:
    """Run full evaluation against ground truth dataset."""
    pairs = load_ground_truth()
    if not pairs:
        logger.error("No ground truth data found in %s", GROUND_TRUTH_DIR)
        logger.info("Add screenshot PNGs and corresponding JSON files to get started.")
        return {"error": "No ground truth data"}

    if backend == "openai":
        from backend.extraction.openai_vision import OpenAIVisionExtractor
        extractor = OpenAIVisionExtractor()
    else:
        from backend.extraction.qwen_local import QwenLocalExtractor
        extractor = QwenLocalExtractor()

    model_name = extractor.get_model_name()
    logger.info("Running eval with model: %s", model_name)
    logger.info("Ground truth pairs: %d", len(pairs))

    all_results = []
    valid_json_count = 0
    total_expected = 0
    total_predicted = 0

    for image_path, expected_listings in pairs:
        logger.info("Processing: %s", image_path.name)

        try:
            predicted_listings = await extractor.extract_listings(image_path)
            valid_json_count += 1
        except Exception as e:
            logger.error("Extraction failed for %s: %s", image_path.name, e)
            predicted_listings = []

        total_expected += len(expected_listings)
        total_predicted += len(predicted_listings)

        matched = match_listings(predicted_listings, expected_listings)

        for pred, exp in matched:
            result = evaluate_listing(pred, exp)
            result["source_file"] = image_path.name
            all_results.append(result)

    aggregated = aggregate_results(all_results)
    aggregated["valid_json_rate"] = valid_json_count / len(pairs) if pairs else 0
    aggregated["recall"] = total_predicted / total_expected if total_expected > 0 else 0
    aggregated["model_name"] = model_name
    aggregated["timestamp"] = datetime.utcnow().isoformat()
    aggregated["ground_truth_files"] = len(pairs)

    overall = (
        aggregated.get("price_accuracy", 0) * 0.3
        + aggregated.get("year_accuracy", 0) * 0.2
        + aggregated.get("model_accuracy", 0) * 0.15
        + aggregated.get("avg_description_rouge", 0) * 0.1
        + aggregated.get("link_extraction_rate", 0) * 0.1
        + aggregated.get("valid_json_rate", 0) * 0.15
    )
    aggregated["overall_score"] = round(overall, 4)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"eval_{timestamp_str}_{backend}.json"
    with open(result_file, "w") as f:
        json.dump(aggregated, f, indent=2)

    logger.info("=" * 60)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 60)
    logger.info("Model:               %s", model_name)
    logger.info("Ground truth files:  %d", len(pairs))
    logger.info("Listings evaluated:  %d", len(all_results))
    logger.info("-" * 60)
    logger.info("Price accuracy:      %.1f%%", aggregated.get("price_accuracy", 0) * 100)
    logger.info("Year accuracy:       %.1f%%", aggregated.get("year_accuracy", 0) * 100)
    logger.info("Model accuracy:      %.1f%%", aggregated.get("model_accuracy", 0) * 100)
    logger.info("Description ROUGE-L: %.3f", aggregated.get("avg_description_rouge", 0))
    logger.info("Link extraction:     %.1f%%", aggregated.get("link_extraction_rate", 0) * 100)
    logger.info("Valid JSON rate:      %.1f%%", aggregated.get("valid_json_rate", 0) * 100)
    logger.info("Recall:              %.1f%%", aggregated.get("recall", 0) * 100)
    logger.info("-" * 60)
    logger.info("OVERALL SCORE:       %.1f%%", overall * 100)
    logger.info("=" * 60)
    logger.info("Results saved to: %s", result_file)

    return aggregated


def main():
    parser = argparse.ArgumentParser(description="Run extraction evaluation")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", type=str, default=None, help="Override model name")
    args = parser.parse_args()

    asyncio.run(run_evaluation(backend=args.backend, model=args.model))


if __name__ == "__main__":
    main()
