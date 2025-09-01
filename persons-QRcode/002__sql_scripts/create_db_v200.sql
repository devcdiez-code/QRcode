

-- drop table persons ;

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS persons (
    -- Основная информация о персоне
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,                  -- имя
    middle_name TEXT,                          -- отчество
    last_name TEXT NOT NULL,                   -- фамилия
    last_name2 TEXT,                           -- фамилия 2
    gender TEXT CHECK(gender IN ('мужской','женский')) NOT NULL,
    salutation TEXT,                           -- обращение
    language TEXT,                             -- язык
    status TEXT CHECK(status IN ('гость','сопровождающий')),

    organization TEXT,
    position TEXT,

    mobile1 TEXT,
    mobile2 TEXT,
    mobile3 TEXT,
    mobile4 TEXT,
    email TEXT,
    email_confirmed BOOLEAN DEFAULT 0,

    -- Контактное лицо
    contact_first_name TEXT,
    contact_middle_name TEXT,
    contact_last_name TEXT,
    contact_last_name2 TEXT,
    contact_gender TEXT CHECK(contact_gender IN ('мужской','женский')),
    contact_language TEXT,
    contact_position TEXT,
    contact_mobile1 TEXT,
    contact_mobile2 TEXT,
    contact_mobile3 TEXT,
    contact_mobile4 TEXT,
    contact_email TEXT,
    contact_email_confirmed BOOLEAN DEFAULT 0,

    -- QR и бейдж
    qr_code TEXT UNIQUE,                       -- строка QR-кода
    badge_created_at DATETIME,                 -- дата/время создания бейджа

    -- Системные поля
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- время создания записи
    modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- время изменения записи
    is_active BOOLEAN DEFAULT 1,                     -- активно/неактивно
    is_allowed BOOLEAN DEFAULT 1,                    -- разрешено/не разрешено

    -- Уведомления
    notified_email BOOLEAN DEFAULT 0,
    notified_email_time DATETIME,
    notified_whatsapp BOOLEAN DEFAULT 0,
    notified_whatsapp_time DATETIME,
    notified_telegram BOOLEAN DEFAULT 0,
    notified_telegram_time DATETIME,
    notified_max BOOLEAN DEFAULT 0,
    notified_max_time DATETIME,

    -- Проход
    passed BOOLEAN DEFAULT 0,
    passed_time DATETIME,
    gate_number TEXT,

    -- Прочее
    note TEXT,
    photo_path TEXT                              -- путь к фото (D:\persons-QRcode\_photos\xxx.jpg)
);

-- Триггер для автоматического обновления modified_at
CREATE TRIGGER IF NOT EXISTS trg_persons_modified
AFTER UPDATE ON persons
FOR EACH ROW
BEGIN
    UPDATE persons SET modified_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
INSERT INTO persons (
    first_name, middle_name, last_name, gender, salutation, language, status,
    organization, position, mobile1, email, email_confirmed,
    contact_first_name, contact_last_name, contact_gender, contact_language, contact_email,
    contact_email_confirmed, qr_code, badge_created_at, note, photo_path
) VALUES (
    'Иван', 'Петрович', 'Сидоров', 'мужской', 'господин', 'русский', 'гость',
    'ООО "Альфа"', 'директор', '+7-900-111-22-33', 'ivan.sidorov@example.com', 1,
    'Алексей', 'Иванов', 'мужской', 'русский', 'alexey.ivanov@example.com', 1,
    'QR1234567890', CURRENT_TIMESTAMP, 'VIP гость',
    'D:\\persons-QRcode\\_photos\\ivan_sidorov.jpg'
);

INSERT INTO persons (
    first_name, middle_name, last_name, gender, salutation, language, status,
    organization, position, mobile1, email,
    contact_first_name, contact_last_name, contact_gender, contact_language, contact_email,
    qr_code, badge_created_at, note, photo_path
) VALUES (
    'Мария', 'Игоревна', 'Кузнецова', 'женский', 'уважаемая', 'русский', 'сопровождающий',
    'ЗАО "Бета"', 'менеджер', '+7-901-222-33-44', 'maria.kuz@example.com',
    'Ольга', 'Смирнова', 'женский', 'русский', 'olga.smirnova@example.com',
    'QR9876543210', CURRENT_TIMESTAMP, 'Сопровождает VIP-гостя',
    'D:\\persons-QRcode\\_photos\\maria_kuznetsova.jpg'
);

