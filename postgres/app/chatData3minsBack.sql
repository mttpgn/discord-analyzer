BEGIN;
SELECT
text
FROM {}
WHERE timestamp >= NOW() - INTERVAL '3 minutes'
AND text='{}';
END;
