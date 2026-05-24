# TCR Dashboard — AI Booking Agent Case Study

https://claude.ai/public/artifacts/25b33c43-e8ed-4cf6-b847-217b951a7b1b


> **What this is:** A live interactive dashboard I built that simulates an AI booking agent, tracks Task Completion Rate in real time, breaks it intentionally, and shows the business cost of every failure.

> **Why I built it:** Any PM can quote "TCR should be 80%." This dashboard shows I *understand* what that number means, what breaks it, and what it costs the business.

---

## What I Built — Plain English

Imagine I am the PM at MakeMyTrip. I have an AI agent handling 24 booking tasks — flights, hotels, cancellations, seat upgrades, FAQ questions.

I open this dashboard and press **Run Simulation**.

The AI processes each task one by one. I watch in real time:
- Which tasks complete on their own (green ✓)
- Which tasks fail and need a human (red ✗ — human override, timeout, low confidence, error)

The moment all tasks are processed, I see:
- My overall TCR percentage
- Which *category* is underperforming (cancellations are weak by design)
- Which categories are below their threshold and need attention
- Exactly how much that costs the business per day

---

## The Two Tabs I Built

### Tab 1 — Dashboard

This is the command centre. Three things on this screen:

**1. The 4 metric cards at the top**

| Card | What it tells me |
|---|---|
| Task Completion Rate | The headline number — what % the AI completed without human help |
| Completed | How many tasks fully resolved by AI |
| Fallbacks | How many needed a human to step in |
| Pending | Tasks not yet processed |

**2. TCR by category (5 coloured cards)**

This is the most important part. The aggregate number hides problems. The breakdown reveals them.

| Category | Target threshold | Why that number |
|---|---|---|
| Flight booking | 90% | High money, irreversible — missing a flight is catastrophic |
| Hotel search | 85% | Medium risk |
| Cancellation | 85% | Customer trust at stake |
| FAQ answer | 70% | Low risk — customer just asks again |
| Seat upgrade | 80% | Medium risk |

If any category drops below its threshold, a red alert fires. This is how I would monitor AI performance as a PM — not one number, but segmented by risk.

**3. The task list at the bottom**

Every single task, its category, its status, and the reason for failure. Four filter buttons: All / Completed / Fallbacks / Pending. This is the audit trail — what I would show engineering when something breaks.

---

### Tab 2 — Business Impact

This tab answers the question leadership always asks: *"What does this actually cost us?"*

Two sliders I built:
- Tasks per day (default 10,000)
- Cost per human-handled task (default ₹200)

As I drag, the numbers update live:

| What I see | What it means |
|---|---|
| Human tasks/day | How many tasks still need human agents |
| Daily agent cost | What I am paying for those humans |
| Annual agent cost | The yearly bill |
| Savings vs 70% baseline | How much better I am doing than a broken system |

The comparison table shows every TCR level from 60% to 95% — daily cost, annual cost — so I can walk into any meeting and say exactly what a 5% improvement is worth.

**The number I would use in any PM interview:**

At 10,000 tasks/day and ₹200 per human task — every 10% TCR improvement saves **₹2,00,000 per day**. That is ₹7.3 Cr per year.

---

## The 3 Buttons I Built on the Left Sidebar

### ▶ Run Simulation

Starts the AI agent. Processes all 24 tasks one by one. I watch the status update in real time. Each task gets a result based on realistic success rates per category.

Success rates I set (before breaking):
- FAQ answers: 95%
- Hotel search: 92%
- Flight booking: 88%
- Seat upgrade: 80%
- Cancellations: 61% ← intentionally weak

I set cancellations to 61% on purpose. This triggers the alert and shows that aggregate TCR can look healthy while one category is failing badly.

### ⚡ Inject Break

This is the most important button I built for demonstrating production failures.

Click it and run the simulation again. The AI now performs much worse — cancellations drop to 20%, flights to 50%. Multiple categories fire red alerts.

This simulates what happened at MakeMyTrip during Diwali week — peak traffic, overwhelmed system, silent failures everywhere.

As a PM, I need to have seen this break to understand production in a way that reading about it cannot teach.

### ↺ Reset

Clears everything. Start fresh.

---

## The Fallback States I Defined — Why They Matter

When a task fails, it does not just "fail." It fails for a specific reason. I track all of them:

| Status | What it means in real life |
|---|---|
| `human_override` | Customer escalated, human agent took over |
| `timeout` | AI took too long, connection dropped |
| `low_confidence` | AI was not sure, escalated automatically |
| `error` | System failure — API crashed, database unreachable |
| `customer_abandoned` | Customer gave up and left |

**Why I defined all five:** If I only track "human_override" as a fallback — timeouts and errors get counted as completions. TCR looks great. The system is silently broken. This is Break #3 from the MakeMyTrip story.


---

## How to Run It

Download `index.html` from this repo. Open it in any browser — Chrome, Safari, Firefox. No installation needed.

```bash
open index.html
```


---

## My Builder Loop for This Project

| Step | What I did |
|---|---|
| Learn | TCR = % tasks AI completes without human help |
| Explain simply | MakeMyTrip story — Rahul's cancelled flight that was never cancelled |
| Tiny build | Python tracker + this HTML dashboard |
| Break intentionally | Built the Inject Break button — 3 failure modes simulated |
| Fix it | Outcome verification, fallback taxonomy, risk thresholds |
| Business thinking | Every 10% lift = ₹2L/day saved |
