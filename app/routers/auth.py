from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, AuthProvider
from ..schemas import (
    LoginRequest, RegisterRequest, GoogleAuthRequest,
    TokenResponse, RefreshTokenRequest, UserResponse
)
from ..utils import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, verify_token,
    get_zodiac_sign_id
)
from ..services.google_oauth import verify_google_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    # Check if email exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Calculate zodiac sign
    zodiac_sign_id = get_zodiac_sign_id(request.birth_date)

    # Create user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        auth_provider=AuthProvider.email,
        name=request.name,
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        birth_location=request.birth_location,
        birth_latitude=request.birth_latitude,
        birth_longitude=request.birth_longitude,
        zodiac_sign_id=zodiac_sign_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account disabled")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth."""
    # Verify Google token
    google_info = await verify_google_token(request.id_token)
    if not google_info:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    # Check if user exists
    user = db.query(User).filter(User.google_id == google_info["google_id"]).first()

    if not user:
        # Check if email already used with password auth
        existing_user = db.query(User).filter(User.email == google_info["email"]).first()
        if existing_user:
            # Link Google account to existing user
            existing_user.google_id = google_info["google_id"]
            user = existing_user
        else:
            # New user - need additional info
            if not all([request.birth_date, request.birth_time, request.birth_location]):
                raise HTTPException(
                    status_code=422,
                    detail="New users must provide birth_date, birth_time, and birth_location"
                )

            zodiac_sign_id = get_zodiac_sign_id(request.birth_date)

            user = User(
                email=google_info["email"],
                google_id=google_info["google_id"],
                auth_provider=AuthProvider.google,
                name=request.name or google_info["name"],
                birth_date=request.birth_date,
                birth_time=request.birth_time,
                birth_location=request.birth_location,
                birth_latitude=request.birth_latitude,
                birth_longitude=request.birth_longitude,
                zodiac_sign_id=zodiac_sign_id,
                avatar_url=google_info.get("picture"),
                is_email_verified=google_info.get("email_verified", False),
            )
            db.add(user)

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Generate new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
