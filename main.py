import uuid,json
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, Cookie, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse 
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
import mimetypes



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


load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_USERDB")]
user_collection = db.users



SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

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


@app.get("/userdata")
async def userdata(current_user: User = Depends(get_current_user)):
    data = user_collection.find_one({"username": current_user.username})
    a = data.get('file', None)
    return a

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    contents = await file.read()
    mime_type = file.content_type

    if mime_type.startswith("image/"):
        resource_type = "image"
    elif mime_type.startswith("video/"):
        resource_type = "video"
    else:
        resource_type = "raw"

    file_ext = mimetypes.guess_extension(mime_type) or ''
    file_uuid = str(uuid.uuid4())  # This will be used as public_id

    upload_result = cloudinary.uploader.upload(
        contents,
        resource_type=resource_type,
        public_id=file_uuid,       #  Set file_uuid as predictable public_id
        use_filename=False,        #  Do not use original filename as public_id
        unique_filename=False,     #  Prevent random hashes in public_id
        overwrite=True,            #  Ensure re-uploads overwrite same ID
        timeout=60,
    )

    cloudinary_url = upload_result.get("secure_url")
    cloudinary_url = cloudinary_url.replace("/upload/", "/upload/fl_attachment/")

    file_info = {               
        "filename": file.filename,
        "file_type": mime_type,
        "file_size": len(contents),
        "file_code": file_uuid, 
        "cloudinary_url": cloudinary_url,
        "resource_type": resource_type,
        "time": str(datetime.utcnow())
    }

    user_collection.update_one(
        {"username": current_user.username},
        {"$push": {"file": file_info}}
    )

    return RedirectResponse(url="/home", status_code=303)

@app.post("/delete/{filename}/{file_code}")
async def delete_file(filename: str, file_code: str, current_user: User = Depends(get_current_user)):
    try:
        # Fetch user's file entry to get resource_type
        user_data = user_collection.find_one({"username": current_user.username})
        user_files = user_data.get("file", [])

        target_file = next((f for f in user_files if f["file_code"] == file_code), None)

        if not target_file:
            raise HTTPException(status_code=404, detail="File not found in MongoDB")

        resource_type = target_file.get("resource_type", "raw")

        # Delete from Cloudinary
        result = cloudinary.uploader.destroy(file_code, resource_type=resource_type)
        print("Cloudinary deletion result:", result)

        if result.get("result") != "ok":
            raise HTTPException(status_code=500, detail=f"Cloudinary deletion failed: {result.get('result')}")

        # Delete from MongoDB
        update = {"$pull": {"file": {"file_code": file_code}}}
        result_db = user_collection.update_one({"username": current_user.username}, update)

        if result_db.modified_count == 0:
            raise HTTPException(status_code=404, detail="File could not be deleted from MongoDB")

        return {"detail": "File deleted from Cloudinary and MongoDB"}
        

    except Exception as e:
        print("Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

