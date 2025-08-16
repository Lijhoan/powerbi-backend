from src.models.user import db
from datetime import datetime

class Reaction(db.Model):
    __tablename__ = 'reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate reactions of same type
    __table_args__ = (db.UniqueConstraint('user_id', 'report_id', 'reaction_type', name='unique_user_report_reaction'),)
    
    def to_dict(self):
        """Convert reaction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_id': self.report_id,
            'tipo': self.reaction_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_reaction_stats(report_id):
        """Get reaction statistics for a report"""
        from sqlalchemy import func
        
        stats = db.session.query(
            Reaction.reaction_type,
            func.count(Reaction.id).label('count')
        ).filter(
            Reaction.report_id == report_id
        ).group_by(
            Reaction.reaction_type
        ).all()
        
        return [{'tipo': stat.reaction_type, 'count': stat.count} for stat in stats]
    
    def __repr__(self):
        return f'<Reaction {self.reaction_type} by {self.user_id} on {self.report_id}>'

