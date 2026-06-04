# AI Support Bot — Image Upload Drop-off Analysis

## 1. Product Context

An e-commerce platform uses an AI customer support bot to help users report order-related issues such as damaged items, wrong items, missing items, delivery delays, refund requests, and replacement requests.

In the damaged item flow, the bot asks the user to upload an image of the damaged product before offering a refund, replacement, or agent review.

The expected user journey is simple:

```text
User reports damaged item
↓
Bot detects damaged_item intent
↓
Bot asks for image proof
↓
User uploads image
↓
System analyzes image
↓
Bot confirms next step
↓
Refund/replacement/agent review is offered
↓
Case is closed or escalated
```

However, a possible product failure occurs when users abandon the chat after the image upload step.

This case study analyzes that failure from a GenAI Product Analyst perspective using:

* User journey mapping
* Failure hypothesis generation
* Event tracking
* Product metrics
* GenAI metrics
* SQL analysis
* Product recommendations
* Business impact thinking

---

## 2. Problem Statement

Users reporting a damaged item may abandon the AI support chatbot after the bot asks them to upload an image.

The failure may not be that users refuse to upload images. A deeper failure may be:

```text
User uploads the image
↓
Bot fails to acknowledge the upload
↓
Bot asks for the image again
↓
User becomes frustrated
↓
User abandons the chat
```

This indicates a breakdown between user action, system state, image analysis, and chatbot conversation flow.

The key product problem is:

> The chatbot may correctly understand the user's intent, but the support journey still fails because the bot does not handle the image upload step properly.

---

## 3. Objective

The objective of this case study is to analyze image upload drop-off in an AI support bot and identify where the journey breaks.

The analysis aims to answer:

1. Are users reaching the image request step?
2. Are users uploading the image after the bot asks for it?
3. Are users abandoning after the image request?
4. Are some users uploading the image but still being asked again?
5. Is this a user behavior issue, a UX issue, a technical issue, or a GenAI/system-state issue?
6. What product changes can reduce abandonment and improve bot containment?

---

## 4. User Journey

### 4.1 Expected Journey

```text
1. User opens support chat
2. User describes issue: "My item arrived damaged"
3. Bot detects intent: damaged_item
4. Bot asks user to upload image proof
5. User uploads image
6. Bot acknowledges image upload
7. System analyzes image
8. Bot checks policy eligibility
9. Bot offers refund or replacement
10. User selects resolution
11. Case is closed
```

### 4.2 Failure Journey

```text
1. User opens support chat
2. User reports damaged item
3. Bot detects damaged_item intent
4. Bot asks user to upload image
5. User uploads image
6. Bot does not acknowledge the upload
7. Bot asks for image again
8. User gets frustrated
9. User abandons chat
```

---

## 5. Failure Point

The main failure point is:

```text
Image requested
↓
Image uploaded
↓
Bot repeats image request
↓
User abandons
```

This is not simply a user-side failure. The user may have completed the requested action, but the system failed to recognize, process, or respond to that action correctly.

---

## 6. Failure Hypotheses

| No. | Failure Hypothesis                                 | Failure Type              | Explanation                                                  |
| --: | -------------------------------------------------- | ------------------------- | ------------------------------------------------------------ |
|   1 | Bot does not explain why image is needed           | Communication failure     | User may not understand why proof is required                |
|   2 | User cannot upload image due to technical issue    | Technical failure         | Upload may fail due to network, size, or format              |
|   3 | User uploads image but bot does not acknowledge it | State/context failure     | Bot conversation state may not update after upload           |
|   4 | Image is uploaded but AI cannot analyze it         | GenAI vision failure      | Image may be blurry, unclear, or model may fail              |
|   5 | Bot repeatedly asks for image                      | Conversation loop failure | Bot repeats same prompt even after user action               |
|   6 | Bot does not offer fallback                        | Fallback design failure   | User has no clear path if upload/analysis fails              |
|   7 | Image proof required for all damaged item cases    | Policy friction           | Mandatory image proof may be too strict for low-value orders |

---

## 7. Product Analyst Framing

A weak interpretation would be:

```text
Users are not uploading images.
```

A stronger Product Analyst interpretation is:

```text
Some users may complete the upload step, but the chatbot fails to acknowledge or process the uploaded image. This creates a repeated prompt loop and causes frustration-driven abandonment.
```

This distinction matters because the product fix changes depending on the root cause.

If the issue is user reluctance, the fix is better explanation.

If the issue is upload failure, the fix is technical reliability.

If the issue is image analysis failure, the fix is GenAI vision improvement or fallback design.

If the issue is repeated prompt behavior, the fix is state handling and conversation logic.

---

## 8. Event Tracking Plan

