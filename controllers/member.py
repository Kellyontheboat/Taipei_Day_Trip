from fastapi import APIRouter,FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
#from fastapi.security import OAuth2PasswordRequestForm
from exceptions import CustomHTTPException
from models.members import Member, Token, UserRegister, UserLogin, authenticate_member, create_access_token, get_current_member, check_if_member_exist, hash_pass_save_into_db

router = APIRouter()

@router.put("/api/user/auth", response_model=Token)
#def login_put(form_data: OAuth2PasswordRequestForm = Depends()):
def login_put(user: UserLogin):
    member = authenticate_member(user.email, user.password)
    if not member:
        raise CustomHTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {
        "id": member["id"],
        "email": member["email"]
    }
    token = create_access_token(token_data)
    return {"token": token}

@router.get("/api/user/auth", response_class=JSONResponse)
async def get_member_data(current_member: Member = Depends(get_current_member)):
    if not current_member:
        raise CustomHTTPException(
            status_code=401,
            detail="用戶無此權限",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = current_member
    return JSONResponse(status_code = 200, content = {"data":data})

@router.post("/api/user")
def register_user(user: UserRegister):
    try:
        if check_if_member_exist(user):
            raise CustomHTTPException(status_code=400, detail="此Email已經註冊帳戶")
        hash_pass_save_into_db(user)
        return {"ok": True}
    except HTTPException as e:
        raise e  # Re-raise HTTPException to ensure response handling
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")
    
# @router.get("/api/protected")
# def read_protected_route(current_member: Member = Depends(get_current_member)):
#         return {"message": f"Hello, {current_member['name']}. This is a protected route."}
