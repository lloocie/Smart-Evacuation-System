SELECT
    t.name      AS [Table],
    i.name      AS [Index]
FROM sys.indexes i
JOIN sys.tables t ON i.object_id = t.object_id
WHERE i.name LIKE 'idx%'
ORDER BY t.name;