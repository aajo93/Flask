from app import db
from app import login
import hashlib
import sqlalchemy
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

def __str__(self):
    return f"Message {self.id} was {self.message} on {self.timestamp}"


class AppUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True,nullable=False)
    email =  db.Column(db.String(120),index=True,unique=True,nullable=False)
    password_hash = db.Column(db.String(256),nullable=False)
    short_urls = db.relationship('ShortURL',backref='appuser')

    #posts: db.WriteOnlyMapped['Post'] = db.relationship(back_populates='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_all_short_urls(self):
        return sqlalchemy.select(ShortURL).join(AppUser, ShortURL.user_id == AppUser.id).where(AppUser.username == self.username)
    
@login.user_loader
def load_user(id):
    return db.session.get(AppUser, int(id))


class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    short_url = db.Column(db.String(64),unique=True,nullable=False)
    actual_url = db.Column(db.String(256),unique=False,nullable=False)
    #user_id = db.Column(db.ForeignKey(AppUser.id),index=True)
    user_id = db.Column(db.Integer, db.ForeignKey(AppUser.id), nullable=False)

    def generate_short_url(self):
        #get id
        counter = self.get_last_index()
        short_key = hashlib.md5(str(counter).encode()).hexdigest()[:6]
        stored_hashes = self.get_stored_hashes()
        if stored_hashes:
            while short_key in stored_hashes:
                counter += 1
                short_key = hashlib.md5(str(counter).encode()).hexdigest()[:6]
        self.short_url = short_key
        return self.short_url
    
    def get_stored_hashes(self):
        query = sqlalchemy.select(ShortURL.short_url)
        return db.session.scalar(query)
    
    def get_last_index(self):
        query = sqlalchemy.select(func.max(ShortURL.id))
        last_id = db.session.scalar(query)
        return last_id if last_id is not None else 0
