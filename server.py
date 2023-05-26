import os
import contextlib
import multiprocessing

import sqlalchemy

from pgc2 import db
from pgc2.db_session import SessionLocal
from pgc2.models import Job, JobResult


def job_result_handler(print_queue):
    with SessionLocal() as session:
        db.listen(session, channel="job_result_channel")
        with contextlib.closing(session.get_bind().raw_connection()) as con:
            for notification in con.notifies():
                job_result = session.get(JobResult, notification.payload)
                output = job_result.result["output"]
                print_queue.put(f"Result from job: {job_result.job_id}\n{output}")

def main():
    print_queue = multiprocessing.Queue()
    watcher_proc = multiprocessing.Process(
        target=job_result_handler,
        args=(print_queue, ),
        daemon=True,
    )
    watcher_proc.start()

    with SessionLocal() as session:
        while True:
            cmd = input("cmd> ")
            if not cmd.strip():
                continue
            job = Job(payload={"command": cmd.strip()}, worker_id="worker")
            job_id = db.add_job(session, job)
            print(f"Sending job: {job_id}")
            db.notify(session, channel="job_channel", payload=job_id)
            output = print_queue.get(timeout=10)
            if output:
                print(output)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        pass
