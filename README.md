# JustChattti Backend

Self-hosted мессенджер с REST API и WebSocket. Бэкенд готов к использованию, мобильный клиент находится в разработке (готов на 60%).

## Основные возможности

**Пользователи и авторизация**
- Регистрация и вход по JWT (access + refresh токены).
- Профиль пользователя: username, bio, аватар, дата рождения, онлайн-статус.
- Роли: `user` и `admin`. Администратор может менять роль и лимиты хранилища других пользователей.

**Чаты и сообщения**
- Приватные чаты (1 на 1).
- Текстовые сообщения и вложения (изображения, видео, аудио, файлы).
- История сообщений с keyset-пагинацией (курсоры).
- Редактирование и удаление сообщений в течение 24 часов.
- Отметка о прочтении.
- Поиск по пользователям, сообщениям (полнотекстовый по содержимому, по отправителю).

**WebSocket**
- Real-time доставка сообщений, событий редактирования/удаления.
- WebRTC-звонки (аудио/видео) с сигнализацией через WebSocket.

**Push-уведомления**
- Firebase Cloud Messaging (FCM) для офлайн-пользователей.
- Возможность замутить отдельного пользователя, чтобы не получать от него уведомления.

**Хранилище файлов**
- Загрузка файлов в MinIO (S3-совместимое хранилище).
- Лимит хранилища на пользователя (по умолчанию 1 ГБ, можно изменить через админку).
- Удаление файлов с каскадным освобождением места.

**OpenAPI-документация**
- Полное описание всех эндпоинтов доступно после запуска по адресу `/docs`.

## Схема базы данных

### users
| Поле              | Тип          | Описание                              |
|-------------------|--------------|---------------------------------------|
| id                | int (PK)     | Уникальный идентификатор              |
| username          | varchar      | Уникальное имя пользователя           |
| hashed_password   | varchar      | Хэш пароля                            |
| avatar_id         | int (FK)     | Внешний ключ к files.id (аватар)      |
| bio               | varchar(250) | Краткая информация о пользователе     |
| gender            | varchar(20)  | Пол                                   |
| role              | enum         | Роль: user или admin                  |
| storage_used_bytes| bigint       | Занято места в хранилище              |
| storage_limit_bytes| bigint      | Лимит хранилища (по умолчанию 1 ГБ)   |
| birth_date        | date         | Дата рождения                         |
| is_online         | boolean      | Флаг онлайна                          |
| last_seen         | timestamptz  | Время последней активности            |
| created_at        | timestamptz  | Дата регистрации                      |
| user_metadata     | json         | Дополнительные данные                 |

### refresh_tokens
| Поле       | Тип         | Описание                         |
|------------|-------------|----------------------------------|
| id         | int (PK)    | Идентификатор токена             |
| user_id    | int (FK)    | Внешний ключ к users.id         |
| token      | varchar     | Уникальный refresh-токен        |
| expires_at | timestamptz | Срок действия токена            |
| created_at | timestamptz | Дата создания                    |

### blacklisted_tokens
| Поле       | Тип         | Описание                         |
|------------|-------------|----------------------------------|
| id         | int (PK)    | Идентификатор записи             |
| token      | varchar     | Заблокированный токен           |
| expires_at | timestamptz | Срок истечения токена           |
| created_at | timestamptz | Дата добавления в чёрный список |

### files
| Поле           | Тип        | Описание                          |
|----------------|------------|-----------------------------------|
| id             | int (PK)   | Идентификатор файла               |
| filename       | varchar    | UUID-имя файла в MinIO            |
| original_name  | varchar    | Оригинальное имя файла            |
| filetype       | varchar    | Тип: image, video, audio, file    |
| filesubtype    | varchar    | Подтип: avatar, voice_message, other|
| size           | int        | Размер в байтах                   |
| uploaded_by_id | int (FK)   | Внешний ключ к users.id          |
| created_at     | timestamptz| Дата загрузки                     |

### chats
| Поле          | Тип        | Описание                          |
|---------------|------------|-----------------------------------|
| id            | int (PK)   | Идентификатор чата                |
| name          | varchar(100)| Название чата                     |
| chat_type     | enum       | Тип чата (пока только private)    |
| avatar_id     | int (FK)   | Внешний ключ к files.id (аватар чата) |
| created_by_id | int (FK)   | Внешний ключ к users.id (создатель) |
| created_at    | timestamptz| Дата создания                     |
| updated_at    | timestamptz| Дата последнего обновления        |

