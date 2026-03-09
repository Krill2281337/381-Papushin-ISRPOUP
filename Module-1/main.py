from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import qrcode

from database import (
    get_user_by_login,
    get_master_requests,
    update_status,
    update_parts,
    get_client_requests,
    get_all_requests,
    create_request,
    assign_master,
    add_comment,
    extend_deadline,
    search_requests,
    get_statistics
)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------
# Генерация QR-кода
# ------------------------------------------------

def generate_qr():
    url = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform"
    img = qrcode.make(url)
    img.save("static/review_qr.png")

generate_qr()


# ------------------------------------------------
# Проверка роли
# ------------------------------------------------

def check_role(request: Request, role: str):

    user = request.session.get("user")

    if not user:
        return False

    if user["type"] != role:
        return False

    return True


# ------------------------------------------------
# Главная
# ------------------------------------------------

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ------------------------------------------------
# Авторизация
# ------------------------------------------------

@app.post("/login")
def login(request: Request, login: str = Form(...), password: str = Form(...)):

    user = get_user_by_login(login, password)

    if not user:

        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )

    request.session["user"] = {
        "userID": user["userID"],
        "type": user["type"],
        "fio": user["fio"]
    }

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


# ------------------------------------------------
# Выход
# ------------------------------------------------

@app.post("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/", status_code=303)


# ------------------------------------------------
# Мастер
# ------------------------------------------------

@app.get("/requests/{master_id}")
def requests_page(request: Request, master_id: int):

    if not check_role(request, "Мастер"):
        return RedirectResponse("/", status_code=303)

    requests = get_master_requests(master_id)

    return templates.TemplateResponse(
        "requests.html",
        {
            "request": request,
            "requests": requests,
            "master_id": master_id,
            "user": request.session.get("user")
        }
    )


# ------------------------------------------------
# Изменение статуса
# ------------------------------------------------

@app.post("/update_status")
def change_status(
    request_id: int = Form(...),
    status: str = Form(...),
    master_id: int = Form(...)
):

    update_status(request_id, status)

    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# ------------------------------------------------
# Запчасти
# ------------------------------------------------

@app.post("/add_parts")
def add_parts(
    request_id: int = Form(...),
    parts: str = Form(...),
    master_id: int = Form(...)
):

    update_parts(request_id, parts)

    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# ------------------------------------------------
# Комментарий
# ------------------------------------------------

@app.post("/add_comment")
def add_master_comment(
    request_id: int = Form(...),
    comment: str = Form(...),
    master_id: int = Form(...)
):

    add_comment(request_id, master_id, comment)

    return RedirectResponse(f"/requests/{master_id}", status_code=303)


# ------------------------------------------------
# Клиент
# ------------------------------------------------

@app.get("/client/{client_id}")
def client_requests(request: Request, client_id: int):

    if not check_role(request, "Заказчик"):
        return RedirectResponse("/", status_code=303)

    requests = get_client_requests(client_id)

    return templates.TemplateResponse(
        "client_requests.html",
        {
            "request": request,
            "requests": requests,
            "client_id": client_id,
            "user": request.session.get("user")
        }
    )


# ------------------------------------------------
# Создание заявки
# ------------------------------------------------

@app.get("/create_request")
def create_request_page(request: Request):

    if not check_role(request, "Заказчик"):
        return RedirectResponse("/", status_code=303)

    user = request.session.get("user")

    return templates.TemplateResponse(
        "create_request.html",
        {
            "request": request,
            "client_id": user["userID"]
        }
    )


@app.post("/create_request")
def submit_new_request(
    request: Request,
    homeTechType: str = Form(...),
    homeTechModel: str = Form(...),
    problemDescription: str = Form(...)
):

    if not check_role(request, "Заказчик"):
        return RedirectResponse("/", status_code=303)

    user = request.session.get("user")

    create_request(
        homeTechType,
        homeTechModel,
        problemDescription,
        user["userID"]
    )

    return RedirectResponse(f"/client/{user['userID']}", status_code=303)


# ------------------------------------------------
# Оператор
# ------------------------------------------------

@app.get("/operator")
def operator_page(request: Request):

    if not check_role(request, "Оператор"):
        return RedirectResponse("/", status_code=303)

    requests = get_all_requests()

    return templates.TemplateResponse(
        "operator.html",
        {
            "request": request,
            "requests": requests,
            "user": request.session.get("user")
        }
    )


@app.post("/assign_master")
def assign_master_to_request(
    request_id: int = Form(...),
    master_id: int = Form(...)
):

    assign_master(request_id, master_id)

    return RedirectResponse("/operator", status_code=303)


# ------------------------------------------------
# Менеджер
# ------------------------------------------------

@app.get("/manager")
def manager_page(request: Request):

    if not check_role(request, "Менеджер"):
        return RedirectResponse("/", status_code=303)

    requests = get_all_requests()

    return templates.TemplateResponse(
        "manager.html",
        {
            "request": request,
            "requests": requests,
            "user": request.session.get("user")
        }
    )


# ------------------------------------------------
# Продление срока
# ------------------------------------------------

@app.post("/extend_deadline")
def extend_request_deadline(
    request_id: int = Form(...),
    new_deadline: str = Form(...)
):

    extend_deadline(request_id, new_deadline)

    return RedirectResponse("/manager", status_code=303)


# ------------------------------------------------
# Статистика
# ------------------------------------------------

@app.get("/statistics")
def statistics_page(request: Request):

    if not check_role(request, "Менеджер"):
        return RedirectResponse("/", status_code=303)

    stats = get_statistics()

    return templates.TemplateResponse(
        "statistics.html",
        {
            "request": request,
            "stats": stats
        }
    )


# ------------------------------------------------
# QR отзыв
# ------------------------------------------------

@app.get("/review")
def review_page(request: Request):

    return templates.TemplateResponse(
        "review.html",
        {"request": request}
    )