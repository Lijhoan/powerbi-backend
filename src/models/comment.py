from src.models.user import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    comment_likes = db.relationship('CommentLike', backref='comment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, current_user_id=None):
        """Convert comment to dictionary"""
        user_liked = False
        if current_user_id:
            user_liked = any(like.user_id == current_user_id for like in self.comment_likes)
        
        return {
            'id': self.id,
            'usuario': self.user.username,
            'contenido': self.content,
            'fecha': self.created_at.isoformat() if self.created_at else None,
            'esAdmin': self.user.is_admin,
            'likes': self.likes,
            'userLiked': user_liked
        }
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.user.username}>'

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_like'),)
    
    def __repr__(self):
        return f'<CommentLike {self.user_id} -> {self.comment_id}>'

