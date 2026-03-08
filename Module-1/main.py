from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import (
    get_user_by_login, get_master_requests, update_status,
    update_parts, get_client_requests, get_all_requests, create_request
)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey")  # Сессии через куки

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Главная страница (логин)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Авторизация

@app.post("/login")
def login(request: Request, login: str = Form(...), password: str = Form(...)):
    user = get_user_by_login(login, password)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )

    # Сохраняем пользователя в сессии
    request.session["user"] = {"userID": user["userID"], "type": user["type"]}

    user_id = user["userID"]
    user_type = user["type"]

    if user_type == "Мастер":
        return RedirectResponse(f"/requests/{user_id}", status_code=303)
    if user_type == "Заказчик":
        return RedirectResponse(f"/client/{user_id}", status_code=303)
    if user_type == "Менеджер":
        return RedirectResponse("/manager", status_code=303)
    if user_type == "Оператор":
        return RedirectResponse("/operator", status_code=303)

    return RedirectResponse("/", status_code=303)


# Выход

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# Страница мастера

@app.get("/requests/{master_id}")
def requests_page(request: Request, master_id: int):
    requests = get_master_requests(master_id)
    return templates.TemplateResponse(
        "requests.html",
        {"request": request, "requests": requests, "master_id": master_id}
    )


# Изменение статуса заявки

@app.post("/update_status")
def change_status(
    request_id: int = Form(...),
    status: str = Form(...),
    master_id: int = Form(...)
):
    update_status(request_id, status)
    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# Добавление запчастей

@app.post("/add_parts")
def add_parts(
    request_id: int = Form(...),
    parts: str = Form(...),
    master_id: int = Form(...)
):
    update_parts(request_id, parts)
    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# Страница клиента

@app.get("/client/{client_id}")
def client_requests(request: Request, client_id: int):
    requests = get_client_requests(client_id)
    return templates.TemplateResponse(
        "client_requests.html",
        {"request": request, "requests": requests, "client_id": client_id}
    )


# Создание заявки (для клиента)

@app.get("/create_request")
def create_request_page(request: Request):
    user = request.session.get("user")
    if not user or user["type"] != "Заказчик":
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "create_request.html",
        {"request": request, "client_id": user["userID"]}
    )

@app.post("/create_request")
def submit_new_request(
    request: Request,
    homeTechType: str = Form(...),
    homeTechModel: str = Form(...),
    problemDescription: str = Form(...)
):
    user = request.session.get("user")
    if not user or user["type"] != "Заказчик":
        return RedirectResponse("/", status_code=303)

    client_id = user["userID"]
    create_request(homeTechType, homeTechModel, problemDescription, client_id)
    return RedirectResponse(f"/client/{client_id}", status_code=303)


# Менеджер

@app.get("/manager")
def manager_page(request: Request):
    requests = get_all_requests()
    return templates.TemplateResponse(
        "manager.html",
        {"request": request, "requests": requests}
    )


# Оператор

@app.get("/operator")
def operator_page(request: Request):
    requests = get_all_requests()
    return templates.TemplateResponse(
        "operator.html",
        {"request": request, "requests": requests}
    )