from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Post
from schemas import PostCreate, PostRead
from database import get_db
from security import get_current_user

router = APIRouter(prefix="/posts")


@router.get("/", response_model=list[PostRead])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return post


@router.post("/", response_model=PostRead)
def create_post(data: PostCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = Post(title=data.title, content=data.content, author_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, data: PostCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    if post.author_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")

    post.title = data.title
    post.content = data.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    if post.author_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
