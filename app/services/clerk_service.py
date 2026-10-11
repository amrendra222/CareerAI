import httpx

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions

from app.config import settings
from app.models.career import User


def authenticate_clerk_request(request: Request) -> str:
    """
    Validate the Clerk session token and return the Clerk user ID.
    """

    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication header."
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    try:
        clerk_request = httpx.Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers)
        )

        clerk = Clerk(
            bearer_auth=settings.CLERK_SECRET_KEY
        )

        auth_state = clerk.authenticate_request(
            clerk_request,
            AuthenticateRequestOptions(
                publishable_key=settings.CLERK_PUBLISHABLE_KEY,
                authorized_parties=[
                    "http://127.0.0.1:5500",
                    "http://localhost:5500"
                ]
            )
        )

        print(
            "Clerk authentication:",
            auth_state.is_signed_in,
            "reason:",
            auth_state.reason
        )

        if not auth_state.is_signed_in:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired authentication token."
            )

        payload = auth_state.payload or {}

        clerk_user_id = payload.get("sub")

        if not clerk_user_id:
            raise HTTPException(
                status_code=401,
                detail="Clerk user ID not found."
            )

        return clerk_user_id

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Clerk authentication error:",
            repr(error)
        )

        raise HTTPException(
            status_code=401,
            detail="Authentication verification failed."
        )


def get_current_clerk_user(
    request: Request,
    db: Session
) -> User:
    """
    Authenticate the Clerk user and connect that Clerk account
    to the local CareerAI User record.
    """

    clerk_user_id = authenticate_clerk_request(request)

    # First try to find the CareerAI user using clerk_id.
    user = (
        db.query(User)
        .filter(
            User.clerk_id == clerk_user_id
        )
        .first()
    )

    if user:
        return user

    # Get the Clerk user details from Clerk Backend API.
    try:
        response = httpx.get(
            f"https://api.clerk.com/v1/users/{clerk_user_id}",
            headers={
                "Authorization":
                    f"Bearer {settings.CLERK_SECRET_KEY}"
            },
            timeout=10.0
        )

        response.raise_for_status()

        clerk_user = response.json()

    except Exception as error:
        print(
            "Could not retrieve Clerk user:",
            repr(error)
        )

        raise HTTPException(
            status_code=401,
            detail="Could not retrieve authenticated Clerk user."
        )

    first_name = (
        clerk_user.get("first_name")
        or ""
    ).strip()

    last_name = (
        clerk_user.get("last_name")
        or ""
    ).strip()

    full_name = (
        f"{first_name} {last_name}"
    ).strip()

    if not full_name:
        full_name = "CareerAI User"

    email_addresses = (
        clerk_user.get("email_addresses")
        or []
    )

    email = None

    primary_email_id = clerk_user.get(
        "primary_email_address_id"
    )

    for email_item in email_addresses:

        if (
            email_item.get("id")
            == primary_email_id
        ):
            email = email_item.get(
                "email_address"
            )
            break

    if not email and email_addresses:
        email = email_addresses[0].get(
            "email_address"
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="No email address found for Clerk user."
        )

    email = email.strip().lower()

    # If an old CareerAI user already exists with this email,
    # connect that record to Clerk.
    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if user:
        user.clerk_id = clerk_user_id

        db.commit()
        db.refresh(user)

        print(
            "CareerAI user linked to Clerk:",
            user.id,
            clerk_user_id
        )

        return user

    # Otherwise create a new CareerAI user.
    user = User(
        clerk_id=clerk_user_id,
        name=full_name,
        email=email,
        password_hash="CLERK_MANAGED"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(
        "CareerAI user created from Clerk:",
        user.id,
        clerk_user_id
    )

    return user