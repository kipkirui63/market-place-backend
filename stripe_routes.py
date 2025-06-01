### stripe_routes.py
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User, Subscription
from utils import verify_token
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

stripe_router = APIRouter()

@stripe_router.post("/create-checkout")
def create_checkout(token: str, product: str, db: Session = Depends(get_db)):
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()

    existing_sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if existing_sub:
        raise HTTPException(status_code=400, detail="Subscription already exists")

    price_ids = {
        "bi_agent": os.getenv("PRICE_ID_BI_AGENT"),
        "crispwrite": os.getenv("PRICE_ID_CRISPWRITE"),
        "sop_agent": os.getenv("PRICE_ID_SOP_AGENT"),
        "resume_analyzer": os.getenv("PRICE_ID_RESUME_ANALYZER"),
        "recruitment_assistant": os.getenv("PRICE_ID_RECRUITMENT_ASSISTANT")
    }

    price_id = price_ids.get(product.lower())
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid product key")

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        line_items=[{
            'price': price_id,
            'quantity': 1
        }],
        mode='subscription',
        subscription_data={"trial_period_days": 7},
        success_url="http://localhost:8080/success",
        cancel_url="http://localhost:8080/cancel"
    )
    return {"checkout_url": session.url}

@stripe_router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'customer.subscription.updated':
        data = event['data']['object']
        email = data['customer_email']
        user = db.query(User).filter(User.email == email).first()
        if user:
            subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if not subscription:
                subscription = Subscription(user_id=user.id, status=data['status'])
                db.add(subscription)
            else:
                subscription.status = data['status']
            db.commit()

    return {"status": "ok"}