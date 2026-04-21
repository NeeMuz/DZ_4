from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Comment, Post
from schemas import CommentCreate, CommentRead
from database import get_db
from security import get_current_user

router = APIRouter(prefix="/comments")


@router.get("/post/{post_id}", response_model=list[CommentRead])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id == post_id).all()


@router.post("/post/{post_id}", response_model=CommentRead)
def create_comment(post_id: int, data: CommentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not db.get(Post, post_id):
        raise HTTPException(404, "Post not found")

    comment = Comment(text=data.text, author_id=user.id, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(comment_id: int, data: CommentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")

    if comment.author_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")

    comment.text = data.text
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")

    if comment.author_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}
