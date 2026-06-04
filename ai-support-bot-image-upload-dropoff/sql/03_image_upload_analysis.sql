-- 1. Count damaged item sessions

SELECT 
    COUNT(*) AS damaged_item_sessions
FROM support_sessions
WHERE issue_type = 'damaged_item';


-- 2. Count abandoned damaged item sessions

SELECT 
    COUNT(*) AS abandoned_damaged_item_sessions
FROM support_sessions
WHERE issue_type = 'damaged_item'
  AND final_status = 'abandoned';


-- 3. Count sessions where image was requested

SELECT 
    COUNT(DISTINCT session_id) AS image_requested_sessions
FROM bot_events
WHERE event_name = 'image_requested';


-- 4. Count sessions where image was uploaded

SELECT 
    COUNT(DISTINCT session_id) AS image_uploaded_sessions
FROM bot_events
WHERE event_name = 'image_uploaded';


-- 5. Find sessions where image was uploaded but bot asked again

SELECT 
    DISTINCT uploaded.session_id
FROM bot_events uploaded
JOIN bot_events repeated
    ON uploaded.session_id = repeated.session_id
WHERE uploaded.event_name = 'image_uploaded'
  AND repeated.event_name = 'image_request_repeated'
  AND repeated.event_step > uploaded.event_step;


-- 6. Count users who abandoned after repeated image request

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
