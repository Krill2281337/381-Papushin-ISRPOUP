from sqlalchemy.orm import Session
import models


def create_client(db: Session, client):
    new_client = models.Client(**client.dict())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


def create_master(db: Session, master):
    new_master = models.Master(**master.dict())
    db.add(new_master)
    db.commit()
    db.refresh(new_master)
    return new_master


def create_request(db: Session, request):
    new_request = models.Request(
        device_type=request.device_type,
        model=request.model,
        problem=request.problem,
        status="Новая",
        repair_time=0,
        client_id=request.client_id
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


def get_requests(db: Session):
    return db.query(models.Request).all()


def update_status(db: Session, request_id: int, status: str):

    req = db.query(models.Request).get(request_id)

    req.status = status
    db.commit()

    return req


def assign_master(db: Session, request_id: int, master_id: int):

    req = db.query(models.Request).get(request_id)

    req.master_id = master_id
    db.commit()

    return req


def statistics(db: Session):

    total = db.query(models.Request).count()

    finished = db.query(models.Request)\
        .filter(models.Request.status == "Готова")\
        .all()

    if len(finished) == 0:
        avg = 0
    else:
        avg = sum([r.repair_time for r in finished]) / len(finished)

    return {
        "total_requests": total,
        "avg_repair_time": avg
    }