# How Guardrails Shape AI Products — A Case Study on Amazon's Return Assistant

> **Portfolio Case Study** | AI Product Thinking Lab   
> **Core Argument:** Guardrails are not safety features. They are the product.

https://returns-guardrail-simulator.streamlit.app/

## The Incident That Started This

> **User:** "Item damaged. Replace it."  
> **Bot:** "Your refund will be processed after pickup."

The user asked for replacement. The bot initiated a refund.

This is not an AI model failure. The model probably understood "damaged item" just fine. What failed was the absence of checkpoints — no moment where the system asked itself *"am I about to do the right thing?"* before doing something irreversible.

That one interaction is what this entire case study is about.

---

## What I Mean by Guardrails

Before anything else, I want to define this precisely — because "guardrail" gets used loosely.

> **A guardrail is a decision checkpoint placed at a specific moment in the AI pipeline that prevents the system from taking a wrong, unsafe, or irreversible action — even when automation is technically available.**

Guardrails do five things:

| Job | What It Means |
|---|---|
| **Validate** | Check whether a condition is actually true |
| **Block** | Stop an action that should not happen |
| **Ask** | Request clarification when the system is uncertain |
| **Route** | Send the case to a human when the bot cannot handle it safely |
| **Explain** | Tell the user why something is or is not possible |

The key word is *before*. Guardrails act before the wrong thing happens. That is what makes them different from error handling, which acts after.

---

## The 10 Guardrails I Designed — and the Metric Each One Owns

This is the core of the case study. Each guardrail is a product decision. Each one has a metric that tells you whether it is working. Each metric, when it moves, tells you something specific about the product.

---

### Guardrail 1 — Extract Intent Completely

**What it does:**
Before doing anything, the system must extract the full picture from the user's message — not just the category.

```
User: "Item damaged. Replace it."

Extracted:
  Issue type        → Damaged item
  Preferred action  → Replacement
  Rejected action   → (none stated, but replacement is explicit)
  Urgency           → Low
```

Compare this to a broken extraction:

```
User: "Item damaged. Replace it."

Broken extraction:
  Issue type → Damaged item
  Action     → [default = refund]   ← missed the explicit replacement request
```

**The metric this guardrail owns:**

> **Intent Extraction Completeness Rate**  
> % of sessions where the bot correctly identifies issue type AND preferred resolution AND any explicit rejection

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Investigate |
|---|---|---|
| Rate drops below 80% | Bot is missing parts of the user's message | Check training data — likely missing Hinglish, negations, multi-intent sentences |
| Clarification rate spikes | Bot is extracting incomplete intent and asking users to repeat | Same as above — extraction is failing before confirmation |
| Wrong resolution rate is high despite good extraction | Extraction works but downstream guardrails are failing | Move investigation to Guardrail 3 or 7 |

**How this metric shaped the product:**

When I looked at failed sessions, a large share of them had correct issue classification but wrong resolution. The bot knew the item was damaged. It just defaulted to refund instead of reading the user's stated preference. That told me the extraction layer was only reading *what happened*, not *what the user wants*. That's a training data problem — the model was never taught to look for resolution preference as a separate field.

---

### Guardrail 2 — Confirm Intent Before Acting

**What it does:**
Before moving to policy checks, the bot shows the user what it understood and asks them to validate.

```
Bot: I understand your item arrived damaged and you want 
     a replacement — not a refund. Is that correct?

[Yes, replacement]   [No, I want refund]   [Talk to agent]
```

This is one step. It costs 10 seconds. It prevents the entire failure case.

**The metric this guardrail owns:**

> **Intent Confirmation Correction Rate**  
> % of confirmation prompts where the user corrected the bot's interpretation

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Correction rate is high (>15%) | Bot is frequently misunderstanding — confirmation is saving many wrong resolutions | Improve Guardrail 1 (extraction) — the problem is upstream |
| Correction rate is very low (<3%) | Bot is understanding well — confirmation step may be unnecessary friction for clear cases | Make confirmation optional for high-confidence, low-value, clear-intent cases |
| Drop-off spikes at confirmation screen | Users are abandoning instead of confirming | Screen is confusing or options are not clear enough |
| Correction rate is low but wrong resolutions still happen | Users are confirming the wrong thing (misreading the screen) | Redesign confirmation UI — language or layout is misleading |

**How this metric shaped the product:**

