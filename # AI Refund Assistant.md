# AI Refund Assistant — Reducing Human Support Dependency in E-commerce

> **Portfolio Case Study** | AI Product Thinking Lab  
> **Author:** [Your Name]  
> **Role:** Aspiring AI Product Manager  
> **Learning Framework:** Concept → Build → Break → Fix → Business Impact → GitHub → Case Study

---

## Table of Contents

1. [Why I Chose This Problem](#1-why-i-chose-this-problem)
2. [The Problem I Was Given](#2-the-problem-i-was-given)
3. [How I Framed the Problem](#3-how-i-framed-the-problem)
4. [Users I Had to Think About](#4-users-i-had-to-think-about)
5. [User Journey I Mapped](#5-user-journey-i-mapped)
6. [Why I Think Chatbots Fail at Transactions — My Systems Analysis](#6-why-i-think-chatbots-fail-at-transactions--my-systems-analysis)
7. [What Data Does the AI Actually Need?](#7-what-data-does-the-ai-actually-need)
8. [The Decision That Mattered Most: AI vs Deterministic Rules](#8-the-decision-that-mattered-most-ai-vs-deterministic-rules)
9. [The Edge Case I Dug Into: Image Upload Flow](#9-the-edge-case-i-dug-into-image-upload-flow)
10. [Risks I Mapped Before Thinking About Launch](#10-risks-i-mapped-before-thinking-about-launch)
11. [How I Would Measure Success](#11-how-i-would-measure-success)
12. [How I Would Run the Experiment](#12-how-i-would-run-the-experiment)
13. [What My PRD Would Look Like](#13-what-my-prd-would-look-like)
14. [Mental Models I Built Through This](#14-mental-models-i-built-through-this)
15. [What I Would Do Differently](#15-what-i-would-do-differently)

---

## 1. Why I Chose This Problem

I started this because I kept seeing the same pattern — companies launch AI chatbots, customers still call human agents, and the company can't figure out why. The bot sounds smart but doesn't actually resolve anything transactional.

I wanted to understand *exactly* why that happens at a systems level — not just "the AI isn't good enough" but the real breakdown points. So I took a realistic e-commerce scenario and worked through it end to end the way I'd actually have to think about it as a PM.

My learning loop for this:
```
Understand the concept
→ Explain it in simple words to myself
→ Build a tiny case
→ Break the assumptions
→ Fix the gaps
→ Add business thinking
→ Document publicly
```

This README is the output.

---

## 2. The Problem I Was Given

**Scenario:**

An e-commerce platform (Flipkart/Amazon scale) deploys an AI chatbot for customer support. Three months after going live, support costs have not dropped. Human agents are still handling most refund and replacement queries.

The CEO says:

> *"The chatbot is live, but support cost is still high. Fix this."*

---

## 3. How I Framed the Problem

My first instinct was to look at the AI model — maybe the intent classification is off, or the training data is poor. But when I dug deeper, I realized that was the wrong starting point.

The real question was: **where exactly in the stack is the failure happening?**

I built this decomposition to force myself to look at every layer before jumping to a solution:

| Layer | What I Asked |
|---|---|
| User Layer | What does the user actually want from this flow? |
| UX Layer | Is the conversational flow intuitive and trust-building? |
| AI Layer | Is the model classifying intent correctly? |
| Data Layer | Does the AI have access to real, current customer data? |
| Systems Layer | Are the backend APIs actually connected to the bot? |
| Infrastructure Layer | Is the system fast and reliable enough to serve real queries? |
| Security Layer | Is the AI's data access being blocked for compliance reasons? |
| Business Layer | Is the AI even authorized to take action, or just to talk? |

What I found: most of the failure lived in **layers 4 through 8** — data, systems, infra, security, and business authorization. Not in the AI model itself.

That reframing changed everything about how I approached the rest of this case.

---

## 4. Users I Had to Think About

### Primary Users — The Customers

| User Type | What They Want | Where They Get Stuck |
|---|---|---|
| Refund requestor | Money back, fast, with confirmation | Bot loops without giving a clear answer |
| Replacement requestor | Correct item, clear ETA | Bot can't confirm eligibility or schedule |
| Damaged item reporter | Acknowledgment + resolution | Gets generic policy text, not a real answer |

### Secondary Users — Everyone the System Also Affects

This was a big shift in my thinking. Before this case, I mostly thought about the end customer. But when I mapped this out, I realized the chatbot behavior directly impacts several other teams — and if I optimize only for the customer, I could silently break things for everyone else.

| Secondary User | What They Need | How AI Behavior Affects Them |
|---|---|---|
| Customer Support Agent | Clean escalation context | Poorly escalated sessions mean agents restart from scratch — wasted time |
| Refund Operations Team | Accurate, policy-compliant refund requests | Wrong AI approvals create operational chaos and financial risk |
| Finance / Accounting Team | Clean payment reconciliation | Duplicate or incorrect refunds break accounting downstream |
| Fraud / Risk Team | Proper checks before any approval | AI acting without risk validation opens fraud abuse vectors |
| Engineering / Infra Team | Stable, predictable API call patterns | Bad AI design creates cascading backend failures at scale |
| Compliance / Legal Team | GDPR and PCI boundaries respected | AI accessing restricted data without proper controls = regulatory exposure |

### The Tension I Had to Hold

```
Customer wants:     Fastest possible resolution
Risk Team needs:    Proper verification before acting

Customer wants:     Minimal friction
Finance needs:      Approvals through correct workflow

Customer wants:     AI to act immediately
Legal needs:        Certain actions to stay with humans
```

There's no perfect answer here — just tradeoffs I'd have to make explicit in the product requirements.

---

## 5. User Journey I Mapped

### Standard Refund / Replacement Flow

```
Customer receives damaged / wrong / missing product
                ↓
Opens chatbot (app or web)
                ↓
Describes issue in natural language
                ↓
Bot identifies intent:
[refund / replacement / status check / escalate to human]
                ↓
Bot requests order ID or surfaces recent orders from OMS
                ↓
System checks eligibility rules:
  → Is return window still open?
  → Is item category eligible for return?
  → Does seller have standard or custom policy?
  → Has user previously claimed on this order?
                ↓
Bot presents options:
  1. Replacement (new item dispatched)
  2. Refund to original payment method
  3. Refund as wallet / store credits
  4. Connect to human agent
                ↓
Customer selects + confirms
                ↓
System creates return / replacement ticket in CRM
                ↓
Pickup scheduling triggered (if return required)
                ↓
Confirmation sent: ticket ID + ETA + next steps
                ↓
Future status queries resolved via same chatbot
```

### Where I Found the Flow Breaking Down

| Step | What Can Break | Why It Breaks |
|---|---|---|
| Intent identification | "Replacement" gets classified as "Refund" | Intent model trained on insufficient variation |
| Order lookup | Order not found / wrong order surfaced | User authentication gap; session not linked to account |
| Eligibility check | Bot gives incorrect window or policy | Rules engine not connected — AI estimates based on training data |
| Resolution options | Bot offers refund on ineligible item | Policy engine not integrated at all |
| Ticket creation | Ticket created with wrong type/priority | Misclassification carried forward through entire pipeline |
| Status query | Bot says "processing" when item already delivered | No real-time OMS sync; cached or stale data |

---

## 6. Why I Think Chatbots Fail at Transactions — My Systems Analysis

This is the section I spent the most time on because it forced me to understand the full architecture, not just the user-facing layer.

### Failure Mode 1: No Backend Integration

The most common and most avoidable. The chatbot has no live connection to the systems that hold actual data.

```
User → Chatbot
BUT
Chatbot ✗ Order Management System
Chatbot ✗ Refund System
Chatbot ✗ Logistics API
Chatbot ✗ Payment Gateway

What the AI actually knows:
  → FAQs
  → Static policy documents
  → General training data

What the AI does NOT know:
  → Whether this specific order is eligible
  → Whether this specific refund was processed
  → Where this specific shipment is right now
```

This happens because companies launch AI fast — "put GPT on the website" — without first doing the integration work. The result is a bot that sounds helpful but is operationally useless for any transactional query.

---

### Failure Mode 2: APIs Exist But Are Access-Restricted

The systems are there. The APIs exist. But security or compliance teams block the AI from accessing them.

Why? These systems contain:
- Full payment card details (PCI-DSS restricted)
- Personally identifiable information (GDPR restricted)
- Financial approval authority (internal controls)
- Sensitive transaction history

I had to internalize this as a PM: **technical possibility ≠ organizational permission.** Getting an engineer to say "yes we can connect this" is a completely different conversation from getting legal, security, and finance to sign off on what the AI is allowed to see and do.

---

### Failure Mode 3: Legacy Systems Can't Integrate in Real Time

Large enterprises often run on infrastructure that was built 10–20 years ago.

```
How the old system works:
Mainframe → CSV Export → Nightly Batch Update → Available next morning

What the AI needs to function:
Real-time API Call → Live response → Grounded answer → Now
```

The AI might technically connect to this system — but it receives data that's 12 hours stale. Customer asks where their refund is. AI tells them what the status was yesterday morning. Both the customer and the AI are wrong about what's actually happening.

---

### Failure Mode 4: Data Sits Across Multiple Disconnected Systems

A single refund query like "Where is my refund?" might need data from:

| Data Point | System |
|---|---|
| Order details | Order Management System |
| Payment confirmation | Payment Gateway |
| Refund processing status | Finance / Refund Engine |
| Shipment tracking | Third-party Logistics API |
| Customer history | CRM |
| Return receipt | Warehouse Management System |

If even one of these is disconnected, the AI gives an incomplete answer. If two systems have contradictory states (payment says "approved," OMS says "pending"), the AI looks wrong even when it's just reflecting a real system inconsistency.

The fix isn't making the AI smarter — it's orchestrating the data properly. AI quality is a direct function of data architecture.

---

### Failure Mode 5: No User Authentication Before Data Access

Before the AI can fetch real order data, it needs to verify the person asking is actually the account holder. Without this:
- Any person could query any order by guessing an order ID
- GDPR and data laws prohibit disclosure without verified identity
- Fraud vectors open up immediately

The tension I had to think about here:
```
More verification steps → More friction → Users abandon the flow
Less verification       → Legal risk + fraud exposure
```
There's no clean answer — I'd need to define the minimum viable verification that satisfies legal requirements without killing conversion.

---

### Failure Mode 6: Real-Time APIs Are Expensive at Scale

At millions of daily sessions, each chatbot interaction might trigger:
- A DB read on the OMS
- An API call to the payment gateway
- A logistics provider lookup
- A CRM fetch

Infrastructure cost compounds fast. This is why companies sometimes intentionally cache data or throttle API calls — which directly degrades answer quality. This was a business tradeoff I hadn't thought about before: accuracy vs. cost at scale.

---

### Failure Mode 7: The AI Isn't Grounded — It Hallucinates

This is the GenAI-specific failure mode I find most dangerous in transactional contexts.

**What the correct flow looks like:**
```
User query → Intent detection → API call → Live data → Grounded response
```

**What a hallucinating flow looks like:**
```
User query → LLM generates plausible-sounding answer from training data
           → No API was called
           → Customer gets confident but completely wrong information
```

LLMs are trained to be helpful. They will generate a plausible refund status even when they have zero access to actual refund data. This is worse than "I don't know" because it gives customers false confidence and destroys trust when they find out the answer was fabricated.

The fix: make retrieval mandatory before generation for any transactional query. The AI should never speak about order/refund/payment state unless it has just fetched live data from the source system.

---

### Failure Mode 8: Intent Routing Fails Before Any API Is Called

The system can break before the AI even attempts to answer.

Example: Customer says *"My replacement still hasn't arrived."*

System classifies: `intent = refund_request`
Correct classification: `intent = shipment_tracking`

Now the refund system gets queried instead of the logistics API. Wrong data comes back. Wrong answer is generated. Customer escalates.

This taught me that AI systems are pipelines — a misclassification at step one corrupts every step after it.

---

### Failure Mode 9: The Company Intentionally Limits What AI Can Do

This one surprised me. Sometimes the AI is restricted not by a technical limitation, but by a deliberate business decision.

Companies prevent AI from:
- Issuing refunds autonomously
- Approving compensation or goodwill credits
- Cancelling subscriptions without human review

Why? Because:
- Fraud risk: bad actors can repeatedly claim refunds if the bot auto-approves
- Financial leakage: unchecked AI approvals damage the P&L at scale
- Legal liability: auto-approving disputed transactions creates exposure

Understanding this changed how I think about AI feature scope. The question isn't just "can we build this?" — it's "does the business want AI to have this authority, and what controls need to exist if it does?"

---

### Failure Mode 10: The Data Itself Is Bad

Even if the AI connects successfully to every system, the data inside those systems might be:

```
Order status:    "SHIP_2A_PENDING_X_REVISED_HOLD"
Refund state:    NULL
Return date:     01/01/1970
Customer ID:     Duplicate records found (3 matches)
```

The AI cannot give a reliable answer from inconsistent, unstandardized data. Worse — it often doesn't know the data is bad, so it answers confidently using garbage input.

This was the biggest mindset shift for me in this entire case: **most AI product problems are actually data quality problems.** Fixing the AI model without fixing the underlying data is building on a broken foundation.

---

## 7. What Data Does the AI Actually Need?

Before designing any flow, I mapped every user query to the exact data required and the system that holds it — including where integration risk is highest.

| User Query | Data Required | Source System | Integration Risk |
|---|---|---|---|
| "Where is my refund?" | Refund status, amount, ETA | Payment / Refund Engine | Medium — may live in separate finance system |
| "Can I replace this item?" | Return window status, item category, policy rules | OMS + Policy Engine | High — policy engine often not exposed via API |
| "My item is damaged" | Order details, item specs, damage evidence | OMS + Support Ticketing | Medium — image upload adds complexity |
| "Why was my refund rejected?" | Rejection reason, policy rule triggered | Refund Engine + Policy Engine | High — rejection reason codes often unstandardized |
| "When will my replacement arrive?" | Replacement order status, dispatch ETA | OMS + Logistics API | High — logistics data often in third-party systems |
| "Can I change my refund method?" | Payment method options, refund processing state | Payment Gateway + Finance | High — financial system access heavily restricted |

---

## 8. The Decision That Mattered Most: AI vs Deterministic Rules

This was the most important product decision in the entire case. And it's a decision most people skip.

**The question I kept asking:** For each step in the workflow, should this be handled by the AI (LLM), or by a deterministic rules engine?

The principle I landed on:

> AI should handle everything that requires understanding, empathy, and contextual language.  
> Deterministic rules should handle everything that requires correctness, compliance, and financial accuracy.

### My Decision Table

| Workflow Step | Who Should Own It | Why |
|---|---|---|
| Understanding user's complaint | AI | Requires natural language understanding, context, and nuance |
| Checking refund eligibility | Rules Engine | Policy is policy — must be 100% deterministic, auditable |
| Generating an empathetic response | AI | Requires tone awareness, personalization, situational language |
| Approving a refund | Finance System | Financial action — must be logged, rule-based, reversible |
| Detecting frustrated user | AI | Sentiment is a language understanding task |
| Escalating a high-risk case | Rules Engine (threshold) + AI (signal) | AI detects the signal; rules decide whether it crosses the threshold |
| Explaining next steps | AI | Communication is inherently a language task |
| Creating a support ticket | Backend CRM System | Structured action — deterministic, must be auditable |
| Fraud risk scoring | Separate ML risk model | Not a job for the general LLM |

### The Exact Problem I Was Trying to Prevent

If eligibility goes to the LLM instead of the rules engine:

```
User:    "Can I return this phone after 25 days?"
Policy:  20-day return window — NOT eligible.
LLM:     "Yes! You should be able to return it." (trying to be helpful)

Result:
→ Customer ships phone back
→ System rejects it on arrival
→ Customer is furious
→ Company either eats the cost or creates a worse support ticket than before
```

The fix is structural, not a prompt tweak:

```
Rules Engine: INELIGIBLE (25 days > 20-day window)
LLM receives that decision and communicates it:
"Unfortunately this order is outside our 20-day return window.
 Here's what I can help with instead: [options]"
```

Eligibility never touches the LLM. The LLM only communicates what the rules engine decided.

---

## 9. The Edge Case I Dug Into: Image Upload Flow

I specifically chose to dig into the damaged item + image upload flow because it's where the most assumptions collapse under pressure.

### When Image Upload Gets Triggered

- Customer reports damaged product
- Customer reports wrong item delivered
- Customer reports missing item / incomplete order
- Customer flags suspected counterfeit

### The Extended Flow

```
Customer opens chatbot
        ↓
States: "I received a damaged product"
        ↓
Bot identifies: intent = DAMAGED_ITEM_COMPLAINT
        ↓
Bot fetches recent orders or asks for Order ID
        ↓
System checks eligibility:
  → Return window open?
  → Does item category require visual evidence? (high-value: YES)
  → Does seller have enhanced verification in their policy?
        ↓
Bot requests image evidence:
"Please upload one photo showing the damage and one showing the full product."
        ↓
User uploads image(s) + explains issue in text
        ↓
        ┌──────────────────────────────────┐
        │       3 Paths After Upload       │
        └──────────────────────────────────┘
               /          |          \
              /           |           \
       Path 1:        Path 2:        Path 3:
   Damage clearly   Image unclear   High-risk /
   visible          or mismatched   Suspicious pattern
        ↓               ↓               ↓
  Eligibility      Ask for one      Escalate to
  check continues  better upload,   human agent,
        ↓          then escalate    pass all context
  Offer refund /       ↓            + images through
  replacement     Human queue           ↓
        ↓                           Manual review
  Customer confirms                 before decision
        ↓
  Ticket created,
  pickup scheduled,
  confirmation sent
```

### Systems I Had to Map for This Flow

| Step | System Involved |
|---|---|
| Image upload | Media / blob storage |
| Image validation (size, format, content check) | Media processing service |
| Damage detection | Computer vision model (separate from LLM) |
| Fraud pattern check | Risk scoring engine |
| Ticket creation with image attached | CRM / support ticketing |
| Audit trail | Compliance logging |

### The Three PM Decisions I Had to Make Explicitly

**Decision 1: Should an image alone trigger refund approval?**

No. I decided image evidence is one input into a multi-factor decision:

```
Decision = Image Evidence + Order Eligibility + Risk Score + Policy Rules
```

Single-factor approval on image alone is a fraud vector. Someone can photograph a damaged product they bought elsewhere and submit it against a valid order.

**Decision 2: What triggers mandatory human review regardless of image quality?**

I defined explicit thresholds:
- Item value above ₹5,000 → always human review
- Customer has 3+ previous refund claims in 90 days → risk flag → human review
- Image metadata doesn't match (wrong product visible, image taken months ago) → automatic escalation

**Decision 3: Should AI interpret the damage or just collect the evidence?**

For v1: AI collects, human or CV model interprets.
For v2+: Fine-tuned CV model classifies damage type and severity.
Never: General LLM both describing damage and making the approval decision simultaneously. That's where hallucination risk is highest.

---

## 10. Risks I Mapped Before Thinking About Launch

I built this risk register before writing any requirements — because requirements should be shaped by risk, not the other way around.

| Risk | Likelihood | Business Impact | Mitigation |
|---|---|---|---|
| AI approves an ineligible refund | Medium | High — financial loss + operational mess | Eligibility always routes to rules engine, never LLM |
| AI exposes another customer's order data | Low | Critical — GDPR violation | Identity verified before any data fetch |
| AI rejects a valid refund | Medium | High — customer trust damage | Always offer human escalation; log rejections for audit |
| Bot loops user without resolution | High | Medium — frustration, abandonment | Loop detection: 2 failed attempts → mandatory escalation |
| Fraud abuse through AI leniency | Medium | High — financial leakage | Risk score threshold required before any approval action |
| Duplicate refund processing | Low | High — accounting failure | Idempotency check in refund system before creation |
| Image submitted from a different order | Medium | High — fraud enablement | Cross-reference image metadata with order details |
| Compliance data exposure (PCI/GDPR) | Low | Critical — regulatory action | AI never receives full card data; masked fields only |

### Non-Negotiables I Would Put in the PRD as Hard Gates

1. Human escalation must be available at every point in the flow — no dead ends
2. Eligibility is never decided by the LLM — always the rules engine
3. Financial actions are initiated by AI but completed only by backend systems
4. Loop detection is mandatory — escalate after 2 unresolved intent cycles
5. High-value items (above ₹5,000) always require human review before approval
6. Identity verification is required before any personal order data is surfaced

---

## 11. How I Would Measure Success

### North Star Metric

**Human Handoff Rate for Refund/Replacement Sessions**

The percentage of refund and replacement chatbot sessions that escalated to a human agent.

Direction: decrease. This is the core business outcome — the chatbot should be resolving these sessions without needing a human.

### Supporting Metrics

| Metric | What It Tells Me |
|---|---|
| Human Handoff Rate | Whether AI is achieving self-resolution (primary) |
| Repeat Contact Rate | Whether the resolution actually held — customer contacting again = failed resolution |
| CSAT per chatbot session | Whether customers trust the AI resolution, or are just accepting it without satisfaction |
| Average Resolution Time | Is AI faster than human? By how much? |
| Intent Classification Accuracy | Is the routing correct? Everything else depends on this |
| First-Intent Resolution Rate | Did the first classification lead all the way to correct resolution? |

### Guardrail Metrics — Must Not Regress

| Guardrail | Threshold | If Breached |
|---|---|---|
| Refund Error Rate | < 0.5% | Pause experiment, audit eligibility logic immediately |
| CSAT | No more than 5% drop from baseline | Pause and investigate UX friction points |
| Fraud Rate | No increase vs. baseline | Immediate escalation to risk team |
| P95 Response Latency | < 3 seconds | Investigate API connection bottlenecks |

**Why guardrails exist:** Without them, optimizing for the North Star can silently destroy other business values. If I optimized only for reducing Human Handoff Rate, the AI might start auto-approving everything to avoid escalation. Fraud spikes. Finance escalates. Product gets shut down. Guardrails are the boundary conditions within which the primary metric is safe to optimize.

---

## 12. How I Would Run the Experiment

### Hypothesis

> If the chatbot is connected to real-time OMS and refund APIs, and eligibility is handled by a deterministic rules engine rather than the LLM, human handoff rate for refund-related sessions will decrease by at least 20% — without degrading CSAT or increasing refund error or fraud rates.

### Experiment Design

**Type:** A/B Test — 50/50 split on refund/replacement intent traffic

| Variable | Control | Treatment |
|---|---|---|
| Backend integration | None (current state) | OMS + refund API connected |
| Eligibility logic | LLM-based estimation | Deterministic rules engine |
| Image upload | Not available | Available for damaged item claims |
| High-value items | Same handling | Routed to human review |

### Decision Tree After Results

```
Primary metric improved ≥20% AND all guardrails held?
  → Full rollout. Expand to replacement + damaged item flows next.

Primary metric improved but by <20%, guardrails held?
  → Don't stop. Diagnose where sessions still fail:
     - Intent classification accuracy logs
     - API failure rates
     - Drop-off points in the conversation flow
  → Iterate and re-run.

Any guardrail breached?
  → Rollback immediately.
  → Root cause analysis before attempting again.

CSAT dropped even though primary metric improved?
  → Do not ship.
     Speed without trust is not a win in support.
     Customers accepting a faster wrong answer is worse than a slower right one.
```

---

## 13. What My PRD Would Look Like

### Problem Statement

Customers using the chatbot for refund and replacement queries still escalate to human agents at a high rate because the bot has no real-time data access, no deterministic eligibility logic, and no way to collect visual evidence for damage claims.

### Goal

Reduce human handoff rate for refund/replacement sessions by 20% within 60 days of launch — without degrading CSAT or increasing refund error or fraud rates.

### Scope

**In scope for v1:**
- Refund request flow (eligible orders, standard seller policy)
- Replacement request flow (standard policy, items under ₹5,000)
- Damaged item flow with image upload (items under ₹5,000)
- Real-time order status via OMS API
- Deterministic eligibility via rules engine
- Human escalation with full session context handoff

**Out of scope for v1:**
- Custom seller policy exceptions
- Partial refunds
- High-value item flows (>₹5,000) — manual review maintained
- Subscription cancellation
- Payment disputes

### Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Bot must verify user identity before surfacing any order data | P0 |
| FR-02 | Eligibility must be determined by the rules engine, not the LLM | P0 |
| FR-03 | Loop detection: after 2 failed resolution attempts, mandatory escalation | P0 |
| FR-04 | Human agent option must be available at every step in the flow | P0 |
| FR-05 | Escalation must pass full session context + intent history to the agent | P1 |
| FR-06 | Image upload supported for damaged item claims (max 3 images, 5MB each) | P1 |
| FR-07 | Bot must show ticket ID + resolution ETA after successful action | P1 |
| FR-08 | Status queries on existing tickets must use real-time OMS data | P1 |
| FR-09 | High-value items (>₹5,000) must always route to human review | P0 |
| FR-10 | No full payment card data accessible to the AI layer | P0 |

### Non-Functional Requirements

- P95 bot response latency: under 3 seconds
- Fallback: if OMS or refund API is unavailable, route entire session to human queue
- Session logs retained for 90 days for audit and retraining
- Zero PII in AI prompt context beyond masked fields

---

## 14. Mental Models I Built Through This

### The 8-Layer Decomposition

When an AI product fails, my default now is to decompose across all 8 layers before diagnosing. The failure almost never lives where it first appears.

```
Layer 1: User        → Did they want what we built?
Layer 2: UX          → Was the flow clear enough to use?
Layer 3: AI          → Did the model understand intent?
Layer 4: Data        → Did AI have access to real, live data?
Layer 5: Systems     → Were the right APIs connected?
Layer 6: Infra       → Was the system fast and reliable?
Layer 7: Security    → Was data access permitted?
Layer 8: Business    → Was the AI authorized to act?
```

### AI Handles Language. Rules Handle Decisions.

For any workflow step: does it require understanding, or does it require correctness? Understanding goes to the LLM. Correctness, compliance, and financial actions go to deterministic systems. Mixing these up is where AI products earn bad reputations.

### Data Quality Is the Foundation

Most AI product problems are actually data problems. A better model on bad data is still a bad product. Before I design AI behavior, I now ask: is the data available, real-time, consistent, and accessible? If any of those are no, that's where the work starts.

### Guardrails Before North Star

A primary metric without guardrails is just a way to find new failure modes faster. Guardrails are not an afterthought — they define the risk boundary within which optimization is actually safe.

### The Stakeholder Ecosystem Is the Product

Any feature decision affects multiple stakeholders simultaneously, and their incentives often conflict. Optimizing purely for the customer can quietly break operations, finance, or compliance. The product isn't just the screen — it's the entire system of incentives around it.

---

## 15. What I Would Do Differently

**1. Build the systems map before the user journey.**
I started with the user journey, then discovered system limitations that constrained what the journey could actually promise. I should have mapped available data and API access first, then designed the journey within those constraints.

**2. Make the AI vs rules boundary an explicit PRD artifact.**
I arrived at it through analysis, but it should be a formal, signed-off document — not an informal design decision. Every workflow step should have a documented, agreed owner: LLM or rules engine.

**3. Include fraud simulation as part of experiment design.**
I focused on how legitimate users would experience the flow. I should have explicitly modeled how a bad actor would try to exploit the AI — especially in the image upload path.

**4. Define escalation context as a formal standard.**
What gets passed to the human agent when the bot escalates? I specified that context must be passed, but didn't define the exact schema. Agents receiving vague escalations restart from scratch — which erases the value of any AI-assisted triage.

**5. Version the rules engine independently from the AI.**
Policy changes happen frequently. If the eligibility rules are baked into the AI model, every policy update requires model changes. They should be separate systems with separate deployment cycles.

---

