# Task Completion Rate (TCR) — AI Product Case Study

https://excalidraw.com/#json=<your-file>

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

## The Problem I Was Solving

I was the PM at MakeMyTrip. I had just launched an AI chatbot to handle flight bookings, cancellations, and hotel searches.

The promise I made to leadership: *AI handles it. Humans don't have to.*

My dashboard showed **95% TCR**. I presented it to the board. Everyone was happy.

Then support tickets started spiking. Customers were furious. Something was very wrong — and I had no idea because I was trusting the wrong numbers.

---

## Who Was Feeling the Pain

| Stakeholder | What happened |
|---|---|
| **Rahul (customer)** | Asked AI to cancel his flight. AI said "Done!" Booking was still active. He found out at the airport. |
| **Support agents** | Spending all day fixing tasks the AI claimed it completed. |
| **Me (PM)** | Reported great numbers to leadership. Had no idea they were fake. |
| **Business** | Still paying for the same 10 human agents. AI vendor cost added on top. ROI never arrived. |

---

## What is TCR — In Simple Words

> Out of every 100 tasks I give the AI, how many does it finish on its own — without a human stepping in?

```
TCR = Tasks completed without human fallback
      ─────────────────────────────────────
              Total tasks attempted
```

**Example:** Rahul and 99 others ask the AI to cancel their flights. 88 cancellations go through correctly. 12 fail. **TCR = 88%.**

| TCR | What it means |
|---|---|
| Below 70% | AI costs more than it saves |
| 80% | Industry baseline — PM interview benchmark |
| 90%+ | Production-grade — AI genuinely replacing human effort |

---

## The 3 Ways TCR Broke — And How I Found Each One

### Break #1 — The AI Was Lying (Metric Gaming)

**What happened in plain English:**

Rahul opened the MakeMyTrip chatbot and typed: *"Cancel my flight BOM-DEL booking #4821."*

The AI replied: *"Done! Your booking has been cancelled. Refund of ₹4,200 in 5–7 days."*

Rahul said thanks and closed the app.

**What actually happened behind the scenes:**

The cancellation API call failed silently. The booking was never cancelled. It was still active in the database. The AI got no confirmation back — but reported success anyway because I had not built any verification step.

**What I saw on my dashboard:** TCR = 95% ✓

**What was actually happening:** Rahul showed up at the airport. His booking was still active. He could not board his new flight. He called support — furious. 340 other customers had the same problem that week.

**What I learned and fixed:**

After the AI says "done", I needed to check the actual database independently.

- Did the booking status actually change to CANCELLED?
- Did the refund actually initiate?

If not — it is a failure. Mark it as a fallback. I learned never to trust the AI's own report. The AI cannot grade its own homework.

---

### Break #2 — The Denominator Trick (Cherry-Picked Tasks)

**What happened in plain English:**

Three months in, my engineer noticed TCR was still low on cancellations. Instead of fixing the actual problem, he quietly changed the routing logic: only send **easy tasks** to the AI — simple FAQ questions, hotel searches, basic seat upgrades.

Hard tasks — cancellations, rebookings, refund disputes — were silently pre-routed to human agents **before** the AI even saw them.

**What I saw on my dashboard:** TCR = 94% ✓ Amazing numbers!

**What was actually happening:**

1,400 hard tasks every day were going directly to humans and not being counted at all. The AI looked brilliant — 94% on the easy stuff it was allowed to try. Meanwhile humans were still doing all the difficult work.

The "AI savings" I was presenting in my slides were fictional.

**How I caught it:**

I pulled the full task log — not just what went to the AI, but every customer request that came in. I saw 1,400 requests that never touched the AI at all.

I segmented the TCR:
- FAQ answers: 94% ✓
- Hotel search: 91% ✓
- Cancellations: 0% — because they were never attempted

**What I fixed:**

I changed the measurement to use a random, unfiltered sample of ALL requests — not just the ones the AI was allowed to try. I learned: cherry-picking the input destroys the metric.

---

### Break #3 — Ghost Completions (Timeouts Counted as Success)

**What happened in plain English:**

Diwali week. Massive traffic spike. The AI booking agent got overwhelmed.

A customer asked to book a flight. The AI started processing. The backend API took 31 seconds to respond. My timeout threshold was 30 seconds. Connection dropped. The screen went blank.

The customer got no confirmation. No error message. Just silence.

**What my code was doing (the bug I found):**

```python
# My incomplete fallback list
FALLBACK_STATUSES = ["human_override"]

# The bug: if status is not in the list, count as completed
if status not in FALLBACK_STATUSES:
    completed += 1   # timeout silently becomes a "completion"
```

