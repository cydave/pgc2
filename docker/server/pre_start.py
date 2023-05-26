import os
import logging

from tenacity import retry, stop_after_attempt, wait_fixed

from pgc2 import db
from pgc2 import db_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
)
def init() -> None:
    try:
        with db_session.SessionLocal() as session:
            db.ping(session)
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    init()


if __name__ == "__main__":
    main()
