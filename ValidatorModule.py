from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from dataBaseStruc import EventStatus



class EventBase(BaseModel):
    name: str
    description: str = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    status: EventStatus 

class EventResponse(EventBase):
    event_id: int
    status: EventStatus
    
    class Config:
        from_attributes = True

class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    event_id: int

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    attendee_id: int
    check_in_status: bool
    class Config:
        from_attributes = True

class CheckIn(BaseModel):
    check_in_status: bool
