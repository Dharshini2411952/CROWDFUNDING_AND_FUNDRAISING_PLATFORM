from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate

router = APIRouter(prefix="/comments", tags=["Comments"])


def _build_comment_read(comment, user_name):
    return CommentRead(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        campaign_id=comment.campaign_id,
        comment_text=comment.comment_text,
        created_at=comment.created_at.isoformat() if comment.created_at else None,
        updated_at=comment.updated_at.isoformat() if comment.updated_at else None,
        user_name=user_name,
    )


@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == payload.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    comment = Comment(
        user_id=current_user.user_id,
        campaign_id=payload.campaign_id,
        comment_text=payload.comment_text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _build_comment_read(comment, current_user.name)


@router.get("/{campaign_id}", response_model=list[CommentRead])
def get_comments_for_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    items = (
        db.query(Comment, User.name.label("user_name"))
        .join(User, User.user_id == Comment.user_id)
        .filter(Comment.campaign_id == campaign_id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    return [_build_comment_read(item.Comment, item.user_name) for item in items]


@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed to edit this comment")

    comment.comment_text = payload.comment_text
    db.commit()
    db.refresh(comment)

    user = db.query(User).filter(User.user_id == comment.user_id).first()
    return _build_comment_read(comment, user.name if user else "Unknown")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    db.delete(comment)
    db.commit()
    return None