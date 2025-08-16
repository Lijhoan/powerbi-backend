from src.models.user import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    powerbi_report_id = db.Column(db.String(100), unique=True, nullable=False)
    powerbi_workspace_id = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='report', lazy=True)
    reactions = db.relationship('Reaction', backref='report', lazy=True)
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'powerbi_report_id': self.powerbi_report_id,
            'powerbi_workspace_id': self.powerbi_workspace_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Report {self.name}>'

