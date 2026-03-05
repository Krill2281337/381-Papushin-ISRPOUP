from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from passlib.hash import bcrypt
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.post("/register")
def register(

        username: str = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        db: Session = Depends(get_db)

):

    user = models.User(
        username=username,
        password=bcrypt.hash(password),
        role=role
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/", 303)


@app.get("/add_request", response_class=HTMLResponse)
def add_page(request: Request):

    return templates.TemplateResponse(
        "add_request.html",
        {"request": request}
    )


@app.post("/add_request")
def add_request(

        device: str = Form(...),
        model: str = Form(...),
        problem: str = Form(...),
        client: str = Form(...),
        phone: str = Form(...),

        db: Session = Depends(get_db)

):

    client_obj = models.Client(
        name=client,
        phone=phone
    )

    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    req = models.Request(

        device=device,
        model=model,
        problem=problem,
        status="Новая",
        repair_time=0,
        client_id=client_obj.id

    )

    db.add(req)
    db.commit()

    return RedirectResponse("/requests", 303)


@app.get("/requests", response_class=HTMLResponse)
def requests_page(

        request: Request,
        db: Session = Depends(get_db)

):

    requests = db.query(models.Request).all()

    return templates.TemplateResponse(
        "requests.html",
        {
            "request": request,
            "requests": requests
        }
    )