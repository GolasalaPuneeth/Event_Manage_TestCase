from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from datetime import datetime
from ValidatorModule import EventCreate,EventResponse,EventUpdate,EventStatus,AttendeeCreate,AttendeeResponse,CheckIn
from dataBaseStruc import get_db,Event,Session,Attendee,func
import uvicorn

app = FastAPI()

# Endpoints
@app.post("/events/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if not event.status:
        now = datetime.now()
        if now > db_event.end_time:
            db_event.status = EventStatus.COMPLETED.value
        elif db_event.start_time <= now <= db_event.end_time:
            db_event.status = EventStatus.ONGOING.value
    
    for key, value in event.model_dump(exclude_unset=True).items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@app.post("/events/{event_id}/attendees", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
def register_attendee(event_id: int, attendee: AttendeeCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    current_attendees = db.query(Attendee).filter(Attendee.event_id == event_id).count()
    if current_attendees >= event.max_attendees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event has reached maximum attendees"
        )
    
    if db.query(Attendee).filter(Attendee.email == attendee.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_attendee = Attendee(**attendee.model_dump())
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

@app.put("/attendees/{attendee_id}/check-in", response_model=AttendeeResponse)
def check_in_attendee(attendee_id: int, check_in: CheckIn, db: Session = Depends(get_db)):
    attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    
    attendee.check_in_status = check_in.check_in_status
    db.commit()
    db.refresh(attendee)
    return attendee


@app.get("/events/", response_model=list[EventResponse] )
def list_events(
    status: EventStatus,
    location: str,
    date: datetime,
    db: Session = Depends(get_db)
):
    query = db.query(Event)
    now = datetime.now()
    events = query.all()
    for event in events:
        print(now,event.end_time,event.status)
        if now > event.end_time and event.status != EventStatus.COMPLETED.value:
            event.status = EventStatus.COMPLETED.value
            db.add(event)
    db.commit()
    if status:
        query = query.filter(Event.status == status)
    if location:
        query = query.filter(Event.location.contains(location))
    if date:
        query = query.filter(func.date(Event.start_time) == func.date(date))
    return query.all()


@app.get("/events/{event_id}/attendees", response_model=list[AttendeeResponse])
def list_attendees(event_id: int, checked_in: bool = None, db: Session = Depends(get_db)):
    query = db.query(Attendee).filter(Attendee.event_id == event_id)
    if checked_in is not None:
        query = query.filter(Attendee.check_in_status == checked_in)
    return query.all()



@app.post("/attendees/bulk-checkin/")
def bulk_check_in(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"message": "Bulk check-in processing not implemented yet"}


if __name__ == "__main__":
    uvicorn.run(app,port=3000)