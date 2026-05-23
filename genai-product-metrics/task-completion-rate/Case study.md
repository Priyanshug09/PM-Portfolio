# Task Completion Rate (TCR) — AI Product Case Study

> **Builder Loop:** Learn → Build → Break → Fix → Business Impact → Publish

---

## TL;DR

TCR measures whether your AI agent **actually completes tasks** — or just pretends to.

Built a live tracker. Broke it 3 ways. Fixed each one.
At 10,000 tasks/day, moving from 70% → 90% TCR saves **₹4,00,000 every single day.**

---

## The Problem

Companies build AI agents to handle customer tasks — booking flights, cancelling orders, answering questions.

The pitch: *"AI handles it so humans don't have to."*

The reality: **nobody knows if the AI is actually doing the job** — or silently failing while humans clean up behind it.

---

## Who Feels the Pain

| Stakeholder | The pain |
|---|---|
| **Customer** | Asks AI to cancel a booking. AI says "done." Booking is still active. Finds out at check-in. Never comes back. |
| **Support agent** | Spends 80% of the day fixing tasks the AI claimed it completed. Hired for edge cases. Does basic rework instead. |
| **Product manager** | Reports "X thousand AI tasks per month" to leadership. Has no idea how many actually completed. Gets blindsided by cost overrun. |
| **Business** | Paid to build AI that replaces 10 agents. Still employs 10 agents. Plus the AI vendor cost. ROI never arrives. |

**Root cause:** Nobody defined what "completed" means. Nobody verified outcomes independently.

---

## What is TCR — In Simple Words

> Out of every 100 tasks you give the AI, how many does it finish on its own — without a human stepping in?

```
TCR = Tasks completed without human fallback
      ─────────────────────────────────────
              Total tasks attempted
```

**Example:** 100 customers ask the AI to book a flight. 88 bookings confirm. 12 fail (timeouts, escalations, errors). **TCR = 88%.**

| TCR | What it means |
|---|---|
| Below 70% | AI costs more than it saves |
| 80% | Industry baseline — PM interview benchmark |
| 90%+ | Production-grade — AI genuinely replacing human effort |

> 80% comes from Yellow.ai, Haptik, Zendesk — they use it as the floor in enterprise QBRs and PM hiring screens.

---

## Use Cases — Where TCR Is Actually Measured

| Industry | What the AI does | What TCR verifies |
|---|---|---|
| Travel & booking | Books flights, hotels | Did the PNR actually get created? |
| E-commerce | Handles returns, refunds | Did the refund actually initiate? |
| Banking / fintech | Files disputes, changes limits | Did the dispute actually get filed? |
| Telecom | Plan upgrades, billing queries | Did the plan actually change? |
| Healthcare | Books appointments | Did the slot actually get reserved? |
| HR / IT helpdesk | Resolves tickets, onboarding | Did the ticket actually get closed? |

> **Key insight:** TCR is not about what the AI *says* it did. It is about what *actually happened* in the system of record.

---

## When to Measure

| When | Why | Action |
|---|---|---|
| At launch | Establish baseline before optimising | 2-week minimum sample |
| Every week | A 3% drop is a signal — catch it early | Alert at −3% week-over-week |
| After every release | Model updates and prompt changes regress TCR silently | Pre/post deploy gate |
| By category | Aggregate hides weak spots — segment reveals them | Per-category dashboard |
| By risk level | Flight bookings ≠ FAQ answers in risk or threshold | Risk-stratified thresholds |
## Business Impact

> At 10,000 tasks/day and ₹200 per human-handled task:

| TCR | Human tasks/day | Daily cost | Annual cost |
|---|---|---|---|
| 70% | 3,000 | ₹6,00,000 | ₹21.9 Cr |
| 80% | 2,000 | ₹4,00,000 | ₹14.6 Cr |
| **90%** | **1,000** | **₹2,00,000** | **₹7.3 Cr** |
| 95% | 500 | ₹1,00,000 | ₹3.65 Cr |

**Every 10% TCR lift = ₹2,00,000 saved per day.**
That is ₹7.3 Cr per year from a single metric improvement.

---
