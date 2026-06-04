INSERT INTO support_sessions 
(session_id, issue_type, final_status)
VALUES
('S001', 'damaged_item', 'resolved_by_bot'),
('S002', 'damaged_item', 'abandoned'),
('S003', 'damaged_item', 'abandoned'),
('S004', 'damaged_item', 'escalated_to_agent'),
('S005', 'wrong_item', 'resolved_by_bot');

INSERT INTO bot_events
(event_id, session_id, event_step, event_name)
VALUES
('E001', 'S001', 1, 'chat_started'),
('E002', 'S001', 2, 'intent_detected'),
('E003', 'S001', 3, 'image_requested'),
('E004', 'S001', 4, 'image_uploaded'),
('E005', 'S001', 5, 'case_closed'),

('E006', 'S002', 1, 'chat_started'),
('E007', 'S002', 2, 'intent_detected'),
('E008', 'S002', 3, 'image_requested'),
('E009', 'S002', 4, 'user_abandoned'),

('E010', 'S003', 1, 'chat_started'),
('E011', 'S003', 2, 'intent_detected'),
('E012', 'S003', 3, 'image_requested'),
('E013', 'S003', 4, 'image_uploaded'),
('E014', 'S003', 5, 'image_request_repeated'),
('E015', 'S003', 6, 'user_abandoned'),

('E016', 'S004', 1, 'chat_started'),
('E017', 'S004', 2, 'intent_detected'),
('E018', 'S004', 3, 'image_requested'),
('E019', 'S004', 4, 'image_upload_failed'),
('E020', 'S004', 5, 'agent_escalated'),

('E021', 'S005', 1, 'chat_started'),
('E022', 'S005', 2, 'intent_detected'),
('E023', 'S005', 3, 'case_closed');
