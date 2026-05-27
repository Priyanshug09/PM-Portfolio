# Returns Guardrail Simulator v3

A tiny Product Management + AI systems project that demonstrates how **guardrails** protect an AI return/refund assistant from triggering the wrong workflow.

## v3 Fix

Added support for **return intent**.

Example:

```text
Mobile is broken I want to return
```

Now detects:

```text
Issue type = damaged_item
Preferred resolution = return_pickup
```

Also fixed the Streamlit dataframe warning by converting mixed table values to strings.

## Product Goal

Prevent wrong refund or replacement workflows by adding decision checkpoints before the assistant triggers any backend action.

```text
User complaint
→ Intent extraction
→ Policy eligibility
→ Evidence check
→ Risk check
→ Valid option generation
→ Final confirmation requirement
```

## How to Run

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Portfolio One-Liner

Built a rule-based AI guardrail simulator for an e-commerce returns assistant to prevent wrong refund/replacement workflows using intent confirmation, policy checks, evidence checks, risk routing, return intent handling, and final confirmation.
