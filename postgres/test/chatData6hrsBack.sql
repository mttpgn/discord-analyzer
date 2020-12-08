BEGIN;
SELECT
text
FROM messages
WHERE timestamp >= NOW() - INTERVAL '6 hours'
END;
