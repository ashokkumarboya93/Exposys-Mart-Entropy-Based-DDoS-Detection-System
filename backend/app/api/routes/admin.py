"""
Admin Routes
--------------
JWT-authenticated admin analytics dashboard endpoints.
Login authenticates against admin_users table with bcrypt.
"""

from __future__ import annotations

import io
import csv
import ipaddress
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token, require_admin,
)
from app.api.dependencies import get_aggregator
from app.models.db_models import (
    TrafficEvent, AttackEvent, AdminUser,
    SuspiciousIP, EntropyHistory,
)
from app.models.schemas import AdminLoginRequest, AdminLoginResponse, AdminAnalyticsResponse
from app.services.store_service import StoreService
from app.services.metrics_aggregator import MetricsAggregator
from app.utils.helpers import timestamp_now
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ANALYTICS_WINDOW_HOURS = 24
ACTIVE_SHOPPER_WINDOW_MINUTES = 30
ENTROPY_HISTORY_LIMIT = 60
RECENT_REQUESTS_LIMIT = 30


def _severity_from_status(status_value: str) -> str:
    if status_value == "DDOS_ATTACK":
        return "critical"
    if status_value == "NORMAL":
        return "safe"
    return "warning"


def _message_from_status(
    status_value: str,
    entropy_score: float | None,
    threshold: float | None,
) -> str:
    if status_value == "DDOS_ATTACK":
        return (
            f"🚨 DDoS attack detected. Entropy ({(entropy_score or 0):.4f}) "
            f"is below threshold ({(threshold or 0):.4f})."
        )
    if status_value == "NORMAL":
        return (
            f"Traffic appears normal. Entropy ({(entropy_score or 0):.4f}) "
            f"is above threshold ({(threshold or 0):.4f})."
        )
    return "Building baseline. More traffic samples are required for stable detection."


def _coerce_traffic_type(traffic_type: Optional[str]) -> Optional[str]:
    if traffic_type is None:
        return None

    value = traffic_type.strip().lower()
    if value in {"normal", "attack"}:
        return value

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="traffic_type must be one of: normal, attack",
    )


def _validate_ip_address(ip_address: str) -> str:
    try:
        return str(ipaddress.ip_address(ip_address))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid IP address format",
        ) from None


# ═══════════════════════════════════════════════════════════════════
#  AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Authenticate admin user against database with bcrypt."""
    admin = db.query(AdminUser).filter(AdminUser.username == request.username).first()

    if not admin or not verify_password(request.password, admin.hashed_password):
        logger.warning("Failed admin login attempt: %s", request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "sub": admin.username,
        "user_id": admin.id,
        "role": "admin",
    })

    logger.info("Admin login successful: %s", admin.username)
    return AdminLoginResponse(success=True, token=token, message="Login successful")


# ═══════════════════════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════════════════════