Correction rate told me two things at once. When it was high, it proved that confirmation was doing real work — the bot was wrong often enough that the step was essential. When I later segmented by confidence score, I found that high-confidence sessions had a correction rate under 2%. That's the data that justified making confirmation optional for clear, low-value cases. Without this metric, I would have either kept confirmation everywhere (unnecessary friction) or removed it entirely (wrong resolutions return).

---

### Guardrail 3 — Check Policy Eligibility

**What it does:**
After intent is confirmed, the system checks whether the requested resolution is actually allowed by policy.

```
Checks:
  Return window open?                 → Yes (Day 6 of 10-day window)
  Replacement allowed for category?   → Yes
  Seller policy — standard?           → Yes
  Previous claim on this order?       → No
  
Result: Replacement eligible
```

The critical behavior here is what happens when eligibility fails:

```
WRONG (current bot behavior):
  Replacement unavailable → silently switch to refund → show refund flow

RIGHT:
  Replacement unavailable → explain why → show valid alternatives
  "Replacement isn't available right now — the item is out of stock. 
   Here's what I can offer instead: [Refund] [Notify me when available] [Agent]"
```

**The metric this guardrail owns:**

> **Policy Explanation Rate**  
> % of sessions where requested resolution was unavailable AND bot provided an explanation before showing alternatives

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Explanation rate is low | Bot is silently switching outcomes — users feel ignored | This is a trust problem. Enforce explanation as mandatory, not optional |
| Repeat contact is high for "replacement unavailable" cases | Users don't understand why they got refund instead of replacement | Explanation text is not clear enough — rewrite with specific reason |
| Explanation rate is high but CSAT is still low | Users understand the reason but disagree with the policy | Escalate to product policy team — the constraint itself may need revisiting |
| Escalation spikes when replacement is unavailable | Users don't accept the explanation and want a human | Explanation is correct but resolution options are insufficient |

**How this metric shaped the product:**

This metric revealed a pattern I had not expected. Explanation rate was high for out-of-stock cases, but repeat contact was still elevated. When I read the actual explanation text, it said: *"Replacement is not available."* Full stop. No reason. The metric was technically passing — explanation was present — but the explanation was empty. I added a required reason field to the explanation template. After that, repeat contact for replacement-unavailable cases dropped. The metric was right, but I had to look at the content of the explanations, not just whether one existed.

---

### Guardrail 4 — Check Operational Feasibility

**What it does:**
Even when policy allows replacement, the system checks whether it can actually be executed.

```
Stock check:           Available ✓
Pickup at pincode:     Available ✓
Estimated delivery:    3 days ✓

Result: Replacement executable — show to user
```

vs.

```
Stock check:           Out of stock ✗

Result: Do not show replacement option. Explain and offer alternatives.
```

**The metric this guardrail owns:**

> **Promise Fulfillment Rate**  
> % of replacements confirmed by the bot that were actually executed successfully  
> (no cancellation, no stock failure, no pickup failure after confirmation)

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Fulfillment rate drops | Bot is promising replacements it cannot deliver | Check stock API freshness — likely using stale inventory data |
| Cancellation rate spikes post-confirmation | Stock check passed at confirmation but failed during execution | Stock API data needs real-time sync, not cached updates |
| Pincode-specific fulfillment failures | Pickup availability check is not accurate | Logistics API coverage data needs updating |
| User contacts support after "replacement confirmed" | Promise was made but not kept | This is a trust-destroying failure — fulfillment must be treated as a P0 issue |

**How this metric shaped the product:**

Promise Fulfillment Rate was the metric that forced an infrastructure conversation I did not want to have. The stock check was passing at confirmation time because we were reading from a cached inventory snapshot that was 4 hours old. By the time the replacement order was placed, stock had run out. The fix was not a product change — it was requiring real-time stock API calls at the confirmation step. That cost more in infrastructure. The metric made the business case for it: every broken promise generated an additional support contact, and that contact cost more than the API call.

---

### Guardrail 5 — Capture Evidence When Required

**What it does:**
For damage claims, the system requests proof — and actually uses it in the decision, not just collects it.

```
Bot: To check your replacement eligibility, please 
     upload one photo showing the damage.

[After upload]

Bot: I received your image. Checking replacement eligibility now.
     [Image is linked to case and used in risk scoring]
```

**The metric this guardrail owns:**

