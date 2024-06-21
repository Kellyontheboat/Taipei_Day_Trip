from fastapi import APIRouter,FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.members import Member, Token, UserRegister, UserLogin, authenticate_member, create_access_token, get_current_member, check_if_member_exist, hash_pass_save_into_db
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()

@router.put("/api/user/auth", response_model=Token)
#def login_put(form_data: OAuth2PasswordRequestForm = Depends()):
def login_put(user: UserLogin):
    member = authenticate_member(user.email, user.password)
    if not member:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {
        "id": member["id"],
        "email": member["email"]
    }
    token = create_access_token(token_data)
    return {"token": token}

@router.get("/api/user/auth", response_model=Member)
def get_member_data(current_member: Member = Depends(get_current_member)):
    if not current_member:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Member not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_member


@router.post("/api/user")
def register_user(user: UserRegister):
    try:
        if check_if_member_exist(user):
            print (check_if_member_exist(user))
            raise HTTPException(status_code=400, detail="Email already registered")
        hash_pass_save_into_db(user)
        return {"ok": True}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")

        
    
@router.get("/api/protected")
def read_protected_route(current_member: Member = Depends(get_current_member)):
        return {"message": f"Hello, {current_member['name']}. This is a protected route."}