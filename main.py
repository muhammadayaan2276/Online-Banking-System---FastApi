from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# ----- USERS DATABASE -----
users = {
    "Ayaan": {"pin_number": "1111", "balance": 1000},
    "Huzaifa": {"pin_number": "2222", "balance": 700},
    "Ovais": {"pin_number": "3333", "balance": 300},
}

# HTML Templates Folder
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --------------------
# LOGIN PAGE
# --------------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# --------------------
# AUTHENTICATE USER
# --------------------
@app.post("/authenticate")
def authenticate_user(request: Request, name: str = Form(...), pin_number: str = Form(...)):
    if name in users and users[name]["pin_number"] == pin_number:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "name": name,
            "balance": users[name]["balance"]
        })

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid name or PIN!"
    })


# --------------------
# DASHBOARD PAGE
# --------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, name: str):
    if name not in users:
        return templates.TemplateResponse("login.html", {"request": request, "error": "User not found!"})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "name": name,
        "balance": users[name]["balance"]
    })


# --------------------
# BANK TRANSFER PAGE
# --------------------
@app.get("/bank-transfer", response_class=HTMLResponse)
def transfer_page(request: Request, name: str):
    return templates.TemplateResponse("transfer.html", {"request": request, "name": name})


# --------------------
# PROCESS TRANSFER
# --------------------
@app.post("/bank-transfer")
def process_transfer(
    request: Request,
    sender: str = Form(...),
    receipent: str = Form(...),
    amount: int = Form(...)
):
    # Receiver not found
    if receipent not in users:
        return templates.TemplateResponse("transfer.html", {
            "request": request,
            "name": sender,
            "error": "❌ Receiver not found!",
            "balance": users[sender]["balance"]
        })

    # Insufficient balance
    if users[sender]["balance"] < amount:
        return templates.TemplateResponse("transfer.html", {
            "request": request,
            "name": sender,
            "error": "❌ Insufficient balance!",
            "balance": users[sender]["balance"]
        })

    # Deduct from sender
    users[sender]["balance"] -= amount

    # Add to receiver
    users[receipent]["balance"] += amount

    # Redirect to receiver page with sender and amount info
    return RedirectResponse(
        f"/authenticate-receiver?name={receipent}&from_sender={sender}&amount={amount}",
        status_code=302
    )


# --------------------
# AUTHENTICATE RECEIVER (SHOW RECEIVED AMOUNT)
# --------------------
@app.get("/authenticate-receiver", response_class=HTMLResponse)
def auth_receiver(request: Request, name: str, from_sender: str = "", amount: int = 0):
    if name not in users:
        return templates.TemplateResponse("login.html", {"request": request, "error": "User not found!"})

    return templates.TemplateResponse("receiver.html", {
        "request": request,
        "name": name,
        "balance": users[name]["balance"],
        "from_sender": from_sender,
        "amount_received": amount
    })
