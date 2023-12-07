"""Import libraries"""
from datetime import datetime
from flask_login import UserMixin
from app import db

user_post = db.Table('user_post',
                     db.Column('user_id', db.Integer,
                               db.ForeignKey("user.id")),
                     db.Column('posts_id', db.Integer,
                               db.ForeignKey("posts.id"))
                     )

post_like = db.Table('post_like',
                     db.Column('user_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('post_id', db.Integer,
                               db.ForeignKey('posts.id')),
                     db.UniqueConstraint(
                         'user_id', 'post_id', name='unique_user_post_like')
                     )

post_dislike = db.Table('post_dislike',
                        db.Column('user_id', db.Integer,
                                  db.ForeignKey('user.id')),
                        db.Column('post_id', db.Integer,
                                  db.ForeignKey('posts.id')),
                        db.UniqueConstraint(
                            'user_id', 'post_id', name='unique_user_post_dislike')
                        )


class User(db.Model, UserMixin):
    """Model of the User"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    nationality = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    relationship_status = db.Column(db.String(120), nullable=True)
    student_bio = db.Column(db.Text(), nullable=True)
    major = db.Column(db.String(200), nullable=True)
    year_of_study = db.Column(db.Integer(), nullable=True)
    birthdate = db.Column(db.DateTime, nullable=True)
    linkedIn = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(200), nullable=True)
    snapchat = db.Column(db.String(200), nullable=True)
    viewd = db.relationship('Posts', secondary=user_post, backref='viewers')
    blogs_created = db.relationship('Posts', back_populates='blog_creator')

    def __str__(self):
        return f'{self.name}'


class Posts(db.Model):
    """Model of the Posts"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text())
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    blogger_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable="False")
    blog_creator = db.relationship('User', back_populates='blogs_created')
    likes = db.relationship('User', secondary=post_like, backref='liked_posts')
    dislikes = db.relationship(
        'User', secondary=post_dislike, backref='disliked_posts')
    score = db.Column(db.Float)

    def calculate_score(self):
        """Model to calculate score of post"""
        like_weight = 1
        dislike_weight = -1
        recency_weight = -0.1

        score = (len(self.likes) * like_weight) + \
            (len(self.dislikes) * dislike_weight)

        # If the date exists
        if self.date_posted is not None:
            current_date = datetime.utcnow()
            days_difference = (current_date - self.date_posted).days
            # If the day difference is more than 10 then make it so that it has a lower score
            if days_difference >= 10:
                recency_score = days_difference * -1
            else:
                recency_score = recency_weight * days_difference
        else:
            recency_score = 0

        self.score = score + recency_score

    def __str__(self):
        return f'<Posts: {self.title}, Score: {self.score}>'
