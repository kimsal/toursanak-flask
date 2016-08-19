#!/usr/bin/env python
from database import *
from sqlalchemy.orm import relationship
from slugify import slugify
from wtforms.widgets import * #TextArea
from wtforms import * #TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField,validators, ValidationError
import wtforms.widgets.core
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
class UserMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100),nullable=True,unique=True)
    password = db.Column(db.String(600))
    password2=db.Column(db.String(200))
    created_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    post=db.relationship('Post', backref="user_member", lazy='dynamic')
    event=db.relationship('Event', backref="user_member", lazy='dynamic')
    def verify_password(self, password):
        #return custom_app_context.encrypt(password) == self.password
        return custom_app_context.verify(password, self.password)
    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.password2 = password
    def add(user):
        db.session.add(user)
        return db.session.commit()
    def update(self):
        return session_commit()
    def delete(user):
        db.session.delete(user)
        return session_commit()
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = UserMember.query.get(data['id'])
        return user
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    slug= db.Column(db.String(50),nullable=True)
    feature_image=db.Column(db.Text)
    possition = db.Column(db.String(300),nullable=True)
    detail=db.Column(db.String(1000),nullable=True)
    created_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __init__(self, name, possition,detail,feature_image):
        self.name = name
        self.slug=slugify(name)
        self.feature_image = feature_image
        self.possition = possition
        self.detail = detail
    def add(member):
        db.session.add(member)
        return db.session.commit()
    def update(self):
        return session_commit()
    def delete(member):
        db.session.delete(member)
        return session_commit()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=  db.Column(db.String(100),nullable=True,unique=True)
    slug= db.Column(db.String(100),nullable=True)
    posts=db.relationship('Post', backref="category", lazy='dynamic')
    is_menu=db.Column(db.Integer,nullable=True,default=0)
    def get_absolute_url(self):
        return ('Category', (), {'slug': self.slug,'id': self.id,})
    def __str__(self):
        return self.name
    def to_Json(self):
        return dict(id=self.id,
            name=self.name,
            slug=self.slug
            )
    def __init__(self, name):
        self.slug=slugify(name)
        self.name =name
    def add(category):
        db.session.add(category)
        return db.session.commit()
    def delete(category):
        db.session.delete(category)
        return db.session.commit()
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(255),nullable=True,unique=True)
    slug= db.Column(db.String(255),nullable=True)
    description = db.Column(db.Text,nullable=True)
    published_at= db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    is_menu=db.Column(db.Integer,nullable=True,default=0)
    def get_absolute_url(self):
        return ('Page', (), {'slug': self.slug,'id': self.id,})
    def __str__(self):
        return self.title
    def to_Json(self):
        return dict(id=self.id,
            title=self.title,
            slug=self.slug,
            description=self.description,
            published_at="{}".format(self.published_at)
            )
    def __init__(self, title,description):
        self.title = title
        self.slug =slugify(title)
        self.description=description
    def add(page):
        db.session.add(page)
        return db.session.commit()
    def delete(page):
        db.session.delete(page)
        return db.session.commit()
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255),nullable=True,unique=True)
    description = db.Column(db.Text,nullable=True)
    short_description = db.Column(db.Text,nullable=True)
    feature_image=db.Column(db.Text,nullable=True)
    slug=db.Column(db.String(255),nullable=True,unique=True)
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=True)
    price=db.Column(db.Integer,nullable=True)
    map=db.Column(db.Text,nullable=True)
    images = db.Column(db.Text,nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'))
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    views = db.Column(db.Integer, nullable=True)
    bookings=db.relationship('Booking', backref="post", lazy='dynamic')
    # images=db.relationship('Image', backref="post", lazy='dynamic')
    def to_Json(self):
        return dict(id=self.id,
            title=self.title,
            description=self.description,
            feature_image=self.feature_image,
            slug=self.slug,
            category_id=self.category_id,
            published_at="{}".format(self.published_at),
            view=self.view,
            images=self.images,
            price=self.price,
            map=self.map,
            short_description=self.short_description
            )
    def __init__(self, title, description, category_id, feature_image, user_id,views=0,images='',price=0,map='',short_description=''):
        self.title = title
        self.slug =slugify(title)
        self.description = description
        self.feature_image = feature_image
        self.category_id = category_id
        self.user_id = user_id
        self.images=images
        self.views=views
        self.price=price
        self.map=map
        self.short_description=short_description
    def add(post):
        db.session.add(post)
        return db.session.commit()
    def update(self):
        return session_commit()
    def delete(post):
        db.session.delete(post)
        return db.session.commit()
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255),nullable=True,unique=True)
    address = db.Column(db.String(300),nullable=True)
    hour = db.Column(db.String(300),nullable=True)
    contact = db.Column(db.String(300),nullable=True)
    feature_image1=db.Column(db.Text,nullable=True)
    feature_image2=db.Column(db.Text,nullable=True)
    slug=db.Column(db.String(255),nullable=True,unique=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'))
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    # bookings=db.relationship('Booking', backref="location", lazy='dynamic')
    def to_Json(self):
        return dict(id=self.id,
            title=self.title,
            address=self.address,
            hour=self.hour,
            slug=self.slug,
            contact=self.contact,
            feature_image1=self.feature_image1,
            feature_image2=self.feature_image2,
            user_id=self.user_id,
            published_at="{}".format(self.published_at)
            )
    def __init__(self, title, address, hour,contact, feature_image1,feature_image2, user_id):
        self.title = title
        self.slug =slugify(title)
        self.address = address
        self.hour=hour
        self.contact=contact
        self.feature_image1 = feature_image1
        self.feature_image2 = feature_image2
        self.user_id = user_id
    def add(location):
        db.session.add(location)
        return db.session.commit()
    def update(self):
        return session_commit()
    def delete(location):
        db.session.delete(location)
        return db.session.commit()

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255),unique=True)
    name  = db.Column(db.String(255),nullable=True)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.name
    def update(self):
        return session_commit()
    def to_Json(self):
        return dict(id=self.id,
            email=self.email,
            name=self.name
            )
    def __init__(self, email,name):
        self.email = email
        self.name =name
    def add(email):
        db.session.add(email)
        return db.session.commit()
    def delete(email):
        db.session.delete(email)
        return db.session.commit()
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name
            )
    def __init__(self,name):
        self.name =name
    def add(group):
        db.session.add(group)
        return db.session.commit()
    def delete(group):
        db.session.delete(group)
        return db.session.commit()
class Emailgroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id  = db.Column(db.Integer)
    group_id  = db.Column(db.Integer)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.email_id
    def to_Json(self):
        return dict(id=self.id,
            email_id=self.email_id,
            group_id=self.group_id
            )
    def __init__(self,email_id,group_id):
        self.email_id =email_id,
        self.group_id =group_id
    def add(emailgroup):
        db.session.add(emailgroup)
        return db.session.commit()
    def delete(emailgroup):
        db.session.delete(emailgroup)
        return db.session.commit()
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname  = db.Column(db.String(255))
    lastname  = db.Column(db.String(255))
    email  = db.Column(db.String(255),unique=True)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email
            )
    def __init__(self,firstname,lastname,email):
        self.firstname =firstname,
        self.lastname =lastname,
        self.email =email
    def add(contact):
        db.session.add(contact)
        return db.session.commit()
    def delete(contact):
        db.session.delete(contact)
        return db.session.commit()
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    email  = db.Column(db.String(255))
    phone  = db.Column(db.String(255),nullable=True)
    amount = db.Column(db.Integer,nullable=True)
    post_id= db.Column(db.Integer,db.ForeignKey('post.id'))
    detail = db.Column(db.Text,nullable=True)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name,
            email=self.email,
            phone=self.phone,
            post_id=self.post_id,
            amount=self.amount,
            detail=self.detail
            )
    def __init__(self,name,email,phone,post_id,amount=1,detail=''):
        self.name =name,
        self.email =email,
        self.phone =phone,
        self.amount=amount,
        self.post_id=post_id,
        self.detail=detail
    def add(booking):
        db.session.add(booking)
        return db.session.commit()
    def delete(booking):
        db.session.delete(booking)
        return db.session.commit()
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title  = db.Column(db.String(500))
    slug=db.Column(db.String(500),unique=True)
    description  = db.Column(db.Text,nullable=True)
    date  = db.Column(db.DateTime,nullable=True)
    feature_image=db.Column(db.Text,nullable=True)
    views = db.Column(db.Integer, nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_member.id'))
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.title
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            title=self.title,
            slug=self.slug,
            description=self.description,
            date=self.date,
            views=self.views,
            user_id=self.user_id,
            feature_image=self.feature_image
            )
    def __init__(self,title,description,date,feature_image,user_id,views=0):
        self.title = title,
        self.slug = slugify(title),
        self.description = description,
        self.date = date,
        self.views=views,
        self.user_id=user_id,
        self.feature_image=feature_image
    def add(event):
        db.session.add(event)
        return db.session.commit()
    def delete(event):
        db.session.delete(event)
        return db.session.commit()
class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    slug  = db.Column(db.String(255))
    url  = db.Column(db.String(255),nullable=True)
    feature_image=db.Column(db.Text,nullable=True)
    published_at=db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name,
            slug=self.slug,
            url=self.url,
            feature_image=self.feature_image
            )
    def __init__(self,name,url,feature_image):
        self.name =name,
        self.slug = slugify(name),
        self.url =url,
        self.feature_image =feature_image
    def add(partner):
        db.session.add(partner)
        return db.session.commit()
    def delete(partner):
        db.session.delete(partner)
        return db.session.commit()
class EmailList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(255))
    email  = db.Column(db.String(255))
    def __str__(self):
        return self.name
    # def update(self):
    #     return session_commit()    
    def to_Json(self):
        return dict(id=self.id,
            name=self.name,
            email=self.email
            )
    def __init__(self,name,email):
        self.name =name,
        self.email =email
    def add(messagelist):
        db.session.add(messagelist)
        return db.session.commit()
    def delete(messagelist):
        db.session.delete(messagelist)
        return db.session.commit()
if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.config['DEBUG'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    manager.run()
    app.run()
# @manager.command
# def init_db():
#     db.drop_all()
#     db.create_all()
#http://techarena51.com/index.php/one-to-many-relationships-with-flask-sqlalchemy/