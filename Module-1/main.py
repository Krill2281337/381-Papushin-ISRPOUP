from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# главная страница (логин)
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# авторизация
@app.post("/login")
def login(request: Request, login: str = Form(...), password: str = Form(...)):

    user = get_user_by_login(login, password)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный логин или пароль"
            }
        )

    master_id = user["id"]

    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# страница заявок мастера
@app.get("/requests/{master_id}")
def requests_page(request: Request, master_id: int):

    requests = get_master_requests(master_id)

    return templates.TemplateResponse(
        "requests.html",
        {
            "request": request,
            "requests": requests,
            "master_id": master_id
        }
    )


# изменение статуса заявки
@app.post("/update_status")
def change_status(
        request_id: int = Form(...),
        status: str = Form(...),
        master_id: int = Form(...)
):

    update_status(request_id, status)

    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# добавление запчастей
@app.post("/add_parts")
def add_parts(
        request_id: int = Form(...),
        parts: str = Form(...),
        master_id: int = Form(...)
):

    update_parts(request_id, parts)

    return RedirectResponse(f"/requests/{master_id}", status_code=303)