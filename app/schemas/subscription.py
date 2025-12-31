from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionStatusResponse(BaseModel):
    """Response for subscription status."""
    tier: str  # "free" or "premium"
    is_premium: bool
    expires_at: Optional[datetime] = None
    platform: Optional[str] = None
    product_id: Optional[str] = None

    class Config:
        from_attributes = True


class RevenueCatWebhookEvent(BaseModel):
    """RevenueCat webhook event payload."""
    event: dict
    api_version: str


class RestorePurchaseRequest(BaseModel):
    """Request to restore purchases."""
    revenuecat_customer_id: str
    platform: str  # "android" or "ios"
