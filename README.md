# Hospital Management Web App

Веб-приложение для управления:
- Больницами
- Врачами
- Пациентами
- Диагнозами
- Назначениями врач-пациент

### Стек технологий
- Python 3.11
- Tornado (Web Server)
- Redis (хранение данных)
- Bootstrap 4 (Frontend)

### Архитектура
- Redis хранит данные в виде хэшей и множеств:
  - `hospital:<ID>` → {name, address, phone, beds_number}
  - `doctor:<ID>` → {surname, profession, hospital_ID}
  - `patient:<ID>` → {surname, born_date, sex, mpn}
  - `diagnosis:<ID>` → {patient_ID, type, information}
  - `doctor-patient:<doctor_ID>` → set(patient_ID)
- Tornado предоставляет HTTP API и HTML-шаблоны.

### Запуск
```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
python3 main.py
