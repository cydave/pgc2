import os
import json

from pgc2 import db
from pgc2.db_session import SessionLocal

with SessionLocal() as session:
    db.init(session)
    if os.getenv("INITIAL_USERS", []):
        for user in json.loads(os.environ["INITIAL_USERS"]):
            if not db.user_exists(session, user["username"]):
                print(f"Creating user: {user['username']}")
                db.register_user(session=session, username=user["username"], password=user["password"])
