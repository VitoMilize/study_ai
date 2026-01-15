import fakeredis
from python3_app.main import init_db


def test_init_db_creates_keys():
    redis_client = fakeredis.FakeRedis(decode_responses=True)

    init_db(redis_client)

    assert redis_client.get("db_initiated") == "1"
    assert redis_client.get("hospital:autoID") == "1"
    assert redis_client.get("doctor:autoID") == "1"
    assert redis_client.get("patient:autoID") == "1"
    assert redis_client.get("diagnosis:autoID") == "1"
