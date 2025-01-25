from locust import HttpUser, task
from ValidatorModule import EventCreate

test_Create_event_data = {
  "name": "string5",
  "description": "string5",
  "start_time": "2025-01-25T16:09:04.336Z",
  "end_time": "2025-01-26T16:09:04.336Z",
  "location": "string",
  "max_attendees": 2
}



class Test_get_requests(HttpUser):
    @task
    def test_get(self):
        self.client.get("/events/?status=scheduled&location=string&date=2025-01-25")
        self.client.get("/events/1/attendees?checked_in=true")
        self.client.post("/events/",EventCreate(**test_Create_event_data).model_dump_json())