To analyze this issue, the chatbot journey should be tracked using event data.

The main event table is:

```text
bot_events
```

Each row represents one action or system event inside a chatbot session.

### 8.1 Events Needed

| Event Name               | Meaning                           |
| ------------------------ | --------------------------------- |
| `chat_started`           | User started support chat         |
| `intent_detected`        | Bot detected the user intent      |
| `image_requested`        | Bot asked user to upload image    |
| `image_upload_attempted` | User attempted image upload       |
| `image_uploaded`         | Image upload was successful       |
| `image_upload_failed`    | Image upload failed               |
| `image_analysis_started` | System started analyzing image    |
| `image_analysis_success` | Image was analyzed successfully   |
| `image_analysis_failed`  | Image analysis failed             |
| `image_request_repeated` | Bot asked for image again         |
| `user_abandoned`         | User left the chat                |
| `agent_escalated`        | Case was escalated to human agent |
| `case_closed`            | Case was closed                   |

---

## 9. Data Model

For the first version of this case study, only two tables are needed.

---

### 9.1 Table 1: `support_sessions`

This table stores the final outcome of each support session.

One row = one chatbot session.

| Column         | Description                       |
| -------------- | --------------------------------- |
| `session_id`   | Unique ID for the chatbot session |
| `issue_type`   | Type of issue reported by user    |
| `final_status` | Final outcome of the session      |

Example:

| session_id | issue_type   | final_status       |
| ---------- | ------------ | ------------------ |
| S001       | damaged_item | resolved_by_bot    |
| S002       | damaged_item | abandoned          |
| S003       | damaged_item | abandoned          |
| S004       | damaged_item | escalated_to_agent |
| S005       | wrong_item   | resolved_by_bot    |

---

### 9.2 Table 2: `bot_events`

This table stores the step-by-step journey inside each chatbot session.

One row = one event inside a session.

| Column       | Description                        |
| ------------ | ---------------------------------- |
| `event_id`   | Unique event ID                    |
| `session_id` | Session to which the event belongs |
| `event_step` | Sequence number of the event       |
| `event_name` | Name of the event/action           |

Example:

| event_id | session_id | event_step | event_name      |
| -------- | ---------- | ---------: | --------------- |
| E001     | S001       |          1 | chat_started    |
| E002     | S001       |          2 | intent_detected |
| E003     | S001       |          3 | image_requested |
| E004     | S001       |          4 | image_uploaded  |
| E005     | S001       |          5 | case_closed     |

---

## 10. Why These Tables Are Needed

The `support_sessions` table answers:

```text
What was the final outcome?
```

The `bot_events` table answers:

```text
What happened step by step?
```

Together, they help answer:

```text
Did abandoned users reach the image request step?
Did users upload the image?
Did the bot ask again after upload?
Did repeated image request lead to abandonment?
```

---

## 11. Sample Journey Patterns

### 11.1 Successful Session

```text
chat_started
intent_detected
image_requested
image_uploaded
case_closed
```

Interpretation:

> User uploaded image and the case was resolved.

---

### 11.2 Abandonment Without Upload

```text
chat_started
intent_detected
image_requested
user_abandoned
```

Interpretation:

> User abandoned after the image request without uploading.

---

### 11.3 Upload Acknowledgement Failure

```text
chat_started
intent_detected
image_requested
image_uploaded
image_request_repeated
user_abandoned
```

Interpretation:

> User uploaded image, but the bot asked again. This suggests state handling, acknowledgement, or image processing failure.

---

### 11.4 Technical Upload Failure

```text
chat_started
intent_detected
image_requested
image_upload_failed
agent_escalated
```

Interpretation:

> User tried to upload, upload failed, and the session was escalated.

---

## 12. Metrics Framework

This case study uses three metric categories:

1. Product metrics
2. GenAI metrics
3. Business metrics

---

## 13. Product Metrics

| Metric                          | Definition                                                 | Why It Matters                           |
| ------------------------------- | ---------------------------------------------------------- | ---------------------------------------- |
| Image upload completion rate    | % of image-requested sessions where image was uploaded     | Measures completion of proof step        |
| Abandonment after image request | % of sessions abandoned after image request                | Measures journey friction                |
| Repeated image request rate     | % of sessions where bot asked for image again after upload | Measures conversation loop/state failure |
| Bot containment rate            | % of sessions resolved without human agent                 | Measures automation success              |
| Escalation rate                 | % of sessions escalated to human agent                     | Measures bot dependency on agents        |

---

## 14. GenAI Metrics

