# app/models.py
from app import db
from sqlalchemy.dialects.postgresql import JSON
import datetime

#-----------------------------------------------------------------------------#
# models match to tables in postgres
#-----------------------------------------------------------------------------#

class Profile(db.Model):

    __tablename__ = 'profile'

    public_id = db.Column(db.String(36), primary_key=True)
    bespoke_avatar = db.Column(db.TEXT, nullable=True) 
    standard_avatar = db.Column(db.VARCHAR(length=50), 
                                nullable=True, 
                                default='blank_avatar_plain')
    about_me = db.Column(db.VARCHAR(length=500), nullable=True)
    modified = db.Column(db.TIMESTAMP(), nullable=True)
    created = db.Column(db.TIMESTAMP(), 
                        nullable=False, 
                        default=datetime.datetime.utcnow)

    def __repr__(self): # pragma: no cover
        return '<id Profile {}>'.format(self.public_id)

