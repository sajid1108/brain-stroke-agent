import json
import logging
import os
from typing import List

logger = logging.getLogger("brain_stroke_agent")

RADIOLOGIST_SYSTEM_PROMPT = """You are an expert radiologist AI assistant specializing in brain CT scan interpretation.

A deterministic diagnostic pipeline has ALREADY decided the primary diagnosis using majority
voting across three CNN models (a custom CNN, ResNet18, and AlexNet), with averaged softmax
probabilities used as a tiebreaker. You are NOT deciding the diagnosis -- it is fixed and given
to you. Your job is purely to explain and report on it in clinical language.

You will be given:
- The final diagnosis (already decided): Normal, Ischemia, or Bleeding.
- The confidence level (already decided): High/Moderate/Low.
- Each model's individual prediction and its probability for each class.

Your job:
1. Summarize, in plain clinical language, how the three models voted and why the deterministic
   pipeline arrived at this diagnosis and confidence level (e.g. unanimous, 2-1 majority, or a
   probability-based tiebreak).
2. Write a short radiological rationale consistent with the GIVEN diagnosis, based on standard
   CT presentations:
   - Ischemia: a focal hypo-dense (darker) region caused by a blockage/infarct.
   - Bleeding: a hyper-dense (brighter) mass with surrounding edema.
   - Normal: no significant hypo-dense or hyper-dense lesion.
3. Recommend an immediate clinical action appropriate to the GIVEN diagnosis.

STRICT RULES:
- Do NOT change, second-guess, or override the diagnosis or confidence level you are given.
- Do NOT invent patient details, symptoms, or history not provided.
- If a model disagreed with the consensus, mention it neutrally.

Respond ONLY in valid JSON with this schema, no extra text:
{
  "model_consensus": "<1-2 sentence summary of how the models voted/agreed>",
  "doctor_notes": "<clinical/radiological rationale consistent with the given diagnosis, referencing each model>",
  "suggested_action": "<1-2 sentence recommended next step>"
}"""


class AgenticDoctor:
    """Wraps Groq to explain an already-fixed diagnosis. Degrades gracefully with no API key."""

    def __init__(self, groq_api_key: str = None, groq_model: str = "llama-3.3-70b-versatile"):
        self.groq_model = groq_model
        api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        self.enabled = bool(api_key)
        self.client = None
        if self.enabled:
            from groq import Groq  # imported lazily so the app still boots without the package/key

            self.client = Groq(api_key=api_key)
        else:
            logger.warning("GROQ_API_KEY not set -- LLM explanation step disabled, deterministic-only mode.")

    def _build_user_prompt(self, tool_output: List[dict], decision: dict) -> str:
        lines = ["DETERMINISTIC PIPELINE OUTPUT (already decided -- do not change):"]
        lines.append(f"- Final diagnosis: {decision['primary_diagnosis']}")
        lines.append(f"- Confidence: {decision['confidence']}")
        lines.append(f"- Decision method: {decision['decision_method']}")
        lines.append(f"- Vote counts: {decision['vote_counts']}")
        lines.append(f"- Averaged probabilities across models: {decision['average_probabilities']}\n")

        lines.append("Per-model breakdown:")
        for res in tool_output:
            lines.append(f"- {res['model']}: predicted {res['prediction']} | probabilities: {res['probabilities']}")

        lines.append("\nWrite the clinical explanation and report for this. Respond with JSON only.")
        return "\n".join(lines)

    def _fallback_explanation(self, decision: dict) -> dict:
        return {
            "model_consensus": f"Diagnosis decided by {decision['decision_method']} "
            f"({decision['vote_counts']}).",
            "doctor_notes": "LLM explanation unavailable (no GROQ_API_KEY configured). "
            "The diagnosis above was produced deterministically by the model ensemble.",
            "suggested_action": "Have a radiologist review this case manually.",
        }

    def explain(self, tool_output: List[dict], decision: dict) -> dict:
        if not self.enabled:
            explanation = self._fallback_explanation(decision)
        else:
            user_prompt = self._build_user_prompt(tool_output, decision)
            try:
                response = self.client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": RADIOLOGIST_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                explanation = json.loads(response.choices[0].message.content)
            except Exception as exc:  # network error, bad key, parse failure, etc.
                logger.exception("Groq explanation failed, falling back")
                explanation = self._fallback_explanation(decision)
                explanation["doctor_notes"] += f" (error: {exc})"

        return {
            "primary_diagnosis": decision["primary_diagnosis"],
            "confidence": decision["confidence"],
            "decision_method": decision["decision_method"],
            "model_consensus": explanation.get("model_consensus", ""),
            "doctor_notes": explanation.get("doctor_notes", ""),
            "suggested_action": explanation.get("suggested_action", ""),
            "llm_used": self.enabled,
        }
