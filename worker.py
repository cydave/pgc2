import os
import uuid
import subprocess
import contextlib

import sqlalchemy
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from pgc2.models import Job, JobResult

from pgc2 import db
from pgc2.db_session import SessionLocal


class JobServer:

    def __init__(self, session: Session, channel: str = "job_channel"):
        self.id = str(uuid.uuid4())
        self.channel = channel
        self._session = session
        self._bg_jobs = []

    def _handle_job(self, job_id, session):
        job = session.get(Job, job_id)
        if job is None:
            return
        print(f"Handling job: {job_id}")
        cmd = job.payload["command"]
        proc = subprocess.run(cmd, shell=True, capture_output=True)
        stdout = proc.stdout.decode("utf8", errors="replace")
        session.add(JobResult(job_id=job.id, result={"output": stdout}))
        session.commit()

    def serve(self):
        print(f"Subscribing to {self.channel!r}")
        db.listen(self._session, self.channel)
        with contextlib.closing(self._session.get_bind().raw_connection()) as con:
            gen = con.driver_connection.notifies()
            for notify in gen:
                self._handle_job(job_id=notify.payload, session=self._session)


def main():
    with SessionLocal() as session:
        JobServer(session).serve()


if __name__ == "__main__":
    main()
