"""POST /auth/login — the only auth endpoint. Returns a JWT to use on every protected request after."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import verify_admin_credentials, create_access_token

router = APIRouter()


@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_admin_credentials(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token()
    return {"access_token": token, "token_type": "bearer"}