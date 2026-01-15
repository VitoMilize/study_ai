from locust import HttpUser, task, between
import random


class HospitalUser(HttpUser):
    wait_time = between(1, 3)  # пауза между запросами

    @task(3)  # GET выполняем чаще
    def get_hospitals(self):
        self.client.get("/hospital")

    @task(1)  # POST выполняем реже
    def add_hospital(self):
        data = {
            "name": f"Hospital {random.randint(1, 1000)}",
            "address": f"Street {random.randint(1, 1000)}",
            "beds_number": str(random.randint(10, 500)),
            "phone": f"+7{random.randint(9000000000, 9999999999)}"
        }
        self.client.post("/hospital", data=data)
