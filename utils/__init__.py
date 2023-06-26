import random

from app import app, db
from faker import Faker
from models import User, Follow


def generate_users(user_amount=50):
    num_users = int(user_amount)  # Default to generating 10 users

    fake = Faker()

    for _ in range(num_users):
        username = fake.user_name()
        user = User(username=username)
        db.session.add(user)
        db.session.commit()


def generate_followings(following_amount=30):
    num_followings = int(following_amount)  # Default to generating 10 followers

    users = User.query.all()

    for user in users:
        for _ in range(num_followings):
            random_user = random.choice(users)
            if random_user is not user:
                follow = Follow(follower_id=user.id, followed_id=random_user.id)
                # check if follow relationship already exists
                if not Follow.query.filter_by(follower_id=user.id, followed_id=random_user.id).first():
                    db.session.add(follow)
                    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        generate_users()
        generate_followings()
