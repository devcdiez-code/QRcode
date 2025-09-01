
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    last_name2 TEXT,              -- вторая фамилия

    birth_date TEXT,                 -- дата рождения (в формате 'YYYY-MM-DD')

    status TEXT,                     -- гость / сопровождающий
    organization TEXT,               -- название организации
    position TEXT,                   -- должность

    phone1 TEXT,
    phone2 TEXT,
    phone3 TEXT,
    phone4 TEXT,

    email TEXT,
    photo_path TEXT,                 -- путь к файлу фотографии (в папке)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    is_active INTEGER DEFAULT 1,             -- активно/неактивно (1/0)
    is_allowed INTEGER DEFAULT 1,            -- разрешено/не разрешено
    is_email_confirmed INTEGER DEFAULT 0,    -- e-mail подтверждён

    notified_email INTEGER DEFAULT 0,        -- приглашение на e-mail
    notified_whatsapp INTEGER DEFAULT 0,     -- приглашение на WhatsApp
    notified_telegram INTEGER DEFAULT 0      -- приглашение на Telegram
);

-- Поиск по фамилии
CREATE INDEX IF NOT EXISTS idx_persons_last_name ON persons(last_name);

-- Поиск по email
CREATE INDEX IF NOT EXISTS idx_persons_email ON persons(email);

-- Поиск по основному телефону
CREATE INDEX IF NOT EXISTS idx_persons_phone1 ON persons(phone1);

-- Поиск по дате рождения
CREATE INDEX IF NOT EXISTS idx_persons_birth_date ON persons(birth_date);

-- Фильтрация по статусу (гость/сопровождающий)
CREATE INDEX IF NOT EXISTS idx_persons_status ON persons(status);

-- Быстрая фильтрация по активности
CREATE INDEX IF NOT EXISTS idx_persons_is_active ON persons(is_active);

-- Фильтрация по уведомлениям
CREATE INDEX IF NOT EXISTS idx_persons_notified_email ON persons(notified_email);

