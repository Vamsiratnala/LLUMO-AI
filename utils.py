from bson import ObjectId
from datetime import datetime


def serialize_doc(doc: dict) -> dict:
    if not doc:
        return None
    out = doc.copy()
    # convert ObjectId
    if "_id" in out:
        out["_id"] = str(out["_id"])
    # convert joining_date if datetime
    jd = out.get("joining_date")
    if isinstance(jd, datetime):
        out["joining_date"] = jd.date().isoformat()
    return out
