"""
Store Routes
--------------
E-commerce store traffic endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_store_user, optional_store_user
from app.api.dependencies import get_aggregator
from app.models.schemas import StoreTrackRequest, StoreTrackResponse
from app.models.db_models import StoreOrder, StoreOrderItem
from app.services.store_service import StoreService
from app.services.metrics_aggregator import MetricsAggregator
from app.utils.helpers import timestamp_now
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/store", tags=["Store"])


@router.get("/products")
async def get_products(category: str = Query(default=None), db: Session = Depends(get_db), _user: dict = Depends(optional_store_user)):
    """Return product catalog, optionally filtered by category."""
    products = StoreService.get_products(db, category)
    return {"products": products, "total": len(products)}


@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db), _user: dict = Depends(optional_store_user)):
    """Get single product details."""
    product = StoreService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/categories")
async def get_categories(_user: dict = Depends(optional_store_user)):
    """Return available categories."""
    return {"categories": StoreService.get_categories()}


@router.post("/track", response_model=StoreTrackResponse)
async def track_interaction(
    request: StoreTrackRequest,
    db: Session = Depends(get_db),
    aggregator: MetricsAggregator = Depends(get_aggregator),
    _user: dict = Depends(require_store_user),
):
    """
    Track a store interaction and generate normal traffic.
    Every user action (pageview, click, add-to-cart, checkout)
    generates realistic normal traffic.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # Generate normal traffic via the existing simulator too
        generated, total = await aggregator.traffic_simulator.generate_normal_traffic()

        # Track in DB
        db_total = StoreService.track_interaction(
            db=db,
            session_id=session_id,
            page=request.page,
            action=request.action.value,
            product_id=request.product_id,
            search_query=request.search_query,
        )

        return StoreTrackResponse(
            success=True,
            message=f"Tracked: {request.action.value} on {request.page}",
            session_id=session_id,
            traffic_generated=total + db_total,
        )
    except Exception as exc:
        logger.exception("Store track error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


from pydantic import BaseModel
from typing import List

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreateSchema(BaseModel):
    items: List[OrderItemSchema]
    total_amount: float

@router.post("/orders")
async def create_order(
    payload: OrderCreateSchema,
    db: Session = Depends(get_db),
    user: dict = Depends(require_store_user)
):
    """Create a new order from cart checkout."""
    try:
        import uuid
        order_id_str = 'SZ-' + str(uuid.uuid4()).split('-')[0].upper()
        
        new_order = StoreOrder(
            order_id=order_id_str,
            user_id=user["user_id"],
            total_amount=payload.total_amount,
            status="Completed"
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        for item in payload.items:
            order_item = StoreOrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price
            )
            db.add(order_item)
            
        db.commit()
        
        return {"success": True, "order_id": order_id_str}
    except Exception as exc:
        logger.exception("Order creation error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