### chat_participants
| Поле         | Тип        | Описание                          |
|--------------|------------|-----------------------------------|
| id           | int (PK)   | Идентификатор записи              |
| chat_id      | int (FK)   | Внешний ключ к chats.id          |
| user_id      | int (FK)   | Внешний ключ к users.id          |
| joined_at    | timestamptz| Дата вступления                   |
| last_read_at | timestamptz| Время последнего прочтения        |

### messages
| Поле            | Тип        | Описание                                 |
|-----------------|------------|------------------------------------------|
| id              | int (PK)   | Идентификатор сообщения                  |
| chat_id         | int (FK)   | Внешний ключ к chats.id                 |
| sender_id       | int (FK)   | Внешний ключ к users.id (отправитель)   |
| message_type    | enum       | Тип: text, image, video, audio, voice, file |
| content         | text       | Текст сообщения                          |
| file_id         | int (FK)   | Внешний ключ к files.id (вложение)      |
| reply_to_id     | int (FK)   | Внешний ключ к messages.id (ответ на)    |
| status          | enum       | Статус: sent, delivered, read            |
| edited          | boolean    | Флаг редактирования                      |
| message_metadata| json       | Дополнительные данные                    |
| created_at      | timestamptz| Время отправки                           |
| updated_at      | timestamptz| Время последнего изменения               |

### calls
| Поле         | Тип        | Описание                          |
|--------------|------------|-----------------------------------|
| id           | int (PK)   | Идентификатор звонка              |
| chat_id      | int (FK)   | Внешний ключ к chats.id          |
| initiator_id | int (FK)   | Внешний ключ к users.id          |
| call_type    | varchar(20)| Тип звонка: audio или video       |
| status       | varchar(20)| Статус: ringing, active, ended    |
| started_at   | timestamptz| Время начала                      |
| ended_at     | timestamptz| Время окончания                   |

### call_participants
| Поле      | Тип        | Описание                          |
|-----------|------------|-----------------------------------|
| id        | int (PK)   | Идентификатор записи              |
| call_id   | int (FK)   | Внешний ключ к calls.id          |
| user_id   | int (FK)   | Внешний ключ к users.id          |
| joined_at | timestamptz| Время подключения                 |
| left_at   | timestamptz| Время отключения                  |

### user_fcm_tokens
| Поле       | Тип         | Описание                          |
|------------|-------------|-----------------------------------|
| id         | int (PK)    | Идентификатор записи              |
| user_id    | int (FK)    | Внешний ключ к users.id          |
| fcm_token  | varchar(512)| Токен устройства для FCM         |
| device_id  | varchar(256)| Идентификатор устройства          |
| created_at | timestamptz | Дата добавления                   |
| updated_at | timestamptz | Дата обновления                   |

### user_mutes
| Поле             | Тип        | Описание                                 |
|------------------|------------|------------------------------------------|
| id               | int (PK)   | Идентификатор записи                     |
| muted_by_user_id | int (FK)   | Внешний ключ к users.id (кто замутил)    |
| muted_user_id    | int (FK)   | Внешний ключ к users.id (кого замутили)  |
| created_at       | timestamptz| Дата мута                                |

Связи между таблицами реализованы через внешние ключи с каскадным удалением или установкой NULL, где это необходимо.

## Быстрый запуск (Docker Compose)

1. Убедитесь, что установлены Docker и Docker Compose.
2. Склонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd JustChattti
   ```
3. Создайте файл `.env` из примера и при необходимости измените секретные ключи и пароли:
   ```bash
   cp .env.example .env
   ```
4. Для работы push-уведомлений через Firebase поместите ваш `firebase-credentials.json` в папку `backend/`. Если файл отсутствует, FCM не будет работать, но остальной функционал останется доступным.
5. Запустите проект:
   ```bash
   docker compose up -d --build
   ```
6. После запуска:
   - Backend API доступен на `http://localhost:1000`
   - Swagger UI: `http://localhost:1000/docs`
   - MinIO (S3-хранилище): `http://localhost:9000` (консоль на порту `9001`)

При первом запуске автоматически создаётся тестовый администратор с учётными данными из переменных окружения (по умолчанию admin/admin).

## Стек технологий (backend)

- FastAPI (Python 3.13+)
- SQLAlchemy (asyncpg) + PostgreSQL 17
- MinIO (S3-совместимое файловое хранилище)
- WebSocket (встроенный в FastAPI)
- Firebase Admin SDK (FCM)
- Docker Compose для развёртывания