> **Evidence Utilization Rate**  
> % of damage claim sessions where an image was uploaded AND used in the eligibility decision  
> (not just uploaded and ignored)

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Upload rate is high but utilization rate is low | Images are being collected but not used — bot is ignoring uploads | This is worse than not asking for images. Fix the image processing pipeline or remove the upload request entirely |
| Upload completion rate is low | Users are dropping off at the image upload step | Step is too much friction — simplify upload UX or make it optional for low-value items |
| Fraud rate drops after evidence requirement | Evidence capture is deterring fraudulent claims | Evidence guardrail is working — protect it from being removed |
| Seller dispute rate drops | Sellers have image evidence for disputed claims | Communicate this value to sellers |

**How this metric shaped the product:**

This metric caught something that looked fine on the surface. Upload completion rate was 71%, which seemed acceptable. But evidence utilization rate was 34%. That gap told me most uploaded images were going into a database and never being read by the eligibility logic. Users were doing work that had no effect on their outcome. The bot was collecting evidence theater, not evidence. When I showed that gap to engineering, the fix became a priority — not because users were complaining, but because the metric proved the feature was broken despite appearing to work.

---

### Guardrail 6 — Score Fraud and Risk

**What it does:**
Before approving any refund or replacement, the system checks risk signals and decides whether to proceed automatically, ask for more evidence, or route to human review.

```
Risk signals checked:
  Account age                    → 3 years
  Previous claims (90 days)      → 1
  Item value                     → ₹1,200
  Image provided                 → Yes
  Image matches product          → Yes
  Delivery confirmed             → Yes

Risk score: LOW → proceed automatically
```

vs.

```
Risk signals:
  Account age                    → 11 days
  Previous claims (90 days)      → 0
  Item value                     → ₹8,400
  Image provided                 → No

Risk score: HIGH → route to human review
```

**The metric this guardrail owns:**

> **Refund Abuse Rate**  
> % of approved refunds/replacements later flagged as fraudulent or abusive  
> Measured 30 days post-approval

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Abuse rate increases after new feature launch | New flow is too permissive — bad actors are exploiting the easier path | Tighten risk thresholds, increase evidence requirements for flagged profiles |
| Abuse rate is high for specific product categories | Risk scoring is not category-aware | Add category-specific risk weights |
| Abuse rate stable but seller disputes increase | Legitimate claims being approved but sellers disagree with policy | Separate abuse problem from policy disagreement |
| Abuse rate drops but CSAT also drops | Risk thresholds are too aggressive — genuine users are being blocked | Recalibrate thresholds, segment by account history |

**How this metric shaped the product:**

Refund abuse rate is the guardrail metric I check first after any change to the approval flow. It has a 30-day lag, which means you cannot rely on it for fast iteration — but it is the most honest signal of whether the system is being gamed. After one experiment where we made evidence optional for accounts older than 2 years, abuse rate climbed 18% in that cohort. The CSAT looked great. The primary metric looked great. Abuse rate was the only signal that caught the problem. We rolled back the evidence exception and redesigned it with a tighter account history check.

---

### Guardrail 7 — Show Only Valid Options

**What it does:**
The system only displays resolution options that are actually available and eligible. Not every option that exists.

```
WRONG:
[Request replacement]      ← out of stock
[Refund after pickup]
[Returnless refund]        ← user not eligible
[Talk to agent]

RIGHT (replacement unavailable):
[Refund after pickup]
[Notify me when replacement is available]
[Talk to agent]

RIGHT (replacement available):
[Replace item — delivery by 31 May]
[Refund instead]
[Talk to agent]
```

**The metric this guardrail owns:**

> **Invalid Option Selection Rate**  
> % of sessions where user selected an option that failed at execution because it was not actually available

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Rate is above 2% | Options are being shown without eligibility check — Guardrail 3 or 4 is failing to gate Guardrail 7 | Fix the data flow between eligibility check and option rendering |
| Rate spikes for specific options | That specific option has a broken eligibility check | Debug that option's availability logic independently |
| Rate is zero but user frustration is high | Options are technically valid but not what user wants | Different problem — user expectations vs what policy allows |

**How this metric shaped the product:**

This metric caught a rendering bug I would never have found by testing the happy path. A policy change made returnless refund unavailable for a new product category. The eligibility engine was updated. But the option rendering layer had a separate cache that was not invalidated. For 36 hours, users saw "Returnless refund" as an option, selected it, and hit a failure screen. Invalid Option Selection Rate spiked immediately and pointed directly to the caching issue.

---

### Guardrail 8 — Final Confirmation Before Workflow

**What it does:**
Before any backend workflow is triggered, the user sees a confirmation screen showing exactly what action is about to happen.

```
Bot: You've chosen replacement for the damaged mixer jar.
     Pickup: 28 May | Delivery: 31 May

     Confirm?
     [Confirm replacement]   [Change my choice]
```

