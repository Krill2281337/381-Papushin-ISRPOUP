from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date

from database import SessionLocal, engine, Base
from models import User, Request, Comment
from fastapi import Request as FastAPIRequest

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def login_page(request: FastAPIRequest):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
        request: FastAPIRequest,
        login: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):

    user = db.query(User)\
        .filter(User.login == login)\
        .filter(User.password == password)\
        .first()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )

    return RedirectResponse("/requests", status_code=303)


@app.get("/requests", response_class=HTMLResponse)
def requests_page(request: FastAPIRequest, db: Session = Depends(get_db)):

    requests = db.query(Request).all()

    return templates.TemplateResponse(
        "requests.html",
        {"request": request, "requests": requests}
    )


@app.get("/create", response_class=HTMLResponse)
def create_page(request: FastAPIRequest):
    return templates.TemplateResponse("create_request.html", {"request": request})


@app.post("/create")
def create_request(
        type: str = Form(...),
        model: str = Form(...),
        problem: str = Form(...),
        db: Session = Depends(get_db)
):

    new_request = Request(
        startDate=str(date.today()),
        homeTechType=type,
        homeTechModel=model,
        problemDescription=problem,
        requestStatus="Новая заявка"
    )

    db.add(new_request)
    db.commit()

    return RedirectResponse("/requests", status_code=303)


@app.get("/comments/{request_id}", response_class=HTMLResponse)
def comments_page(request_id: int,
                  request: FastAPIRequest,
                  db: Session = Depends(get_db)):

    comments = db.query(Comment)\
        .filter(Comment.requestID == request_id)\
        .all()

    return templates.TemplateResponse(
        "comments.html",
        {"request": request, "comments": comments, "request_id": request_id}
    )


@app.post("/comments/{request_id}")
def add_comment(
        request_id: int,
        message: str = Form(...),
        db: Session = Depends(get_db)
):

    comment = Comment(
        message=message,
        masterID=1,
        requestID=request_id
    )

    db.add(comment)
    db.commit()

    return RedirectResponse(f"/comments/{request_id}", status_code=303)