import json

from flask import jsonify, request, Flask
from models import User, Follow, db
from redis import Redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db.init_app(app)
redis = Redis(host='localhost', port=6379)

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


def flush_redis_follows(follower_id: int, followed_id: int):
    redis.delete(f'followers:{followed_id}')
    redis.delete(f'following:{follower_id}')


@app.route('/follow', methods=['POST'])
def follow_user():
    data = request.get_json()
    follower_id = data['follower_id']
    followed_id = data['followed_id']

    follow = Follow(follower_id=follower_id, followed_id=followed_id)
    db.session.add(follow)
    db.session.commit()

    # Invalidate Redis cache
    flush_redis_follows(follower_id, followed_id)

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
        flush_redis_follows(follower_id, followed_id)
        return jsonify({'message': 'User unfollowed successfully'}), 200
    else:
        return jsonify({'message': 'Follow relationship not found'}), 404


@app.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    # Check if user_id is cached in Redis
    cached_followers = redis.get(f'followers:{user_id}')
    if cached_followers:
        follower_list = json.loads(cached_followers)
        print('hit')
    else:
        print('miss')
        followers = User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == user_id).all()
        follower_list = [serialize(follower, True) for follower in followers]
        # Cache followers in Redis
        redis.set(f'followers:{user_id}', json.dumps(follower_list))
    return jsonify({'followers': follower_list}), 200


@app.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    offset = request.args.get('offset', default=0, type=int)
    limit = 20  # Number of results per request
    # Check if user_id is cached in Redis
    cached_following = redis.get(f'following:{user_id}:offset:{offset}')
    if cached_following:
        following_list = json.loads(cached_following)
        print('hit')
    else:
        print('miss')
        following = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == user_id).offset(
            offset * limit).limit(limit).all()
        following_list = [followed.username for followed in following]
        # Cache following in Redis
        redis.set(f'following:{user_id}:offset:{offset}', json.dumps(following_list))
    if len(following_list) == 0:
        return jsonify({'message': 'No more users to show'}), 404
    return jsonify({'following': following_list}), 200


if __name__ == '__main__':
    app.run(debug=True)