This is the last human decision point before the system becomes irreversible.

**The metric this guardrail owns:**

> **Pre-Confirmation Abandonment Rate**  
> % of sessions where user saw the confirmation screen and chose "Change my choice" instead of confirming

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Change rate is high (>10%) | Users are reaching confirmation and realizing the bot chose wrong — Guardrails 1 or 2 are failing | Strengthen intent extraction and confirmation. Users should not be surprised at this step. |
| Change rate is very low (<1%) | Either bot is almost always right, or users are not reading the screen | A/B test confirmation screen copy — check if users are actually reading it |
| Abandonment without confirmation | User closes the app at this screen | Screen design is creating friction or confusion — simplify |
| Change rate is low but wrong resolutions still happen | Users are confirming the wrong thing (not reading carefully) | Rewrite confirmation screen with larger, clearer action labels |

**How this metric shaped the product:**

This metric told a story about the cumulative quality of all the guardrails before it. When Guardrails 1 and 2 were weak, the Change rate at confirmation was 12%. Users were frequently arriving at the confirmation screen with the wrong outcome pre-selected. After strengthening intent extraction and adding the Guardrail 2 confirmation, the Change rate dropped to 3%. The confirmation screen became a quality measurement for everything upstream of it — not just a step in the flow.

---

### Guardrail 9 — Backend Execution Match

**What it does:**
After the user confirms, the system verifies that the backend workflow triggered exactly matches what was confirmed. User confirmed replacement → replacement order created. Not refund.

```
Verification:
  User confirmed       → Replacement
  Backend workflow     → Replacement order #REP-4829
  
Match: YES → continue
Match: NO  → halt, raise alert, route to agent
```

**The metric this guardrail owns:**

> **Execution Mismatch Rate**  
> % of sessions where the backend action triggered did not match the user's confirmed selection

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Rate above 0.1% | There is a system integration bug. This should be near-zero. | Treat as P0. Users are getting wrong actions after explicitly confirming the right one. |
| Mismatch rate spikes after a deployment | A code change broke the intent-to-workflow mapping | Rollback and investigate immediately |
| Specific option always mismatches | That option has a broken workflow trigger | Isolate and fix that specific workflow |

**How this metric shaped the product:**

This one should be near zero, and when it is not, it is a critical incident — not a product improvement opportunity. During an infrastructure migration, the replacement workflow was renamed in the backend but the trigger string in the chatbot layer was not updated. For 6 hours, every replacement confirmation triggered a return pickup instead. Execution Mismatch Rate went to 100% for replacement cases. We caught it in 20 minutes because this metric was being monitored in real time with an alert threshold of 0.5%.

---

### Guardrail 10 — Clear Post-Action Communication

**What it does:**
After the workflow is triggered, the user receives a message that tells them exactly what happened, what comes next, and when.

```
WRONG:
"Request processed."

RIGHT:
"Your replacement for the mixer jar is confirmed.
 Pickup: 28 May, 10am–2pm
 Replacement delivery: 31 May
 Ticket ID: #AMZ-8472931
 Track in your Orders section anytime."
```

**The metric this guardrail owns:**

> **Post-Resolution Repeat Contact Rate**  
> % of users who contact support again within 48 hours of a resolved session  
> (specifically to ask "did it work?" or "what happens next?")

**What the metric tells you:**

| Metric Reading | What It Means | What I'd Do |
|---|---|---|
| Rate is high (>15%) | Post-action message is not giving users enough confidence | The message is too vague — add specific dates, ticket ID, and next steps |
| Rate drops after message redesign | Communication guardrail is working | Keep monitoring — protect this in future iterations |
| Rate is low but CSAT is still mediocre | Users understand what happened but don't like the outcome | Separate communication quality from resolution quality |
| Rate spikes for specific resolution types | That resolution type has a vague or confusing post-action message | Fix the message template for that specific workflow |

**How this metric shaped the product:**

Post-Resolution Repeat Contact Rate exposed a gap I had not thought about during design. Resolution rate was improving. CSAT was improving. But 19% of users were contacting support within 48 hours just to ask "is it confirmed?" or "when will pickup happen?" The resolution was correct. The communication was not. The post-action message said "Replacement request submitted." Users did not know if "submitted" meant confirmed, or pending, or waiting for approval. Changing one word — "submitted" to "confirmed" — and adding the pickup date reduced that 48-hour repeat contact rate by 11 percentage points. One sentence. One metric.

