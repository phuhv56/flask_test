from marshmallow import fields, Schema
from . import db, bcrypt
import datetime


class UserModel(db.Model):
    """
    User Model
    """

    __tablename__ = 'user'


    id = db.Column('id', db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String(200))
    tel_no = db.Column(db.String(20))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, email, full_name, job_id):
        self.email = email
        self.full_name = full_name
        self.job_id = job_id
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
