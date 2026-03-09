from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import qrcode

from database import (
    add_comment,
    assign_master,
    create_request,
    delete_comment,
    delete_request,
    extend_deadline,
    get_all_comments,
    get_all_requests,
    get_all_users,
    get_client_by_id,
    get_client_requests,
    get_masters,
    get_master_requests,
    get_request_by_id,
    get_statistics,
    get_user_by_login,
    manager_update_request,
    search_requests,
    update_client_request,
    update_parts,
    update_status,
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

STATUSES = [
    "Новая заявка",
    "В процессе ремонта",
    "Ожидание запчастей",
    "Готова к выдаче",
]


def generate_qr():
    url = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link"
    img = qrcode.make(url)
    img.save("static/review_qr.png")


generate_qr()



def get_current_user(request: Request):
    return request.session.get("user")



def ensure_role(request: Request, role: str):
    user = get_current_user(request)
    return bool(user and user.get("type") == role)



def redirect_home():
    return RedirectResponse("/", status_code=303)


@app.get("/")
def home(request: Request):
    user = get_current_user(request)
    if user:
        if user["type"] == "Мастер":
            return RedirectResponse(f"/requests/{user['userID']}", status_code=303)
        if user["type"] == "Заказчик":
            return RedirectResponse(f"/client/{user['userID']}", status_code=303)
        if user["type"] == "Менеджер":
            return RedirectResponse("/manager", status_code=303)
        if user["type"] == "Оператор":
            return RedirectResponse("/operator", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, login: str = Form(...), password: str = Form(...)):
    user = get_user_by_login(login, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин или пароль"},
        )

    request.session["user"] = {
        "userID": user["userID"],
        "type": user["type"],
        "fio": user["fio"],
    }
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect_home()


@app.get("/requests/{master_id}")
def requests_page(request: Request, master_id: int):
    user = get_current_user(request)
    if not user or user["type"] != "Мастер" or user["userID"] != master_id:
        return redirect_home()

    requests = get_master_requests(master_id)
    return templates.TemplateResponse(
        "requests.html",
        {"request": request, "requests": requests, "master_id": master_id, "statuses": STATUSES},
    )


@app.post("/update_status")
def change_status(
    request: Request,
    request_id: int = Form(...),
    status: str = Form(...),
    master_id: int = Form(...),
):
    user = get_current_user(request)
    if not user or user["type"] != "Мастер" or user["userID"] != master_id:
        return redirect_home()
    if status not in STATUSES:
        return RedirectResponse(f"/requests/{master_id}", status_code=303)
    update_status(request_id, status)
    return RedirectResponse(f"/requests/{master_id}", status_code=303)


@app.post("/add_parts")
def add_parts(
    request: Request,
    request_id: int = Form(...),
    parts: str = Form(...),
    master_id: int = Form(...),
):
    user = get_current_user(request)
    if not user or user["type"] != "Мастер" or user["userID"] != master_id:
        return redirect_home()
    update_parts(request_id, parts.strip())
    return RedirectResponse(f"/requests/{master_id}", status_code=303)


@app.post("/add_comment")
def add_master_comment(
    request: Request,
    request_id: int = Form(...),
    comment: str = Form(...),
    master_id: int = Form(...),
):
    user = get_current_user(request)
    if not user or user["type"] != "Мастер" or user["userID"] != master_id:
        return redirect_home()
    if comment.strip():
        add_comment(request_id, master_id, comment.strip())
    return RedirectResponse(f"/requests/{master_id}", status_code=303)


@app.get("/client/{client_id}")
def client_requests_page(request: Request, client_id: int):
    user = get_current_user(request)
    if not user or user["type"] != "Заказчик" or user["userID"] != client_id:
        return redirect_home()

    requests = get_client_requests(client_id)
    client = get_client_by_id(client_id)
    client_name = client["fio"] if client else "Клиент"
    return templates.TemplateResponse(
        "client_requests.html",
        {
            "request": request,
            "requests": requests,
            "client_id": client_id,
            "client_name": client_name,
            "statuses": STATUSES,
        },
    )


@app.get("/create_request")
def create_request_page(request: Request):
    user = get_current_user(request)
    if not user or user["type"] != "Заказчик":
        return redirect_home()
    return templates.TemplateResponse(
        "create_request.html",
        {"request": request, "client_id": user["userID"]},
    )


@app.post("/create_request")
def submit_new_request(
    request: Request,
    homeTechType: str = Form(...),
    homeTechModel: str = Form(...),
    problemDescription: str = Form(...),
):
    user = get_current_user(request)
    if not user or user["type"] != "Заказчик":
        return redirect_home()

    create_request(homeTechType.strip(), homeTechModel.strip(), problemDescription.strip(), user["userID"])
    return RedirectResponse(f"/client/{user['userID']}", status_code=303)


@app.get("/edit_request/{request_id}")
def edit_request_page(request: Request, request_id: int):
    user = get_current_user(request)
    if not user or user["type"] != "Заказчик":
        return redirect_home()

    req = get_request_by_id(request_id)
    if not req or req["clientID"] != user["userID"]:
        return redirect_home()

    return templates.TemplateResponse(
        "create_request.html",
        {"request": request, "client_id": user["userID"], "edit_request": req},
    )


@app.post("/edit_request")
def update_request_by_client(
    request: Request,
    request_id: int = Form(...),
    homeTechType: str = Form(...),
    homeTechModel: str = Form(...),
    problemDescription: str = Form(...),
):
    user = get_current_user(request)
    if not user or user["type"] != "Заказчик":
        return redirect_home()

    update_client_request(
        request_id,
        user["userID"],
        homeTechType.strip(),
        homeTechModel.strip(),
        problemDescription.strip(),
    )
    return RedirectResponse(f"/client/{user['userID']}", status_code=303)


@app.get("/operator")
def operator_page(request: Request):
    if not ensure_role(request, "Оператор"):
        return redirect_home()
    requests = get_all_requests()
    masters = get_masters()
    return templates.TemplateResponse(
        "operator.html",
        {"request": request, "requests": requests, "masters": masters, "statuses": STATUSES},
    )


@app.post("/assign_master")
def assign_master_to_request(
    request: Request,
    request_id: int = Form(...),
    master_id: int = Form(...),
):
    if not ensure_role(request, "Оператор"):
        return redirect_home()
    assign_master(request_id, master_id)
    return RedirectResponse("/operator", status_code=303)


@app.get("/search")
def search(
    request: Request,
    number: str = None,
    status: str = None,
    q: str = None,
):
    user = get_current_user(request)
    if not user or user["type"] not in {"Оператор", "Менеджер"}:
        return redirect_home()

    results = search_requests(number, status, q)
    return templates.TemplateResponse(
        "search_results.html",
        {"request": request, "requests": results, "statuses": STATUSES},
    )


@app.get("/manager")
def manager_page(request: Request):
    if not ensure_role(request, "Менеджер"):
        return redirect_home()
    requests = get_all_requests()
    users = get_all_users()
    comments = get_all_comments()
    masters = get_masters()
    return templates.TemplateResponse(
        "manager.html",
        {
            "request": request,
            "requests": requests,
            "users": users,
            "comments": comments,
            "masters": masters,
            "statuses": STATUSES,
        },
    )


@app.post("/manager_update_request")
def manager_update_request_route(
    request: Request,
    request_id: int = Form(...),
    status: str = Form(...),
    master_id: str = Form(""),
    parts: str = Form(""),
):
    if not ensure_role(request, "Менеджер"):
        return redirect_home()

    master_id_value = int(master_id) if master_id.strip() else None
    parts_value = parts.strip() if parts.strip() else None
    if status not in STATUSES:
        return RedirectResponse("/manager", status_code=303)
    manager_update_request(request_id, status, master_id_value, parts_value)
    return RedirectResponse("/manager", status_code=303)


@app.post("/extend_deadline")
def extend_request_deadline(
    request: Request,
    request_id: int = Form(...),
    new_deadline: str = Form(...),
):
    if not ensure_role(request, "Менеджер"):
        return redirect_home()
    extend_deadline(request_id, new_deadline)
    return RedirectResponse("/manager", status_code=303)


@app.post("/delete_request")
def delete_request_route(request: Request, request_id: int = Form(...)):
    if not ensure_role(request, "Менеджер"):
        return redirect_home()
    delete_request(request_id)
    return RedirectResponse("/manager", status_code=303)


@app.post("/delete_comment")
def delete_comment_route(request: Request, comment_id: int = Form(...)):
    if not ensure_role(request, "Менеджер"):
        return redirect_home()
    delete_comment(comment_id)
    return RedirectResponse("/manager", status_code=303)


@app.get("/statistics")
def statistics_page(request: Request):
    user = get_current_user(request)
    if not user or user["type"] not in {"Менеджер", "Оператор"}:
        return redirect_home()
    stats = get_statistics()
    return templates.TemplateResponse(
        "statistics.html",
        {"request": request, "stats": stats},
    )


@app.get("/review")
def review_page(request: Request):
    if not get_current_user(request):
        return redirect_home()
    return templates.TemplateResponse("review.html", {"request": request})
