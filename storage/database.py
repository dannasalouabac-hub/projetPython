import os

import psycopg2


def save_events(events):
    connection = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS auth_events (
                        id SERIAL PRIMARY KEY,
                        event_time TEXT,
                        event_type TEXT NOT NULL,
                        ip TEXT NOT NULL,
                        actor TEXT NOT NULL,
                        city TEXT,
                        country TEXT,
                        username TEXT,
                        message TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    "ALTER TABLE auth_events ADD COLUMN IF NOT EXISTS username TEXT"
                )
                cursor.executemany(
                    """
                    INSERT INTO auth_events
                        (event_time, event_type, ip, actor, city, country, username, message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    events,
                )
    finally:
        connection.close()
