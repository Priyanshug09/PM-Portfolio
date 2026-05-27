import streamlit as st
import pandas as pd
from guardrails import OrderContext, run_guardrails

st.set_page_config(page_title="Returns Guardrail Simulator v3", layout="wide")

SCENARIOS = {
    "Low-risk replacement": {
        "description": "Clear damaged-item complaint, replacement available, image uploaded, low risk.",
        "user_text": "The jar is broken. I want replacement, not refund.",
        "context": OrderContext(
            item_category="kitchen_appliance",
            item_value=2500,
            return_window_open=True,
            replacement_stock_available=True,
            pickup_available=True,
            user_account_age_days=365,
            past_refund_claims_90d=1,
            image_uploaded=True,
        ),
        "expected": "show_valid_options_and_ask_final_confirmation",
    },
    "Return pickup requested": {
        "description": "User clearly wants to return the damaged item.",
        "user_text": "Mobile is broken I want to return",
        "context": OrderContext(
            item_category="electronics",
            item_value=2500,
            return_window_open=True,
            replacement_stock_available=True,
            pickup_available=True,
            user_account_age_days=365,
            past_refund_claims_90d=1,
            image_uploaded=True,
        ),
        "expected": "show_valid_options_and_ask_final_confirmation",
    },
    "No image uploaded": {
        "description": "Damaged-item complaint but no evidence uploaded.",
        "user_text": "The jar is broken. I want replacement, not refund.",
        "context": OrderContext(
            item_category="kitchen_appliance",
            item_value=2500,
            return_window_open=True,
            replacement_stock_available=True,
            pickup_available=True,
            user_account_age_days=365,
            past_refund_claims_90d=1,
            image_uploaded=False,
        ),
        "expected": "request_evidence",
    },
    "Replacement unavailable": {
        "description": "User wants replacement but stock is not available.",
        "user_text": "The item is damaged. I want replacement.",
        "context": OrderContext(
            item_category="kitchen_appliance",
            item_value=2500,
            return_window_open=True,
            replacement_stock_available=False,
            pickup_available=True,
            user_account_age_days=365,
            past_refund_claims_90d=1,
            image_uploaded=True,
        ),
        "expected": "explain_policy_and_offer_valid_options",
    },
    "Unclear user intent": {
        "description": "User complaint is vague, so the assistant should not guess.",
        "user_text": "This is bad. Help me.",
        "context": OrderContext(
            item_category="kitchen_appliance",
            item_value=2500,
            return_window_open=True,
            replacement_stock_available=True,
            pickup_available=True,
            user_account_age_days=365,
            past_refund_claims_90d=1,
            image_uploaded=True,
        ),
        "expected": "ask_clarifying_question",
    },
    "High-risk claim": {
        "description": "Clear intent but high item value and repeated refund claims create business risk.",
        "user_text": "The item is broken. I want refund.",
        "context": OrderContext(
            item_category="electronics",
            item_value=10000,
            return_window_open=True,
            replacement_stock_available=True,
            pickup_available=True,
            user_account_age_days=5,
            past_refund_claims_90d=5,
            image_uploaded=True,
        ),
        "expected": "escalate_to_human_agent",
    },
}


def context_to_sidebar(context: OrderContext):
    st.sidebar.header("Order Context")
    st.sidebar.write("These values come from the selected scenario. You can still edit them manually below.")

    categories = ["kitchen_appliance", "electronics", "fashion", "grocery", "other"]

    item_category = st.sidebar.selectbox(
        "Item category",
        categories,
        index=categories.index(context.item_category),
    )

    item_value = st.sidebar.slider("Item value", 100, 20000, context.item_value, step=100)
    return_window_open = st.sidebar.checkbox("Return window open", value=context.return_window_open)
    replacement_stock_available = st.sidebar.checkbox("Replacement stock available", value=context.replacement_stock_available)
    pickup_available = st.sidebar.checkbox("Pickup available", value=context.pickup_available)
    image_uploaded = st.sidebar.checkbox("Image uploaded", value=context.image_uploaded)
    user_account_age_days = st.sidebar.slider("User account age in days", 1, 2000, context.user_account_age_days)
    past_refund_claims_90d = st.sidebar.slider("Past refund claims in last 90 days", 0, 10, context.past_refund_claims_90d)

    return OrderContext(
        item_category=item_category,
        item_value=item_value,
        return_window_open=return_window_open,
        replacement_stock_available=replacement_stock_available,
        pickup_available=pickup_available,
        user_account_age_days=user_account_age_days,
        past_refund_claims_90d=past_refund_claims_90d,
        image_uploaded=image_uploaded,
    )


st.title("Returns Guardrail Simulator v3")
st.caption("A tiny AI product guardrail project for an e-commerce refund/replacement assistant.")

st.markdown("""
### Product Goal
Prevent wrong refund or replacement workflows by adding guardrails before the assistant triggers any backend action.
""")

scenario_name = st.selectbox("Choose a test scenario", list(SCENARIOS.keys()))
scenario = SCENARIOS[scenario_name]

st.info(f"**Scenario purpose:** {scenario['description']}")
st.write(f"**Expected final action:** `{scenario['expected']}`")

context = context_to_sidebar(scenario["context"])

user_text = st.text_area(
    "User complaint",
    value=scenario["user_text"],
    height=120,
)

if st.button("Run Guardrails", type="primary"):
    decision = run_guardrails(user_text, context)

    st.subheader("Guardrail Decision")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Issue Type", decision.issue_type)
    col2.metric("Preferred Resolution", decision.preferred_resolution)
    col3.metric("Intent Confidence", decision.intent_confidence)
    col4.metric("Risk Level", decision.risk_level)

    st.markdown("### Final Action")
    if decision.final_action == scenario["expected"]:
        st.success(f"{decision.final_action} ✅ matches expected scenario")
    else:
        st.warning(f"{decision.final_action} ⚠️ does not match expected scenario")
        st.write("This usually means sidebar values were manually changed and another guardrail overrode the expected result.")

    st.markdown("### Explanation")
    st.info(decision.explanation)

    st.markdown("### Guardrails Triggered")
    for guardrail in decision.guardrails_triggered:
        st.write(f"- {guardrail}")

    st.markdown("### Eligible Resolution Options")
    st.write(decision.policy_eligible_options)

    st.markdown("### Decision Output Table")
    df = pd.DataFrame([
        {"Metric": "Issue type", "Value": str(decision.issue_type)},
        {"Metric": "Preferred resolution", "Value": str(decision.preferred_resolution)},
        {"Metric": "Intent confidence", "Value": str(decision.intent_confidence)},
        {"Metric": "Evidence required", "Value": str(decision.evidence_required)},
        {"Metric": "Risk level", "Value": str(decision.risk_level)},
        {"Metric": "Final action", "Value": str(decision.final_action)},
        {"Metric": "Expected final action", "Value": str(scenario["expected"])},
    ])
    st.dataframe(df, use_container_width=True)

st.markdown("""
---
### PM Learning Point

A guardrail does not mean “stop everything.”

A guardrail decides whether the assistant should:

```text
Proceed
Clarify
Request evidence
Explain policy
Escalate to human
Ask final confirmation
```

The goal is not maximum automation.  
The goal is the fastest correct resolution with acceptable business risk.
""")