@router.get("/analytics", response_model=AdminAnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    aggregator: MetricsAggregator = Depends(get_aggregator),
    _admin: dict = Depends(require_admin),
):
    """Full analytics data for the admin dashboard."""
    try:
        # Refresh entropy/detection snapshot (stored into EntropyHistory).
        # Dashboard metrics below are DB-derived for consistency/reliability.
        engine_snapshot = None
        try:
            engine_snapshot = await aggregator.get_metrics()
        except Exception as exc:
            logger.warning("Metrics refresh degraded; using DB snapshot only: %s", exc)

        now = datetime.utcnow()
        window_start = now - timedelta(hours=ANALYTICS_WINDOW_HOURS)

        # Active shoppers (robust union logic in StoreService).
        active_shoppers = StoreService.get_active_sessions(
            db, minutes=ACTIVE_SHOPPER_WINDOW_MINUTES
        )

        # Entropy history and latest snapshot
        history = db.query(EntropyHistory).order_by(
            EntropyHistory.timestamp.desc()
        ).limit(ENTROPY_HISTORY_LIMIT).all()
        latest_entropy = history[0] if history else None

        entropy_history = [
            {
                "timestamp": h.timestamp.isoformat() if h.timestamp else "",
                "entropy": h.entropy_value,
                "normalized": h.normalized_entropy,
                "baseline": h.baseline_entropy,
                "threshold": h.threshold,
                "status": h.status,
            }
            for h in reversed(history)
        ]

        # Request totals + unique IPs (all-time, DB source of truth)
        totals_row = db.query(
            func.coalesce(func.sum(TrafficEvent.request_count), 0).label("total_requests"),
            func.count(func.distinct(TrafficEvent.ip_address)).label("unique_ips"),
        ).one()
        total_requests = int(totals_row.total_requests or 0)
        unique_ips = int(totals_row.unique_ips or 0)

        # Detection snapshot values
        if latest_entropy:
            status_value = latest_entropy.status or "INSUFFICIENT_DATA"
            entropy_score = float(latest_entropy.entropy_value or 0.0)
            normalized_entropy = float(latest_entropy.normalized_entropy or 0.0)
            baseline_entropy = latest_entropy.baseline_entropy
            threshold = latest_entropy.threshold
        elif engine_snapshot:
            status_value = engine_snapshot.status.value
            entropy_score = float(engine_snapshot.entropy)
            normalized_entropy = float(engine_snapshot.normalized_entropy)
            baseline_entropy = engine_snapshot.baseline_entropy
            threshold = engine_snapshot.threshold
        else:
            status_value = "INSUFFICIENT_DATA"
            entropy_score = 0.0
            normalized_entropy = 0.0
            baseline_entropy = None
            threshold = None

        severity_value = _severity_from_status(status_value)
        message = (
            engine_snapshot.message
            if engine_snapshot and engine_snapshot.status.value == status_value
            else _message_from_status(status_value, entropy_score, threshold)
        )

        # Recent sessions
        recent_sessions = StoreService.get_recent_sessions(
            db, active_minutes=ACTIVE_SHOPPER_WINDOW_MINUTES
        )

        # Recent request stream for dashboard "live packets" (real DB events only)
        recent_events = db.query(TrafficEvent).order_by(
            TrafficEvent.timestamp.desc()
        ).limit(RECENT_REQUESTS_LIMIT).all()
        recent_requests = [
            {
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "ip": e.ip_address,
                "method": e.method,
                "endpoint": e.endpoint,
                "traffic_type": e.traffic_type,
                "request_count": int(e.request_count or 0),
                "session_id": e.session_id or "",
            }
            for e in recent_events
        ]

        # Attack events
        attacks = db.query(AttackEvent).order_by(
            AttackEvent.timestamp.desc()
        ).limit(20).all()

        attack_events = [
            {
                "attack_id": a.attack_id[:12],
                "timestamp": a.timestamp.isoformat() if a.timestamp else "",
                "preset_type": a.preset_type,
                "num_ips": a.num_ips,
                "total_requests": a.total_requests,
                "status": a.status,
                "duration_ms": a.duration_ms,
            }
            for a in attacks
        ]

        # Suspicious IPs
        sus_ips = db.query(SuspiciousIP).order_by(
            SuspiciousIP.total_requests.desc()
        ).limit(20).all()

        suspicious = [
            {
                "ip": s.ip_address,
                "requests": s.total_requests,
                "risk_score": s.risk_score,
                "first_seen": s.first_seen.isoformat() if s.first_seen else "",
                "last_seen": s.last_seen.isoformat() if s.last_seen else "",
                "is_blocked": s.is_blocked,
            }
            for s in sus_ips
        ]

        # Traffic breakdown (normal vs attack)
        traffic_events = db.query(
            TrafficEvent.traffic_type,
            func.coalesce(func.sum(TrafficEvent.request_count), 0).label("total"),
        ).filter(
            TrafficEvent.timestamp >= window_start
        ).group_by(
            TrafficEvent.traffic_type
        ).all()

        normal_count = 0
        attack_count = 0
        for t in traffic_events:
            if t.traffic_type == "normal":
                normal_count = int(t.total or 0)
            elif t.traffic_type == "attack":
                attack_count = int(t.total or 0)

        total_all = normal_count + attack_count
        attack_confidence = round(
            (attack_count / total_all * 100) if total_all > 0 else 0, 1
        )

        # Top attacked endpoints
        endpoint_total = func.coalesce(
            func.sum(TrafficEvent.request_count), 0
        ).label("total_requests")
        top_endpoints = db.query(
            TrafficEvent.endpoint,
            endpoint_total,
        ).filter(
            TrafficEvent.traffic_type == "attack",
            TrafficEvent.timestamp >= window_start,
        ).group_by(
            TrafficEvent.endpoint
        ).order_by(
            endpoint_total.desc()
        ).limit(10).all()

        top_attacked_endpoints = [
            {"endpoint": ep.endpoint, "total_requests": int(ep.total_requests or 0)}
            for ep in top_endpoints
        ]

        # IP traffic distribution (same window as normal_vs_attack)
        ip_total = func.coalesce(
            func.sum(TrafficEvent.request_count), 0
        ).label("requests")
        top_ips = db.query(
            TrafficEvent.ip_address,
            ip_total,
        ).filter(
            TrafficEvent.timestamp >= window_start
        ).group_by(
            TrafficEvent.ip_address
        ).order_by(
            ip_total.desc()
        ).limit(20).all()

        window_total_requests = normal_count + attack_count
        traffic_distribution = [
            {
                "ip": row.ip_address,
                "requests": int(row.requests or 0),
                "percentage": round(
                    ((row.requests or 0) / window_total_requests) * 100, 2
                ) if window_total_requests > 0 else 0,
            }
            for row in top_ips
        ]

        return AdminAnalyticsResponse(
            total_requests=total_requests,
            active_shoppers=active_shoppers,
            unique_ips=unique_ips,
            entropy_score=entropy_score,
            normalized_entropy=normalized_entropy,
            attack_confidence=attack_confidence,
            status=status_value,
            severity=severity_value,
            baseline_entropy=baseline_entropy,
            threshold=threshold,
            message=message,
            suspicious_ips=suspicious,
            traffic_distribution=traffic_distribution,
            entropy_history=entropy_history,
            recent_sessions=recent_sessions,
            recent_requests=recent_requests,
            attack_events=attack_events,
            top_attacked_endpoints=top_attacked_endpoints,
            normal_vs_attack={"normal": normal_count, "attack": attack_count},
            timestamp=timestamp_now(),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Analytics error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Unable to compute analytics at this time",
        )


