import uuid,json
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
import jwt 
from jwt import PyJWTError as JWTError 
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
from gridfs import GridFS
# from jose import JWTError
# from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

client = MongoClient('mongodb://localhost:27017')
db = client.user_database
user_collection = db.users
fs = GridFS(db, collection="files")
fs_chunks = db['files.chunks']
fs_files = db['files.files']

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError: # type: ignore
        raise credentials_exception
    user = user_collection.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return User(**user)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("dash.html", {"request": request})

@app.get("/login")
async def new_page(request: Request):
    return templates.TemplateResponse("login3.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = user_collection.find_one({"username": username})
    if user and verify_password(password, user["password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
        json_response = JSONResponse(content={"exists": False})
        json_response.set_cookie(key="token", value=access_token)
        return json_response
    else:
        return {"exists": True}


@app.get("/dash")
async def new_page(request: Request):
    return templates.TemplateResponse("dash.html", {"request": request})



@app.get("/signup")
async def new_page(request: Request):
    return templates.TemplateResponse("signup3.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    if not user_collection.find_one({"username": username}):
        hashed_password = get_password_hash(password)
        user = {"username": username, "password": hashed_password}
        user_collection.insert_one(user)
        return JSONResponse(content={"exists": False})
    else:
        return {"exists": True}

@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="token")
    return response


@app.get("/home")
async def home(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("HomePage2.html", {"request": request, "username": current_user.username})

@app.get("/download/{filecode}")
async def download_file(filecode: str):
    file_data = fs_files.find_one({"file_code": filecode})
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    data = fs.get(file_data['_id'])
    return Response(content=data.read(), media_type=file_data['contentType'], headers={
        "Content-Disposition": f"attachment; filename={file_data['filename']}"
    })

@app.post("/upload")
async def upload_file( file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    num = str(uuid.uuid4())
    print(file.content_type)
    print(file.filename)
    update = {"$push": {"file": {num: file.filename,"num":num , "filename":file.filename, "file_size": file.size,"time":str(datetime.utcnow()),"file_type":file.content_type}}}
    user_collection.update_one({"username": current_user.username}, update)
    fs.put(file.file, filename=file.filename, content_type=file.content_type, username=current_user.username, file_code=num)
    return RedirectResponse(url="/home",status_code=303)

@app.post("/delete/{filename}/{filecode}")
async def delete_file(filename: str, filecode: str, current_user: User = Depends(get_current_user)):
    file_id = fs_files.find_one_and_delete({"file_code": filecode})
    fs_chunks.delete_many({"files_id": file_id["_id"]})
    update = {"$pull": {"file": {filecode: filename}}}
    user_collection.update_one({"username": current_user.username}, update)
    return {"detail": "File deleted successfully"}

@app.get("/userdata")
async def userdata(current_user: User = Depends(get_current_user)):
    data = user_collection.find_one({"username": current_user.username})
    a=data['file']
    return a
