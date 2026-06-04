# AI Support Bot Prototype Flow

## Bad Flow

1. User says: "My item arrived damaged."
2. Bot asks: "Please upload an image."
3. User uploads image.
4. Bot does not acknowledge upload.
5. Bot asks again: "Please upload an image."
6. User abandons chat.

## Improved Flow

1. User says: "My item arrived damaged."
2. Bot says: "Please upload a clear photo of the damaged item. This helps us verify the issue faster."
3. User uploads image.
4. Bot says: "Image received. I’m checking it now."
5. If image analysis succeeds:
   - Bot offers refund or replacement.
6. If image analysis fails:
   - Bot explains the issue.
   - Bot offers retry or agent review.

## Events Tracked

- chat_started
- intent_detected
- image_requested
- image_upload_attempted
- image_uploaded
- image_upload_failed
- image_analysis_started
- image_analysis_success
- image_analysis_failed
- image_request_repeated
- user_abandoned
- agent_escalated
- case_closed

## Metrics Supported

- Image upload completion rate
- Repeated image request rate
- Abandonment after image request
- Bot containment rate
- Escalation rate