# ═══════════════════════════════════════════════════════════════════
#  ENTROPY HISTORY
# ═══════════════════════════════════════════════════════════════════

@router.get("/entropy-history")
async def get_entropy_history(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    _admin: dict = Depends(require_admin),
):
    """Get entropy history for trend charts."""
    history = db.query(EntropyHistory).order_by(
        EntropyHistory.timestamp.desc()
    ).limit(limit).all()

    return {
        "success": True,
        "data": {
            "history": [
                {
                    "timestamp": h.timestamp.isoformat() if h.timestamp else "",
                    "entropy": h.entropy_value,
                    "normalized": h.normalized_entropy,
                    "baseline": h.baseline_entropy,
                    "threshold": h.threshold,
                    "status": h.status,
                    "total_requests": h.total_requests,
                    "unique_ips": h.unique_ips,
                }
                for h in reversed(history)
            ]
        },
    }


# ═══════════════════════════════════════════════════════════════════
#  REQUEST LOGS
# ═══════════════════════════════════════════════════════════════════

@router.get("/logs")
async def get_logs(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    traffic_type: Optional[str] = Query(default=None),
    _admin: dict = Depends(require_admin),
):
    """Get paginated request logs."""
    traffic_type_value = _coerce_traffic_type(traffic_type)
    query = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc())
    if traffic_type_value:
        query = query.filter(TrafficEvent.traffic_type == traffic_type_value)

    events = query.limit(limit).all()

    return {
        "success": True,
        "data": {
            "logs": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                    "ip": e.ip_address,
                    "endpoint": e.endpoint,
                    "method": e.method,
                    "traffic_type": e.traffic_type,
                    "action": e.action,
                    "request_count": e.request_count,
                    "session_id": (e.session_id or "")[:12],
                }
                for e in events
            ],
            "total": len(events),
        },
    }


# ═══════════════════════════════════════════════════════════════════
#  IP MANAGEMENT (Block / Unblock)
# ═══════════════════════════════════════════════════════════════════

