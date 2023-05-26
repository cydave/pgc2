import re
import contextlib

import sqlalchemy
from sqlalchemy.orm import Session
import psycopg
import psycopg.sql

from pgc2.models import Base, Job, JobResult


def init(session: Session):
    Base.metadata.create_all(bind=session.bind.engine)
    session.execute(
        sqlalchemy.text(
            """
    -- Revoke access to job_* tables
    REVOKE ALL PRIVILEGES ON job FROM PUBLIC;
    REVOKE ALL PRIVILEGES ON job_result FROM PUBLIC;

    -- Enable row level security
    ALTER TABLE job ENABLE ROW LEVEL SECURITY;

    -- Restrict workers from accessing other worker's jobs
    DROP POLICY IF EXISTS restrict_job_access_to_worker ON job;
    CREATE POLICY restrict_job_access_to_worker ON job FOR SELECT USING (current_user = worker_id);


    -- Create a function that notifies about new job_result inserts.
    CREATE OR REPLACE FUNCTION notify_job_result()
    RETURNS trigger AS $$
    DECLARE
    BEGIN
        PERFORM pg_notify('job_result_channel', NEW.id::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Register a trigger which uses the notify_job_result() proceedure to invoke pg_notify about new jobs.
    CREATE OR REPLACE TRIGGER notify_job_result_inserted AFTER INSERT ON job_result FOR EACH ROW EXECUTE PROCEDURE notify_job_result();
"""
        )
    )
    session.commit()


def register_user(session: Session, username: str, password: str):
    with contextlib.closing(session.get_bind().raw_connection()) as con:
        stmt = psycopg.sql.SQL(
            """
        CREATE USER {username} WITH PASSWORD {password} NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION CONNECTION LIMIT 4;

        -- Allow the user to fetch jobs.
        GRANT SELECT ON job TO {username};

        -- Allow the user to insert job results.
        GRANT INSERT ON job_result TO {username};
        """)
        con.execute(stmt.format(username=psycopg.sql.Identifier(username), password=psycopg.sql.Literal(password)))
        con.commit()
    return username, password


def listen(session: Session, channel: str):
    channel = re.sub(r"[^\w ]+", "", channel)
    session.execute(sqlalchemy.text(f"LISTEN {channel}"))
    session.commit()


def unlisten(session: Session, channel: str):
    channel = re.sub(r"[^\w ]+", "", channel)
    session.execute(sqlalchemy.text(f"UNLISTEN {channel}"))
    session.commit()


def notify(session: Session, channel: str, payload: str):
    session.execute(
        sqlalchemy.text("SELECT pg_notify(:channel, :payload)"),
        dict(channel=channel, payload=payload),
    )
    session.commit()


def user_exists(session: Session, username: str) -> bool:
    cursor = session.execute(sqlalchemy.text("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname=:username"), dict(username=username))
    return bool(cursor.scalar_one_or_none())

def add_job(session: Session, job: Job) -> str:
    session.add(job)
    session.commit()
    return str(job.id)


def ping(session: Session):
    session.execute(sqlalchemy.select(1))
    return True
