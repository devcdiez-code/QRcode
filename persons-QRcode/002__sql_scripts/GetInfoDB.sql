
--drop table persons;
--DELETE FROM persons;
-- Путь к файлу базы данных
PRAGMA database_list;

-- Версия SQLite
SELECT sqlite_version();

-- Список таблиц
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

SELECT * FROM persons ;


SELECT *
FROM persons
WHERE photo_path IS NULL OR photo_path = '';