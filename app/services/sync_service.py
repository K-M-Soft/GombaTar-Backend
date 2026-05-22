from app.repositories.sync_repository import get_mushrooms_delta
from app.helpers.datetime import serialize_value

def get_mushrooms_delta_service(since):
    rows = get_mushrooms_delta(since)
    mushrooms = [{k: serialize_value(v) for k, v in row.items()} for row in rows]
    return mushrooms
