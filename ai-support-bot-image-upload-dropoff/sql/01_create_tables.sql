CREATE TABLE support_sessions (
    session_id VARCHAR(10) PRIMARY KEY,
    issue_type VARCHAR(50),
    final_status VARCHAR(50)
);

CREATE TABLE bot_events (
    event_id VARCHAR(10) PRIMARY KEY,
    session_id VARCHAR(10),
    event_step INT,
    event_name VARCHAR(100)
);
