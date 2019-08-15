from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime


__author__ = "Zhaozn"


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    _created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    _updated_at = db.Column(db.DateTime, default=0, onupdate=datetime.now, comment='更新时间')

    @hybrid_property
    def updated_at(self):
        if isinstance(self._updated_at,str):
            return self._updated_at
        return self._updated_at.strftime('%Y-%m-%d %H:%M:%S')

    @hybrid_property
    def created_at(self):
        return self._created_at.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it """
        instance = cls(**kwargs)
        instance.save()
        return instance

    def save(self, commit=True):
        """Save the record to database."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