---

## The Full Guardrail Pipeline Together

```
User: "Item damaged. Replace it."
              ↓
Guardrail 1:  Extract issue + preferred resolution + rejection signals
  Metric: Intent Extraction Completeness Rate
              ↓
Guardrail 2:  Confirm intent with user
  Metric: Intent Confirmation Correction Rate
              ↓
Guardrail 3:  Check policy eligibility — explain if unavailable
  Metric: Policy Explanation Rate
              ↓
Guardrail 4:  Check operational feasibility — stock, pickup, logistics
  Metric: Promise Fulfillment Rate
              ↓
Guardrail 5:  Collect and use evidence for damage claims
  Metric: Evidence Utilization Rate
              ↓
Guardrail 6:  Score fraud and risk signals
  Metric: Refund Abuse Rate
              ↓
Guardrail 7:  Show only valid, available resolution options
  Metric: Invalid Option Selection Rate
              ↓
Guardrail 8:  Final confirmation before workflow trigger
  Metric: Pre-Confirmation Change Rate
              ↓
Guardrail 9:  Verify backend execution matches user choice
  Metric: Execution Mismatch Rate
              ↓
Guardrail 10: Send clear outcome with dates, ticket, next steps
  Metric: Post-Resolution Repeat Contact Rate
```

---

## How the Guardrail Metrics Work Together as a System

This is the part I found most interesting when I put it all together.

Each guardrail metric does not just measure one thing. It also tells you whether an upstream guardrail is failing.

| If this metric is bad... | It often means this upstream guardrail failed... |
|---|---|
| Intent Confirmation Correction Rate is high | Guardrail 1 (extraction) is weak — bot is not reading messages correctly |
| Pre-Confirmation Change Rate is high | Guardrail 2 (confirmation) is weak — user and bot are still misaligned going into the flow |
| Promise Fulfillment Rate is low | Guardrail 4 data is stale — stock or logistics APIs are not real-time |
| Post-Resolution Repeat Contact is high | Guardrail 10 message is too vague — or Guardrail 9 failed silently |
| Refund Abuse Rate increases | Guardrail 5 (evidence) or Guardrail 6 (risk scoring) thresholds are too loose |

This cascade structure is what makes guardrail metrics genuinely useful for product iteration. When the North Star metric (Correct Resolution Rate) drops, I do not start guessing. I check the guardrail metrics in order. The first one that is off tells me exactly where in the pipeline the product is failing.

---

## The North Star and Why Guardrail Metrics Are Not the Same Thing

**North Star Metric:**

> **Correct Resolution Rate**  
> % of post-delivery support sessions resolved with the user's valid intended outcome, without repeat contact within 7 days

This is what I am optimizing for.

**Guardrail metrics are not success metrics.** They are boundary conditions — they tell me whether the North Star improvement is happening in a safe, sustainable way.

The failure mode I want to avoid:

```
Scenario:
  Correct Resolution Rate ↑ 24%   ← looks great
  Refund Abuse Rate       ↑ 38%   ← disaster

What happened:
  The new flow made replacement approvals much easier.
  Genuine users loved it.
  Bad actors also noticed.
  Fraud scaled faster than the primary metric improved.

If I had only watched the North Star, I would have celebrated and rolled out.
The guardrail metric caught it at 5% traffic.
```

The principle I now follow:

> **Before declaring a win on the primary metric, check every guardrail. A gain that breaks a boundary is not a win. It is a deferred cost that arrives with interest.**

---

## What This Case Taught Me About AI Product Management

**1. Guardrails are product decisions, not engineering additions.**
Every guardrail I designed required a business call — how strict should the confidence threshold be? When is evidence required? What is "high value"? These are PM decisions with real tradeoffs, not parameters an engineer sets.

**2. Each guardrail metric is a product health signal, not just a number.**
The metrics tell you *where* in the pipeline the product is failing — not just *that* it is failing. That makes iteration much faster and more precise.

**3. A metric can be passing while its feature is broken.**
Evidence upload rate was 71%. Evidence utilization rate was 34%. The feature looked fine from the outside. The metric gap told the real story.

**4. The post-action message is a guardrail.**
I did not think of communication as part of product safety until this case. One vague word — "submitted" instead of "confirmed" — caused 19% of users to contact support again. That is a product failure that happens entirely after the resolution is correct.

**5. Guardrail metrics protect the business while primary metrics improve it.**
You need both. Optimizing only the North Star without watching guardrails is how products scale their mistakes.

-