| Metric                                 | Definition                                                   | Why It Matters                                 |
| -------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------- |
| Correct intent but failed continuation | Bot detected the right issue but user failed next step       | Shows journey failure after AI understanding   |
| Image analysis failure rate            | % of uploaded images that could not be analyzed              | Measures AI vision reliability                 |
| Repeated prompt rate                   | Bot repeats same request after user action                   | Indicates weak memory/state handling           |
| Groundedness                           | Bot response matches actual system state                     | Prevents unsupported or incorrect bot behavior |
| Fallback success rate                  | % of failed image flows recovered through retry/agent review | Measures recovery design quality               |

---

## 15. Business Metrics

| Metric                      | Definition                                                                   | Why It Matters                     |
| --------------------------- | ---------------------------------------------------------------------------- | ---------------------------------- |
| Lost automation opportunity | Cases that could have been resolved by bot but failed due to upload friction | Measures missed automation benefit |
| Agent escalation cost       | Cost created by human escalation                                             | Measures operational cost          |
| Repeat contact risk         | Risk that abandoned users contact support again                              | Measures unresolved issue burden   |
| Customer experience risk    | Frustration created by repeated bot prompts                                  | Impacts trust and retention        |

---

## 16. SQL Analysis Questions

The SQL analysis should answer the following questions:

1. How many damaged item sessions occurred?
2. How many damaged item sessions were abandoned?
3. How many sessions reached the image request step?
4. How many sessions successfully uploaded the image?
5. Which sessions uploaded image but were asked again?
6. How many users abandoned after repeated image request?
7. What product issue does this indicate?

---

## 17. SQL Analysis Plan

### 17.1 Count Damaged Item Sessions

Purpose:

> Understand how many sessions are related to damaged item complaints.

```sql
SELECT 
    COUNT(*) AS damaged_item_sessions
FROM support_sessions
WHERE issue_type = 'damaged_item';
```

---

### 17.2 Count Abandoned Damaged Item Sessions

Purpose:

> Understand how many damaged item users failed to complete the support journey.

```sql
SELECT 
    COUNT(*) AS abandoned_damaged_item_sessions
FROM support_sessions
WHERE issue_type = 'damaged_item'
  AND final_status = 'abandoned';
```

---

### 17.3 Count Sessions Where Image Was Requested

Purpose:

> Identify how many users reached the image proof step.

```sql
SELECT 
    COUNT(DISTINCT session_id) AS image_requested_sessions
FROM bot_events
WHERE event_name = 'image_requested';
```

---

### 17.4 Count Sessions Where Image Was Uploaded

Purpose:

> Identify how many users completed the upload step.

```sql
SELECT 
    COUNT(DISTINCT session_id) AS image_uploaded_sessions
FROM bot_events
WHERE event_name = 'image_uploaded';
```

---

### 17.5 Find Sessions Where Image Was Uploaded but Bot Asked Again

Purpose:

> Detect sessions where the user completed the upload step but the bot still repeated the request.

```sql
SELECT 
    DISTINCT uploaded.session_id
FROM bot_events uploaded
JOIN bot_events repeated
    ON uploaded.session_id = repeated.session_id
WHERE uploaded.event_name = 'image_uploaded'
  AND repeated.event_name = 'image_request_repeated'
  AND repeated.event_step > uploaded.event_step;
```

---

### 17.6 Count Users Who Abandoned After Repeated Image Request

Purpose:

> Measure how often repeated image requests are associated with abandonment.

```sql
SELECT 
    COUNT(DISTINCT s.session_id) AS abandoned_after_repeated_image_request
FROM support_sessions s
JOIN bot_events uploaded
    ON s.session_id = uploaded.session_id
JOIN bot_events repeated
    ON s.session_id = repeated.session_id
WHERE s.final_status = 'abandoned'
  AND uploaded.event_name = 'image_uploaded'
  AND repeated.event_name = 'image_request_repeated'
  AND repeated.event_step > uploaded.event_step;
```

---

## 18. Expected Insights

Possible insights from the analysis:

1. Users may not be abandoning only because they do not want to upload images.
2. Some users may upload images, but the bot still asks again.
3. Repeated image requests may indicate state handling failure or image analysis failure.
4. The bot may correctly detect damaged item intent but still fail at task completion.
5. The failure may be caused by weak product flow, not only weak AI understanding.
6. A better fallback flow could reduce abandonment and agent escalation.

---

## 19. Product Recommendations

### 19.1 Acknowledge Upload Clearly

Current weak behavior:

```text
Please upload image.
```

Improved behavior:

```text
Image received. I’m checking it now.
```

Why:

> The user needs immediate confirmation that their action was successful.

---

### 19.2 Avoid Repeated Image Request After Successful Upload

The bot should not ask for another image if `image_uploaded` has already happened.

Recommended rule:

