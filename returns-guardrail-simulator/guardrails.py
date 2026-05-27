from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class OrderContext:
    item_category: str = "kitchen_appliance"
    item_value: int = 2500
    return_window_open: bool = True
    replacement_stock_available: bool = True
    pickup_available: bool = True
    user_account_age_days: int = 365
    past_refund_claims_90d: int = 1
    image_uploaded: bool = True


@dataclass
class GuardrailDecision:
    issue_type: str
    preferred_resolution: str
    intent_confidence: float
    policy_eligible_options: List[str]
    evidence_required: bool
    risk_level: str
    guardrails_triggered: List[str]
    final_action: str
    explanation: str

    def to_dict(self) -> Dict:
        return asdict(self)


def extract_intent(user_text: str) -> Dict:
    text = user_text.lower()

    issue_type = "unknown"
    preferred_resolution = "unknown"
    confidence = 0.45

    damaged_terms = ["damaged", "broken", "cracked", "defective", "not working"]
    wrong_item_terms = ["wrong item", "different item", "incorrect item"]
    missing_terms = ["missing", "missing part", "part not included"]
    pickup_terms = ["pickup failed", "pickup not done", "no pickup"]

    replacement_terms = ["replacement", "replace", "exchange", "send new"]
    refund_terms = ["refund", "money back"]
    return_terms = ["return", "return item", "send back", "return pickup"]
    negative_refund_terms = ["not refund", "don't want refund", "do not want refund", "no refund"]

    if any(term in text for term in damaged_terms):
        issue_type = "damaged_item"
        confidence += 0.25
    elif any(term in text for term in wrong_item_terms):
        issue_type = "wrong_item"
        confidence += 0.25
    elif any(term in text for term in missing_terms):
        issue_type = "missing_part"
        confidence += 0.20
    elif any(term in text for term in pickup_terms):
        issue_type = "pickup_failure"
        confidence += 0.25

    if any(term in text for term in negative_refund_terms):
        preferred_resolution = "replacement"
        confidence += 0.20
    elif any(term in text for term in replacement_terms):
        preferred_resolution = "replacement"
        confidence += 0.20
    elif any(term in text for term in refund_terms):
        preferred_resolution = "refund"
        confidence += 0.20
    elif any(term in text for term in return_terms):
        preferred_resolution = "return_pickup"
        confidence += 0.20

    confidence = min(round(confidence, 2), 0.98)

    return {
        "issue_type": issue_type,
        "preferred_resolution": preferred_resolution,
        "intent_confidence": confidence,
    }


def check_policy(context: OrderContext) -> List[str]:
    options = []

    if not context.return_window_open:
        return ["talk_to_agent"]

    if context.replacement_stock_available:
        options.append("replacement")

    options.append("refund_after_pickup")

    if context.item_category in ["kitchen_appliance", "electronics"]:
        options.append("warranty_support")

    if context.pickup_available:
        options.append("return_pickup")

    options.append("talk_to_agent")
    return options


def is_evidence_required(issue_type: str, context: OrderContext) -> bool:
    if issue_type in ["damaged_item", "wrong_item"]:
        return True
    if context.item_value >= 3000:
        return True
    return False


def calculate_risk(context: OrderContext) -> str:
    risk_score = 0

    if context.item_value >= 5000:
        risk_score += 2
    elif context.item_value >= 3000:
        risk_score += 1

    if context.user_account_age_days < 30:
        risk_score += 2

    if context.past_refund_claims_90d >= 3:
        risk_score += 2
    elif context.past_refund_claims_90d == 2:
        risk_score += 1

    if risk_score >= 4:
        return "high"
    if risk_score >= 2:
        return "medium"
    return "low"


def run_guardrails(user_text: str, context: OrderContext) -> GuardrailDecision:
    intent = extract_intent(user_text)
    issue_type = intent["issue_type"]
    preferred_resolution = intent["preferred_resolution"]
    intent_confidence = intent["intent_confidence"]

    eligible_options = check_policy(context)
    evidence_required = is_evidence_required(issue_type, context)
    risk_level = calculate_risk(context)

    triggered = []

    if intent_confidence < 0.65:
        triggered.append("intent_clarification_required")

    if preferred_resolution == "unknown":
        triggered.append("preferred_resolution_missing")

    if evidence_required and not context.image_uploaded:
        triggered.append("evidence_required_before_resolution")

    if preferred_resolution != "unknown" and preferred_resolution not in eligible_options:
        triggered.append("requested_resolution_not_eligible")

    if risk_level == "high":
        triggered.append("human_review_due_to_high_risk")

    triggered.append("final_confirmation_required_before_workflow")

    if "human_review_due_to_high_risk" in triggered:
        final_action = "escalate_to_human_agent"
        explanation = "High-risk signals detected. The assistant should not auto-approve refund or replacement. Route to human review."

    elif "intent_clarification_required" in triggered or "preferred_resolution_missing" in triggered:
        final_action = "ask_clarifying_question"
        explanation = "The assistant is not confident about the user's issue or preferred resolution. Ask a clarifying question before action."

    elif "requested_resolution_not_eligible" in triggered:
        final_action = "explain_policy_and_offer_valid_options"
        explanation = f"The user requested '{preferred_resolution}', but that option is not eligible. Explain why and show valid options: {eligible_options}."

    elif "evidence_required_before_resolution" in triggered:
        final_action = "request_evidence"
        explanation = "The claim requires proof. Ask the user to upload an image before approving refund or replacement."

    else:
        final_action = "show_valid_options_and_ask_final_confirmation"
        explanation = "The assistant can show valid options, but must ask for final confirmation before triggering backend workflow."

    return GuardrailDecision(
        issue_type=issue_type,
        preferred_resolution=preferred_resolution,
        intent_confidence=intent_confidence,
        policy_eligible_options=eligible_options,
        evidence_required=evidence_required,
        risk_level=risk_level,
        guardrails_triggered=triggered,
        final_action=final_action,
        explanation=explanation,
    )
