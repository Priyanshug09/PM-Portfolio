# Case Study: Guardrails for AI Return Assistant

## Problem

Users with damaged/wrong items may receive the wrong resolution when an AI support assistant misclassifies intent or directly triggers refund/replacement without confirmation.

Example:

```text
User: The item is damaged. I want replacement, not refund.
Bot: Your refund will be processed after pickup.
```

## Product Diagnosis

This is not only a chatbot problem.

It may be a breakdown across:

| Layer | Possible Failure |
|---|---|
| Intent layer | Bot missed replacement/return/refund intent |
| Policy layer | Replacement unavailable but not explained |
| Operations layer | Stock/pickup unavailable |
| Evidence layer | Photo required but not collected |
| Risk layer | Claim needs human review |
| Confirmation layer | Refund triggered without confirmation |
| Backend layer | Wrong workflow executed |

## Guardrail Purpose

Guardrails are decision checkpoints placed across the AI support journey to ensure that the assistant understands the user correctly, checks policy and operational feasibility, handles risk, asks for clarification when needed, and confirms before triggering any refund, return, or replacement workflow.

## Scenario Tests

| Scenario | Expected Action |
|---|---|
| Low-risk replacement | Show valid options and ask final confirmation |
| Return pickup requested | Show valid options and ask final confirmation |
| No image uploaded | Request evidence |
| Replacement unavailable | Explain policy and offer valid options |
| Unclear user intent | Ask clarifying question |
| High-risk claim | Escalate to human agent |

## Core Metrics

| Metric | Why It Matters |
|---|---|
| Correct resolution rate | Main success metric |
| Repeat contact rate | Detect failed resolutions |
| Wrong refund initiation rate | Detect harmful automation |
| Evidence completion rate | Measure proof collection |
| Human escalation rate | Monitor support load |
| Fraud/risk rate | Protect business and sellers |
| CSAT | Measure customer trust |
