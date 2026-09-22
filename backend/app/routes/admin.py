from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.models.transaction import Transaction
from app.models.user import User
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead

router = APIRouter(prefix="/admin", tags=["Admin"])


def _verify_admin(current_user: User):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def _log_audit_action(db: Session, admin_id: int, action: str, entity_type: str, entity_id: int = None, details: str = None):
    audit_log = AuditLog(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(audit_log)
    db.commit()


@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    users = db.query(User).all()
    return [{
        "user_id": u.user_id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "phone": u.phone,
        "is_active": getattr(u, "is_active", True),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]


@router.patch("/users/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user.is_active = True
    _log_audit_action(db, current_user.user_id, "USER_ACTIVATED", "USER", target_user.user_id, f"Activated user '{target_user.email}'")
    db.commit()

    return {
        "success": True,
        "message": f"User {target_user.email} activated successfully",
        "user_id": target_user.user_id,
        "is_active": True
    }


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot deactivate their own active account"
        )

    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user.is_active = False
    _log_audit_action(db, current_user.user_id, "USER_DEACTIVATED", "USER", target_user.user_id, f"Deactivated user '{target_user.email}'")
    db.commit()

    return {
        "success": True,
        "message": f"User {target_user.email} deactivated successfully",
        "user_id": target_user.user_id,
        "is_active": False
    }


@router.get("/campaigns")
def get_all_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.patch("/campaigns/{campaign_id}/approve")
def approve_campaign(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)

    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = "ACTIVE"

    notif = Notification(
        user_id=campaign.creator_id,
        title="Campaign Approved",
        message=f"Your campaign '{campaign.title}' has been approved and is now ACTIVE!",
        notification_type="CAMPAIGN_APPROVED",
        is_read=False
    )
    db.add(notif)
    _log_audit_action(db, current_user.user_id, "CAMPAIGN_APPROVED", "CAMPAIGN", campaign.campaign_id, f"Approved campaign '{campaign.title}'")
    db.commit()
    return {"success": True, "message": "Campaign approved", "data": {"campaign_id": campaign.campaign_id, "status": campaign.status}}


@router.patch("/campaigns/{campaign_id}/reject")
def reject_campaign(campaign_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)

    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = "REJECTED"

    notif = Notification(
        user_id=campaign.creator_id,
        title="Campaign Rejected",
        message=f"Your campaign '{campaign.title}' was rejected by the admin.",
        notification_type="CAMPAIGN_REJECTED",
        is_read=False
    )
    db.add(notif)
    _log_audit_action(db, current_user.user_id, "CAMPAIGN_REJECTED", "CAMPAIGN", campaign.campaign_id, f"Rejected campaign '{campaign.title}'")
    db.commit()
    return {"success": True, "message": "Campaign rejected", "data": {"campaign_id": campaign.campaign_id, "status": campaign.status}}


@router.get("/donations")
def get_donations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    return db.query(Donation).order_by(Donation.created_at.desc()).all()


@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    return db.query(Transaction).order_by(Transaction.created_at.desc()).all()


@router.get("/audit-logs", response_model=list[AuditLogRead])
def get_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)
    items = (
        db.query(AuditLog, User.name.label("admin_name"))
        .join(User, User.user_id == AuditLog.admin_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    result = []
    for log, admin_name in items:
        result.append(
            AuditLogRead(
                audit_id=log.audit_id,
                admin_id=log.admin_id,
                admin_name=admin_name,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                details=log.details,
                created_at=log.created_at.isoformat() if log.created_at else None,
            )
        )

    return result


@router.get("/reports")
def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _verify_admin(current_user)

    total_users = db.query(User).count()
    total_donors = db.query(User).filter(User.role == "DONOR").count()
    total_campaigners = db.query(User).filter(User.role == "CAMPAIGNER").count()

    total_campaigns = db.query(Campaign).count()
    pending_campaigns = db.query(Campaign).filter(Campaign.status == "PENDING").count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "ACTIVE").count()
    completed_campaigns = db.query(Campaign).filter(Campaign.status == "COMPLETED").count()
    rejected_campaigns = db.query(Campaign).filter(Campaign.status == "REJECTED").count()

    total_donations = db.query(Donation).count()
    total_amount = sum((d.amount or 0) for d in db.query(Donation).all())

    successful_transactions = db.query(Transaction).filter(Transaction.status == "SUCCESS").count()
    failed_transactions = db.query(Transaction).filter(Transaction.status == "FAILED").count()

    # Category breakdown
    category_counts = {}
    categories = db.query(Campaign.category, func.count(Campaign.campaign_id)).group_by(Campaign.category).all()
    for cat, count in categories:
        if cat:
            category_counts[cat] = count

    return {
        "success": True,
        "data": {
            "total_users": total_users,
            "total_donors": total_donors,
            "total_campaigners": total_campaigners,
            "total_campaigns": total_campaigns,
            "pending_campaigns": pending_campaigns,
            "active_campaigns": active_campaigns,
            "completed_campaigns": completed_campaigns,
            "rejected_campaigns": rejected_campaigns,
            "total_donations": total_donations,
            "total_amount_raised": total_amount,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "campaigns_by_category": category_counts,
        },
    }