@router.post("/ip/{ip_address}/block")
async def block_ip(
    ip_address: str,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Block a suspicious IP address."""
    validated_ip = _validate_ip_address(ip_address)
    sus_ip = db.query(SuspiciousIP).filter(SuspiciousIP.ip_address == validated_ip).first()
    if not sus_ip:
        raise HTTPException(status_code=404, detail="IP not found in suspicious list")

    sus_ip.is_blocked = True
    db.commit()
    logger.warning("IP blocked by admin: %s", validated_ip)

    return {"success": True, "message": f"IP {validated_ip} has been blocked"}


@router.post("/ip/{ip_address}/unblock")
async def unblock_ip(
    ip_address: str,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Unblock a suspicious IP address (false-positive handling)."""
    validated_ip = _validate_ip_address(ip_address)
    sus_ip = db.query(SuspiciousIP).filter(SuspiciousIP.ip_address == validated_ip).first()
    if not sus_ip:
        raise HTTPException(status_code=404, detail="IP not found")

    sus_ip.is_blocked = False
    sus_ip.risk_score = max(0, sus_ip.risk_score - 30)
    db.commit()
    logger.info("IP unblocked by admin: %s", validated_ip)

    return {"success": True, "message": f"IP {validated_ip} has been unblocked"}


# ═══════════════════════════════════════════════════════════════════
#  REPORTS
# ═══════════════════════════════════════════════════════════════════

@router.get("/report")
async def download_report(
    db: Session = Depends(get_db),
    aggregator: MetricsAggregator = Depends(get_aggregator),
    _admin: dict = Depends(require_admin),
):
    """Generate a downloadable attack report."""
    metrics = await aggregator.get_metrics()

    attacks = db.query(AttackEvent).order_by(
        AttackEvent.timestamp.desc()
    ).limit(50).all()

    sus_ips = db.query(SuspiciousIP).order_by(
        SuspiciousIP.total_requests.desc()
    ).limit(30).all()

    return {
        "success": True,
        "data": {
            "report_id": timestamp_now().replace(":", "-").replace(" ", "_"),
            "generated_at": timestamp_now(),
            "summary": {
                "total_requests": metrics.total_requests,
                "unique_ips": metrics.unique_ips,
                "current_entropy": metrics.entropy,
                "detection_status": metrics.status.value,
                "severity": metrics.severity.value,
            },
            "attack_history": [
                {
                    "attack_id": a.attack_id,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else "",
                    "type": a.preset_type,
                    "ips": a.num_ips,
                    "requests": a.total_requests,
                    "status": a.status,
                }
                for a in attacks
            ],
            "suspicious_ips": [
                {
                    "ip": s.ip_address,
                    "requests": s.total_requests,
                    "risk_score": s.risk_score,
                    "blocked": s.is_blocked,
                }
                for s in sus_ips
            ],
        },
    }


@router.get("/report/csv")
async def download_csv_report(
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Download traffic data as CSV."""
    logs = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).limit(1000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "IP Address", "Endpoint", "Method", "Action", "Traffic Type", "Requests"])

    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.isoformat() if log.timestamp else "",
            log.ip_address,
            log.endpoint,
            log.method,
            log.action,
            log.traffic_type,
            log.request_count,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=traffic_report_{timestamp_now().replace(':', '-')}.csv"}
    )


@router.get("/report/pdf")
async def download_pdf_report(
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Download security report as PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Exposys Mart - Security Analytics Report")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated: {timestamp_now()}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Recent Suspicious IPs (Top 10):")

    sus_ips = db.query(SuspiciousIP).order_by(desc(SuspiciousIP.total_requests)).limit(10).all()
    y = height - 130
    p.setFont("Helvetica", 10)
    for ip in sus_ips:
        blocked = "Yes" if ip.is_blocked else "No"
        p.drawString(50, y, f"IP: {ip.ip_address} | Requests: {ip.total_requests} | Blocked: {blocked} | Score: {ip.risk_score}")
        y -= 20

    p.setFont("Helvetica-Bold", 12)
    y -= 20
    p.drawString(50, y, "Recent Attacks (Top 10):")

    attacks = db.query(AttackEvent).order_by(desc(AttackEvent.timestamp)).limit(10).all()
    y -= 20
    p.setFont("Helvetica", 10)
    for att in attacks:
        p.drawString(50, y, f"ID: {att.attack_id[:8]} | Type: {att.preset_type} | IPs: {att.num_ips} | Reqs: {att.total_requests}")
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=security_report_{timestamp_now().replace(':', '-')}.pdf"}
    )


# ═══════════════════════════════════════════════════════════════════
#  STORE ADMIN (Products & Users)
# ═══════════════════════════════════════════════════════════════════

from pydantic import BaseModel
from app.models.db_models import StoreProduct, User, StoreOrder

class ProductCreateUpdate(BaseModel):
    name: str
    brand: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    category: str
    image: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = 4.0
    reviews: Optional[int] = 0
    badge: Optional[str] = None

@router.get("/products")
async def admin_get_products(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    products = db.query(StoreProduct).all()
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "price": float(p.price) if p.price else 0,
                "original_price": float(p.original_price) if p.original_price else 0,
                "category": p.category,
                "image": p.image,
                "description": p.description,
            }
            for p in products
        ]
    }

@router.post("/products")
async def admin_create_product(payload: ProductCreateUpdate, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    new_product = StoreProduct(
        name=payload.name,
        brand=payload.brand,
        price=payload.price,
        original_price=payload.original_price,
        category=payload.category,
        image=payload.image,
        description=payload.description,
        rating=payload.rating,
        reviews=payload.reviews,
        badge=payload.badge
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"success": True, "product_id": new_product.id}

@router.put("/products/{product_id}")
async def admin_update_product(product_id: int, payload: ProductCreateUpdate, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    product = db.query(StoreProduct).filter(StoreProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = payload.name
    product.brand = payload.brand
    product.price = payload.price
    product.original_price = payload.original_price
    product.category = payload.category
    product.image = payload.image
    product.description = payload.description
    
    db.commit()
    return {"success": True}

@router.delete("/products/{product_id}")
async def admin_delete_product(product_id: int, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    product = db.query(StoreProduct).filter(StoreProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"success": True}

@router.get("/users")
async def admin_get_users(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else ""
            }
            for u in users
        ]
    }

@router.get("/orders")
async def admin_get_orders(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    orders = db.query(StoreOrder).order_by(StoreOrder.created_at.desc()).all()
    # Join with User to get username
    result = []
    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        result.append({
            "id": o.id,
            "order_id": o.order_id,
            "username": user.username if user else "Unknown",
            "total_amount": float(o.total_amount),
            "status": o.status,
            "created_at": o.created_at.isoformat() if o.created_at else ""
        })
    return {"orders": result}

@router.put("/orders/{order_id}/status")
async def admin_update_order_status(order_id: int, status_update: dict, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    order = db.query(StoreOrder).filter(StoreOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_update.get("status", order.status)
    db.commit()
    return {"success": True, "status": order.status}

@router.get("/store-report/csv")
async def download_store_csv(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    """Download store orders as CSV."""
    orders = db.query(StoreOrder).order_by(StoreOrder.created_at.desc()).limit(1000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "Customer Username", "Total Amount", "Status", "Date"])

    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        writer.writerow([
            o.order_id,
            user.username if user else "Unknown",
            f"{o.total_amount:.2f}",
            o.status,
            o.created_at.isoformat() if o.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=store_orders_{timestamp_now().replace(':', '-')}.csv"}
    )

@router.get("/store-report/pdf")
async def download_store_pdf(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    """Download store report as PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Exposys Mart - Store Analytics Report")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated: {timestamp_now()}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Recent Orders (Top 15):")

    orders = db.query(StoreOrder).order_by(desc(StoreOrder.created_at)).limit(15).all()
    y = height - 130
    p.setFont("Helvetica", 10)
    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        username = user.username if user else "Unknown"
        date_str = o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "N/A"
        p.drawString(50, y, f"ID: {o.order_id} | User: {username} | Amount: ₹{o.total_amount:.2f} | Status: {o.status} | Date: {date_str}")
        y -= 20

    p.setFont("Helvetica-Bold", 12)
    y -= 20
    p.drawString(50, y, "Product Inventory Summary:")
    y -= 20
    p.setFont("Helvetica", 10)
    
    total_products = db.query(func.count(StoreProduct.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    total_revenue = db.query(func.sum(StoreOrder.total_amount)).filter(StoreOrder.status == 'Completed').scalar() or 0.0

    p.drawString(50, y, f"Total Products: {total_products}")
    y -= 20
    p.drawString(50, y, f"Registered Store Users: {total_users}")
    y -= 20
    p.drawString(50, y, f"Total Revenue (Completed Orders): ₹{total_revenue:.2f}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=store_report_{timestamp_now().replace(':', '-')}.pdf"}
    )
