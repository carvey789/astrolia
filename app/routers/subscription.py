from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, SubscriptionTier
from ..schemas.subscription import (
    SubscriptionStatusResponse,
    RevenueCatWebhookEvent,
    RestorePurchaseRequest
)
from ..utils import get_current_user

router = APIRouter(prefix="/subscription", tags=["Subscription"])


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
):
    """Get current user's subscription status."""
    return SubscriptionStatusResponse(
        tier=current_user.subscription_tier.value,
        is_premium=current_user.is_premium,
        expires_at=current_user.subscription_expires_at,
        platform=current_user.subscription_platform,
        product_id=current_user.subscription_product_id,
    )


@router.post("/webhook")
async def handle_revenuecat_webhook(
    event: RevenueCatWebhookEvent,
    db: Session = Depends(get_db),
):
    """
    Handle RevenueCat webhook events.

    Events:
    - INITIAL_PURCHASE: User subscribed
    - RENEWAL: Subscription renewed
    - CANCELLATION: User cancelled (but still active until expires)
    - EXPIRATION: Subscription expired
    - BILLING_ISSUE: Payment failed
    """
    try:
        event_data = event.event
        event_type = event_data.get("type", "")
        subscriber_id = event_data.get("app_user_id", "")

        if not subscriber_id:
            return {"status": "ignored", "reason": "no subscriber_id"}

        # Find user by RevenueCat ID
        user = db.query(User).filter(User.revenuecat_id == subscriber_id).first()

        if not user:
            # Try to find by email (fallback)
            email = event_data.get("subscriber_attributes", {}).get("$email", {}).get("value")
            if email:
                user = db.query(User).filter(User.email == email).first()

        if not user:
            return {"status": "ignored", "reason": "user not found"}

        # Handle different event types
        if event_type in ["INITIAL_PURCHASE", "RENEWAL", "PRODUCT_CHANGE"]:
            # Subscription is active
            product_id = event_data.get("product_id", "")
            expiration = event_data.get("expiration_at_ms")

            user.subscription_tier = SubscriptionTier.premium
            user.subscription_product_id = product_id

            if expiration:
                user.subscription_expires_at = datetime.fromtimestamp(expiration / 1000)
            else:
                # Default to 1 month if no expiration provided
                user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)

        elif event_type in ["EXPIRATION", "BILLING_ISSUE"]:
            # Subscription expired or payment failed
            user.subscription_tier = SubscriptionTier.free

        elif event_type == "CANCELLATION":
            # User cancelled but subscription remains active until expiry
            # We don't change the tier here, just note it expired at the end date
            pass

        db.commit()
        return {"status": "ok", "event_type": event_type}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/restore")
async def restore_purchases(
    request: RestorePurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Restore purchases - called after RevenueCat restores purchases on device.
    The actual verification happens via RevenueCat SDK + webhook.
    This endpoint links the RevenueCat customer ID to our user.
    """
    current_user.revenuecat_id = request.revenuecat_customer_id
    current_user.subscription_platform = request.platform
    db.commit()

    return {
        "status": "ok",
        "message": "RevenueCat ID linked. Subscription will sync via webhook."
    }


@router.post("/grant-premium")
async def grant_premium(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    DEV ONLY: Grant premium subscription for testing.
    Remove this endpoint in production!
    """
    current_user.subscription_tier = SubscriptionTier.premium
    current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=days)
    current_user.subscription_platform = "test"
    db.commit()

    return {
        "status": "ok",
        "message": f"Premium granted for {days} days",
        "expires_at": current_user.subscription_expires_at.isoformat()
    }


@router.post("/revoke-premium")
async def revoke_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    DEV ONLY: Remove premium subscription for testing.
    Remove this endpoint in production!
    """
    current_user.subscription_tier = SubscriptionTier.free
    current_user.subscription_expires_at = None
    current_user.subscription_platform = None
    current_user.subscription_product_id = None
    db.commit()

    return {
        "status": "ok",
        "message": "Premium subscription removed"
    }