Because "timeout" was not in my fallback list, my code assumed silence = success. Ghost completion.

**What I saw on my dashboard:** TCR = 84% ✓

**What was actually happening:**

800 tasks timed out during Diwali week. All 800 were counted as completions. Real TCR was 68%. My dashboard was lying by 16 percentage points.

**What I fixed:**

I named every possible failure explicitly. If it is not on the success list, it is a fallback.

```python
# My complete fallback taxonomy
FALLBACK_STATUSES = [
    "human_override",      # agent stepped in
    "timeout",             # AI took too long
    "low_confidence",      # AI not sure, escalated
    "error",               # system failure
    "customer_abandoned"   # customer gave up
]
```

I learned: anything not explicitly a success is a fallback. Silence is not success.

---

## How I Fixed Everything — My PM Approach

### Step 1 — I stopped looking at the aggregate

| Category | TCR | Status |
|---|---|---|
| FAQ answers | 91% | ✓ Fine |
| Flight booking | 79% | ⚠ Watch |
| Cancellations | 58% | ✗ Crisis |

My overall TCR was 82% — looked fine. But cancellations at 58% was a crisis I had missed. I focused all engineering effort there first. The aggregate number was hiding the real problem from me.

### Step 2 — I set different thresholds per risk level

| Task | Threshold I set | Why |
|---|---|---|
| Flight booking | 90%+ | High money, irreversible — missing a flight is catastrophic |
| Cancellations | 85%+ | Customer trust at stake |
| FAQ answers | 70% | Low risk — customer just asks again |

I had been using one threshold for everything. That was wrong. A flight booking failure and an FAQ failure are not the same thing.

### Step 3 — I translated it to money for leadership

At 10,000 tasks/day and ₹200 per human-handled task:

| TCR | Human tasks/day | Daily cost |
|---|---|---|
| 70% | 3,000 | ₹6,00,000 |
| 80% | 2,000 | ₹4,00,000 |
| 90% | 1,000 | ₹2,00,000 |

My pitch to leadership: *"Fixing cancellations from 58% to 85% saves ₹1.8 Cr per year. That is the engineering sprint I am asking budget for."*

### Step 4 — I moved from monthly reviews to weekly alerts

A 3% drop week-over-week means something changed. I set up an alert that fires the moment any category drops 3% in a week. Customers feel it in week 1. I needed to catch it in week 1, not month 3.

---

## Business Impact

**Every 10% TCR lift = ₹2,00,000 saved per day** at 10,000 tasks/day.

That is ₹7.3 Cr per year from fixing one metric.

---

## What Real Products Do With TCR

| Product | What they call it | Key insight |
|---|---|---|
| Yellow.ai | Task Completion Rate | 80% = enterprise baseline. PM interviews probe threshold design. |
| Haptik | TCR + Deflection Rate | High deflection + low TCR = red flag. AI deflects but does not resolve. |
| Intercom Fin | Resolution Rate | 45–50% baseline, rising to 70%+ with custom training. |
| Zendesk AI | Autonomous Resolution Rate | Below 60% means AI creates more work than it saves. |

---

## The Interview Answer I Would Give

Most candidates say:
> *"TCR should be above 80%."*

What I would say:
> *"I segment by task category and risk level, set different thresholds per category, and alert when any segment drops 3–5% week-over-week — not just when the aggregate falls below 80%. Aggregate TCR is a lagging indicator. Segmented, threshold-checked TCR is an early warning system."*

---

## What I Learned

- TCR is not about what the AI says. It is about what actually happened in the system.
- I should never let the AI grade its own homework. I must verify outcomes independently.
- Aggregate TCR hid my biggest problem. Segmenting by category revealed it.
- Silence is not success. I must name every failure mode explicitly.
- Every 10% TCR lift at 10k tasks/day = ₹2,00,000 saved per day.
- Breaking the system intentionally taught me more than any document could.

---

## My Builder Loop for This Project

| Step | What I did |
|---|---|
| Learn | TCR = % tasks AI completes without human help |
| Explain simply | MakeMyTrip story — Rahul's cancelled flight that was never cancelled |
| Tiny build | Python tracker + live HTML dashboard |
| Break intentionally | 3 failure modes — I broke each one myself |
| Fix it | Outcome verification, fallback taxonomy, risk thresholds |
| Business thinking | Every 10% lift = ₹2L/day saved |
| Push to GitHub | This repo |
| Case study | This file |


---
