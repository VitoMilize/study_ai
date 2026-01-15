#!/usr/bin/env python3
"""
Hospital Management Web App with Redis + Tornado.

Provides CRUD for:
- Hospital
- Doctor
- Patient
- Diagnosis
- Doctor-Patient assignments
"""

import logging
import os
import redis
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

PORT = 8888


def get_redis():
    """Create Redis connection."""
    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True
    )


r = get_redis()


# --- Utility functions --- #
def get_next_id(entity: str) -> int:
    """Return the next auto-increment ID for an entity."""
    ID = r.get(f"{entity}:autoID")
    return int(ID) if ID else 1


def get_entity(entity: str, entity_id: str) -> dict | None:
    """Fetch a single entity by ID from Redis."""
    result = r.hgetall(f"{entity}:{entity_id}")
    return result if result else None


def init_db(redis_client):
    """Initialize Redis keys and auto-increment counters if not exist."""
    if not redis_client.get("db_initiated"):
        for entity in ["hospital", "doctor", "patient", "diagnosis"]:
            redis_client.set(f"{entity}:autoID", 1)
        redis_client.set("db_initiated", 1)


def log_request(*args):
    """Centralized logging helper."""
    logging.debug(" ".join(map(str, args)))


# --- Request Handlers --- #
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")


