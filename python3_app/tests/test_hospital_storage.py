import fakeredis


def test_hospital_creation():
    r = fakeredis.FakeRedis(decode_responses=True)

    r.set("hospital:autoID", 1)

    ID = r.get("hospital:autoID")

    r.hset(f"hospital:{ID}", mapping={
        "name": "City Hospital",
        "address": "Main street",
        "phone": "123",
        "beds_number": "100"
    })

    r.incr("hospital:autoID")

    hospital = r.hgetall("hospital:1")

    assert hospital["name"] == "City Hospital"
    assert hospital["address"] == "Main street"
    assert hospital["beds_number"] == "100"
    assert r.get("hospital:autoID") == "2"
