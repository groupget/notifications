from datetime import datetime
from flask import Response
import json


def json_datetime(val):
    if isinstance(val, datetime):
        return str(val)


def json_patch(obj, json):
    for c in obj.__table__.columns:
        if c.name in json:
            setattr(obj, c.name, json[c.name])


def db_add(db, obj):
    try:
        db.session.add(obj)
        db.session.commit()
        return json.dumps(obj.serialize(), default=json_datetime)
    except Exception as e:
        return Response("Error commiting to the database. Bad request! \n {}".format(str(e)), status=400)