```text
If image_uploaded = true,
do not trigger image_requested again unless image_analysis_failed explains why.
```

---

### 19.3 Explain Image Analysis Failure

Bad behavior:

```text
Please upload image again.
```

Better behavior:

```text
The image was uploaded, but the damage is not clearly visible. Please upload a clearer image or continue with agent review.
```

Why:

> The user should know what went wrong and what to do next.

---

### 19.4 Add Retry and Agent Review Options

If the image analysis fails, the bot should offer:

```text
Retry upload
Continue with agent review
```

This prevents dead-end loops.

---

### 19.5 Escalate After Repeated Failure

Recommended logic:

```text
If image_upload_failed twice
OR image_analysis_failed twice
OR image_request_repeated occurs after upload,
offer agent escalation.
```

Why:

> Repeated failure should trigger recovery, not repetition.

---

### 19.6 Improve Image Upload Guidance

Before asking for image, the bot should explain:

```text
Please upload a clear photo of the damaged item. Make sure the damaged area is visible. This helps us verify your issue faster and process refund or replacement.
```

Optional additions:

* Show sample image
* Mention accepted file formats
* Mention maximum file size
* Offer camera/gallery upload
* Offer skip option for agent review

---

## 20. Improved Chatbot Flow

```text
User: My item arrived damaged.

Bot: I can help with that. Please upload a clear photo of the damaged item. Make sure the damaged area is visible. This helps us verify your issue faster.

User uploads image.

Bot: Image received. I’m checking it now.

If image analysis succeeds:
Bot: Damage detected. You are eligible for refund or replacement.

If image analysis fails:
Bot: The image was uploaded, but the damage is not clearly visible. You can upload a clearer photo or continue with agent review.

If user retries and fails again:
Bot: This step is not working smoothly. I’ll connect you to a support agent with your uploaded image attached.
```

---

## 21. Business Impact

If the image upload journey fails, the business may face:

| Failure                           | Business Impact            |
| --------------------------------- | -------------------------- |
| User abandons chat                | Poor customer experience   |
| User contacts again               | Higher repeat contact load |
| User escalates to agent           | Higher support cost        |
| Bot fails to resolve simple cases | Lower automation ROI       |
| Premium user experiences friction | Revenue and trust risk     |
| Refund/replacement delayed        | Lower satisfaction         |

---

## 22. Example Business Impact Estimate

Assumption:

```text
30 users abandon after repeated image request
50% later contact human support
Each human support session costs ₹80
```

Estimated extra support cost:

```text
30 × 50% × ₹80 = ₹1,200
```

At small scale this looks low, but across thousands of sessions per month, this becomes a meaningful operational cost.

---

## 23. AI Prototype Scope

The prototype should show two flows:

### 23.1 Bad Flow

```text
User reports damaged item
↓
Bot asks for image
↓
User uploads image
↓
Bot fails to acknowledge upload
↓
Bot asks for image again
↓
User abandons
```

### 23.2 Improved Flow

```text
User reports damaged item
↓
Bot asks for image with explanation
↓
User uploads image
↓
Bot confirms upload
↓
Bot analyzes image
↓
If success: refund/replacement offered
↓
If failure: retry or agent review offered
```

---

## 24. Prototype Requirements

The AI prototype should include:

1. Bad flow simulation
2. Improved flow simulation
3. Event log panel
4. Metrics panel
5. Failure labels
6. Product insight summary
7. Clear fallback behavior

---

## 25. Key Learning

This case study shows that:

> AI product failure is not always a model failure.

The bot may correctly understand the user's damaged item intent, but the product can still fail because of:

* poor upload acknowledgement
* weak state handling
* repeated prompts
* unclear guidance
* failed image analysis
* missing fallback options
* poor connection between system events and chatbot responses

A strong GenAI Product Analyst should not only ask:

```text
Did the model predict the right intent?
```

They should also ask:

```text
Did the user complete the task?
Did the bot respond based on actual system state?
Did the product recover when the AI/system failed?
Did the journey lead to resolution?
What was the business impact?
```

---

## 26. Final Summary

The image upload step is a critical point in the damaged item support journey.

If the bot asks for proof but does not acknowledge upload, repeats the request, or fails to offer fallback options, users may abandon the chat even though the AI understood their original issue.

The recommended product direction is to improve upload acknowledgement, image analysis messaging, retry logic, and agent fallback. These changes can reduce abandonment, improve bot containment, reduce agent cost, and create a better customer experience.

This micro case study demonstrates the core GenAI Product Analyst loop:

```text
User journey
↓
Failure hypothesis
↓
Event tracking
↓
Metrics
↓
SQL analysis
↓
Insight
↓
Product recommendation
↓
Business impact
```
