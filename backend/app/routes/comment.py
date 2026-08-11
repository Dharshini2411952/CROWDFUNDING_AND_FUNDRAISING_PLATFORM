from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import Comment
from app.schemas import CommentCreate, CommentResponse

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post("/", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    new_comment = Comment(
        campaign_id=comment.campaign_id,
        user_id=comment.user_id,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/", response_model=list[CommentResponse])
def get_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(
        Comment.comment_id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return comment