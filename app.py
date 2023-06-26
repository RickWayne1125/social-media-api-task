from flask import jsonify, request, Flask
from models import User, Follow, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db.init_app(app)

secret_info = ['created_at', 'password']  # secret info that should not be returned to other users


def serialize(obj, secret=False):
    data = {}
    for c in obj.__table__.columns:
        # print(c.name, getattr(obj, c.name))
        if getattr(obj, c.name) is not None:
            if secret:
                if c.name not in secret_info:
                    data[c.name] = getattr(obj, c.name)
            else:
                data[c.name] = getattr(obj, c.name)
    # print(data)
    return data


@app.route('/follow', methods=['POST'])
def follow_user():
    data = request.get_json()
    follower_id = data['follower_id']
    followed_id = data['followed_id']

    follow = Follow(follower_id=follower_id, followed_id=followed_id)
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'User followed successfully'}), 201


@app.route('/unfollow', methods=['POST'])
def unfollow_user():
    data = request.get_json()
    follower_id = data['follower_id']
    followed_id = data['followed_id']

    follow = Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        return jsonify({'message': 'User unfollowed successfully'}), 200
    else:
        return jsonify({'message': 'Follow relationship not found'}), 404


@app.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    followers = User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == user_id).all()
    follower_list = [serialize(follower, True) for follower in followers]
    return jsonify({'followers': follower_list}), 200


@app.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    following = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user_id).all()
    following_list = [serialize(followed, True) for followed in following]
    return jsonify({'following': following_list}), 200


if __name__ == '__main__':
    app.run()
