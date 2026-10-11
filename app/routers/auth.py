from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.career import User

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    hash_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    token_hash = hash_token(token)

    user = db.query(User).filter(
        User.auth_token_hash == token_hash
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return user


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    if len(request.password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters."
        )

    existing_user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    user = User(
        name=request.name.strip(),
        email=request.email.lower(),
        password_hash=hash_password(
            request.password
        )
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    token = create_token()

    user.auth_token_hash = hash_token(token)

    db.commit()

    return {
        "success": True,
        "message": "Account created successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_token()

    user.auth_token_hash = hash_token(token)

    db.commit()

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    current_user.auth_token_hash = None

    db.commit()

    return {
        "success": True,
        "message": "Logged out successfully."
    }


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):

    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    }