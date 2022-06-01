import uvicorn
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Security
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from backend.app.config.auth import AuthHandler
from backend.app.config.conn import get_db
from backend.app.models.model_admin import Model_admin
from backend.app.routes import crud

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_handler = AuthHandler()

templates = Jinja2Templates(directory="templates")

app.include_router(crud.router)
# app.include_router(security.router)

@app.get("/", response_class=HTMLResponse)
def get_main_page(request: Request):    # 메인화면
    return templates.TemplateResponse("index.html", context= {"request": request})

@app.get("/index_admin", response_class=HTMLResponse)
def get_main_admin(request: Request, ):   # 관리자 메인화면
    return templates.TemplateResponse("index_admin.html", context= {"request": request})

@app.get("/attendee_today/", response_class=HTMLResponse)
def get_attendance_table_page(request: Request):   # 학부모들이 출석 완료 후 보여지는 화면
    return templates.TemplateResponse("attendee_today.html", context= {"request": request})

@app.get("/attend_success", response_class=HTMLResponse)
def get_attend_success(request: Request):   # 출석 완료창
    return templates.TemplateResponse("attend_success.html", context= {"request": request})

@app.get("/attendance_table", response_class=HTMLResponse)
def get_attendance_table_page(request: Request):   # 출석부화면
    return templates.TemplateResponse("attendance_table.html", context= {"request": request})

@app.get("/login_page/", response_class=HTMLResponse)
def get_login_page(request: Request):   # 로그인화면
    return templates.TemplateResponse("login.html", context= {"request": request})

@app.get("/attend/", response_class=HTMLResponse)
def get_attend_input_page(request: Request):  # 출석등록 화면
    return templates.TemplateResponse("attend.html", context= {"request": request})

@app.get("/protected", response_class=HTMLResponse)
def get_main_admin(request: Request, username=Depends(auth_handler.auth_wrapper)):

    return templates.TemplateResponse("index_admin.html", context= {"request": request})

@app.post('/secret')
def secret(username = Depends(auth_handler.auth_wrapper)):
    token = username.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@app.post("/register")   # 관리자 계정 생성
def register(username: str, password: str, db: Session = Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).all()
    if user_db:
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(password)
    admin_db = Model_admin(username = username,
                           password = hashed_password)
    db.add(admin_db)
    db.commit()
    return

@app.post('/login/')  # 관리자 로그인
def login(username: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user_db = db.query(Model_admin).filter(Model_admin.username == username).first()
    # user_db = get_user_by_username(username=username)
    user = None
    if user_db:
        user = username
    if (user is None) or (not auth_handler.verify_password(password, user_db.password)):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # token = dict(Authorization=f"Bearer {auth_handler.encode_token(user_db.username)}")
    access_token = auth_handler.encode_token(username)
    # context = {}
    # context['request'] = request
    # context['authorization'] = token
    # # 관리자 페이지 렌더링 리턴할때 context도 같이 전달
    # return templates.TemplateResponse("login_success.html", context)
    return {'access_token': access_token}


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


