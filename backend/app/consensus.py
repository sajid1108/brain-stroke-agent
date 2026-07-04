from typing import Dict, List

from .models import CLASS_NAMES


def compute_consensus_diagnosis(tool_output: List[dict]) -> dict:
    """
    Deterministic diagnosis -- pure Python, no LLM. Majority vote, with
    averaged softmax probabilities as a tiebreaker. Same inputs -> same output, always.
    """
    predictions = [res["prediction"] for res in tool_output]
    vote_counts = {p: predictions.count(p) for p in set(predictions)}
    top_votes = max(vote_counts.values())
    tied_classes = [cls for cls, count in vote_counts.items() if count == top_votes]

    avg_probs: Dict[str, float] = {cls: 0.0 for cls in CLASS_NAMES}
    for res in tool_output:
        for cls, p in res["probabilities"].items():
            avg_probs[cls] += p / len(tool_output)

    if len(tied_classes) == 1:
        consensus_pred = tied_classes[0]
        method = "majority_vote"
    else:
        consensus_pred = max(tied_classes, key=lambda cls: avg_probs[cls])
        method = "probability_average_tiebreak"

    if top_votes == len(tool_output):
        confidence_level = "High (Unanimous)"
    elif top_votes >= 2:
        confidence_level = "Moderate (Majority)"
    else:
        confidence_level = "Low (Inconclusive)"

    return {
        "primary_diagnosis": consensus_pred,
        "confidence": confidence_level,
        "decision_method": method,
        "vote_counts": vote_counts,
        "average_probabilities": avg_probs,
    }