class AnalyticsHandler(tornado.web.RequestHandler):
    """Provide analytical metrics about the system."""

    def get(self):
        try:
            total_hospitals = get_next_id("hospital") - 1
            total_doctors = get_next_id("doctor") - 1
            total_patients = get_next_id("patient") - 1
            total_diagnoses = get_next_id("diagnosis") - 1

            # Среднее количество пациентов на врача
            doctor_patient_counts = []
            for i in range(1, total_doctors + 1):
                patients = r.smembers(f"doctor-patient:{i}")
                doctor_patient_counts.append(len(patients))
            avg_patients_per_doctor = (
                sum(doctor_patient_counts) / len(doctor_patient_counts)
                if doctor_patient_counts else 0
            )

            # Среднее количество диагнозов на пациента
            patient_diagnosis_counts = {}
            for i in range(1, total_diagnoses + 1):
                diag = get_entity("diagnosis", str(i))
                if diag:
                    pid = diag.get("patient_ID")
                    if pid:
                        patient_diagnosis_counts[pid] = patient_diagnosis_counts.get(pid, 0) + 1
            avg_diagnoses_per_patient = (
                sum(patient_diagnosis_counts.values()) / len(patient_diagnosis_counts)
                if patient_diagnosis_counts else 0
            )

            self.write({
                "total_hospitals": total_hospitals,
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_diagnoses": total_diagnoses,
                "avg_patients_per_doctor": round(avg_patients_per_doctor, 2),
                "avg_diagnoses_per_patient": round(avg_diagnoses_per_patient, 2),
            })

        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write({"error": "Redis connection refused"})


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common get_items logic."""

    entity_name: str = ""

    def get_items(self) -> list[dict]:
        """Retrieve all items for this entity."""
        items = []
        try:
            ID = get_next_id(self.entity_name)
            for i in range(1, ID):
                result = get_entity(self.entity_name, str(i))
                if result:
                    items.append(result)
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        return items


class HospitalHandler(BaseHandler):
    entity_name = "hospital"

    def get(self):
        items = self.get_items()
        self.render("templates/hospital.html", items=items)

    def post(self):
        name = self.get_argument("name")
        address = self.get_argument("address")
        phone = self.get_argument("phone")
        beds_number = self.get_argument("beds_number")

        if not name or not address:
            self.set_status(400)
            self.write("Hospital name and address required")
            return

        ID = get_next_id(self.entity_name)
        r.hset(f"{self.entity_name}:{ID}", mapping={
            "name": name, "address": address,
            "phone": phone, "beds_number": beds_number
        })
        r.incr(f"{self.entity_name}:autoID")
        self.write(f"OK: ID {ID} for {name}")


class DoctorHandler(BaseHandler):
    entity_name = "doctor"

    def get(self):
        items = self.get_items()
        self.render("templates/doctor.html", items=items)

    def post(self):
        surname = self.get_argument("surname")
        profession = self.get_argument("profession")
        hospital_ID = self.get_argument("hospital_ID")

        if not surname or not profession:
            self.set_status(400)
            self.write("Surname and profession required")
            return

        if hospital_ID and not get_entity("hospital", hospital_ID):
            self.set_status(400)
            self.write("No hospital with such ID")
            return

        ID = get_next_id(self.entity_name)
        r.hset(f"{self.entity_name}:{ID}", mapping={
            "surname": surname, "profession": profession, "hospital_ID": hospital_ID
        })
        r.incr(f"{self.entity_name}:autoID")
        self.write(f"OK: ID {ID} for {surname}")


class PatientHandler(BaseHandler):
    entity_name = "patient"

    def get(self):
        items = self.get_items()
        self.render("templates/patient.html", items=items)

    def post(self):
        surname = self.get_argument("surname")
        born_date = self.get_argument("born_date")
        sex = self.get_argument("sex")
        mpn = self.get_argument("mpn")

        if not all([surname, born_date, sex, mpn]):
            self.set_status(400)
            self.write("All fields required")
            return
        if sex not in ("M", "F"):
            self.set_status(400)
            self.write("Sex must be 'M' or 'F'")
            return

        ID = get_next_id(self.entity_name)
        r.hset(f"{self.entity_name}:{ID}", mapping={
            "surname": surname, "born_date": born_date, "sex": sex, "mpn": mpn
        })
        r.incr(f"{self.entity_name}:autoID")
        self.write(f"OK: ID {ID} for {surname}")


class DiagnosisHandler(BaseHandler):
    entity_name = "diagnosis"

    def get(self):
        items = self.get_items()
        self.render("templates/diagnosis.html", items=items)

    def post(self):
        patient_ID = self.get_argument("patient_ID")
        diagnosis_type = self.get_argument("type")
        information = self.get_argument("information")

        if not patient_ID or not diagnosis_type:
            self.set_status(400)
            self.write("Patient ID and diagnosis type required")
            return

        patient = get_entity("patient", patient_ID)
        if not patient:
            self.set_status(400)
            self.write("No patient with such ID")
            return

        ID = get_next_id(self.entity_name)
        r.hset(f"{self.entity_name}:{ID}", mapping={
            "patient_ID": patient_ID,
            "type": diagnosis_type,
            "information": information
        })
        r.incr(f"{self.entity_name}:autoID")
        self.write(f"OK: ID {ID} for patient {patient['surname']}")


class DoctorPatientHandler(tornado.web.RequestHandler):
    """Manage doctor-patient relationships."""

    def get(self):
        items = {}
        try:
            ID = get_next_id("doctor")
            for i in range(1, ID):
                patients = r.smembers(f"doctor-patient:{i}")
                if patients:
                    items[i] = patients
        except redis.exceptions.ConnectionError:
            self.set_status(400)
            self.write("Redis connection refused")
        self.render("templates/doctor-patient.html", items=items)

    def post(self):
        doctor_ID = self.get_argument("doctor_ID")
        patient_ID = self.get_argument("patient_ID")

        if not doctor_ID or not patient_ID:
            self.set_status(400)
            self.write("ID required")
            return

        if not get_entity("doctor", doctor_ID) or not get_entity("patient", patient_ID):
            self.set_status(400)
            self.write("No such ID for doctor or patient")
            return

        r.sadd(f"doctor-patient:{doctor_ID}", patient_ID)
        self.write(f"OK: doctor ID: {doctor_ID}, patient ID: {patient_ID}")


# --- Tornado app --- #
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/hospital", HospitalHandler),
        (r"/doctor", DoctorHandler),
        (r"/patient", PatientHandler),
        (r"/diagnosis", DiagnosisHandler),
        (r"/doctor-patient", DoctorPatientHandler),
        (r"/analytics", AnalyticsHandler),
    ], autoreload=True, debug=True, compiled_template_cache=False, serve_traceback=True)


if __name__ == "__main__":
    init_db(r)
    app = make_app()
    app.listen(PORT)
    parse_command_line()
    logging.info(f"Listening on port {PORT}")
    tornado.ioloop.IOLoop.current().start()
