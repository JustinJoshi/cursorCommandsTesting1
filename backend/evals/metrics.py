from typing import Any, Optional

from rapidfuzz import fuzz


def exact_match(predicted: Any, expected: Any) -> bool:
    """Check if two values are exactly equal."""
    if predicted is None and expected is None:
        return True
    if predicted is None or expected is None:
        return False
    return predicted == expected


def numeric_match(predicted: Any, expected: Any, tolerance: float = 0.0) -> bool:
    """Check if two numeric values match within tolerance."""
    if predicted is None and expected is None:
        return True
    if predicted is None or expected is None:
        return False
    try:
        p = float(predicted)
        e = float(expected)
        if tolerance == 0:
            return p == e
        return abs(p - e) <= tolerance
    except (ValueError, TypeError):
        return False


def fuzzy_match(predicted: Optional[str], expected: Optional[str], threshold: float = 0.9) -> float:
    """Return fuzzy match score between 0 and 1. Score >= threshold counts as match."""
    if predicted is None and expected is None:
        return 1.0
    if predicted is None or expected is None:
        return 0.0
    score = fuzz.ratio(predicted.lower().strip(), expected.lower().strip()) / 100.0
    return score


def rouge_l_score(predicted: Optional[str], expected: Optional[str]) -> float:
    """Compute ROUGE-L F1 score between predicted and expected text."""
    if predicted is None and expected is None:
        return 1.0
    if predicted is None or expected is None:
        return 0.0

    pred_tokens = predicted.lower().split()
    exp_tokens = expected.lower().split()

    if not pred_tokens or not exp_tokens:
        return 0.0

    lcs_len = _lcs_length(pred_tokens, exp_tokens)
    precision = lcs_len / len(pred_tokens) if pred_tokens else 0
    recall = lcs_len / len(exp_tokens) if exp_tokens else 0

    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return f1


def _lcs_length(a: list[str], b: list[str]) -> int:
    """Compute length of longest common subsequence."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def evaluate_listing(predicted: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a single predicted listing against ground truth."""
    results = {}

    results["price_correct"] = numeric_match(
        predicted.get("price"), expected.get("price")
    )

    results["year_correct"] = exact_match(
        predicted.get("year"), expected.get("year")
    )

    results["model_score"] = fuzzy_match(
        predicted.get("model"), expected.get("model"), threshold=0.9
    )
    results["model_correct"] = results["model_score"] >= 0.9

    results["trim_score"] = fuzzy_match(
        predicted.get("trim"), expected.get("trim"), threshold=0.85
    )

    results["description_rouge"] = rouge_l_score(
        predicted.get("description"), expected.get("description")
    )

    results["link_extracted"] = predicted.get("link_text") is not None

    results["title_score"] = fuzzy_match(
        predicted.get("title"), expected.get("title"), threshold=0.8
    )

    return results


def aggregate_results(all_results: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate individual listing results into overall metrics."""
    if not all_results:
        return {}

    n = len(all_results)
    return {
        "price_accuracy": sum(1 for r in all_results if r["price_correct"]) / n,
        "year_accuracy": sum(1 for r in all_results if r["year_correct"]) / n,
        "model_accuracy": sum(1 for r in all_results if r["model_correct"]) / n,
        "avg_description_rouge": sum(r["description_rouge"] for r in all_results) / n,
        "link_extraction_rate": sum(1 for r in all_results if r["link_extracted"]) / n,
        "avg_title_score": sum(r["title_score"] for r in all_results) / n,
        "total_evaluated": n,
    }
