import fakeredis


def test_doctor_patient_relation():
    r = fakeredis.FakeRedis(decode_responses=True)

    r.hset("doctor:1", mapping={"surname": "Smith"})
    r.hset("patient:1", mapping={"surname": "Ivanov"})

    r.sadd("doctor-patient:1", "1")

    patients = r.smembers("doctor-patient:1")

    assert "1" in patients
