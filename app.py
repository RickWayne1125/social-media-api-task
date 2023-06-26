import json

from flask import jsonify, request, Flask
from models import User, followers, db
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


def flush_redis_follows(follower_id: int, following_id: int):
    redis.delete(f'followers:{following_id}')
    redis.delete(f'following:{follower_id}')


@app.route('/follow', methods=['POST'])
def follow_user():
    data = request.get_json()
    follower_id = data['follower_id']
    following_id = data['following_id']

    user = User.query.filter_by(id=follower_id).first()
    if not user:
        return jsonify({'message': 'Follower user not found'}), 404
    following = User.query.filter_by(id=following_id).first()
    if not following:
        return jsonify({'message': 'Followed user not found'}), 404

    # Check if already following
    if following in user.following:
        return jsonify({'message': 'Already following'}), 400
    else:
        user.following.append(following)

    db.session.commit()

    # Invalidate Redis cache
    flush_redis_follows(follower_id, following_id)

    return jsonify({'message': 'User following successfully'}), 201


@app.route('/unfollow', methods=['POST'])
def unfollow_user():
    data = request.get_json()
    follower_id = data['follower_id']
    following_id = data['following_id']

    user = User.query.filter_by(id=follower_id).first()
    if not user:
        return jsonify({'message': 'Follower user not found'}), 404
    following = User.query.filter_by(id=following_id).first()
    if not following:
        return jsonify({'message': 'Followed user not found'}), 404

    if following not in user.following:
        return jsonify({'message': 'Not following'}), 400

    user.following.remove(following)
    db.session.commit()

    flush_redis_follows(follower_id, following_id)

    return jsonify({'message': 'User unfollowing successfully'}), 200


@app.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    # Check if user_id is cached in Redis
    cached_followers = redis.get(f'followers:{user_id}')
    if cached_followers:
        follower_list = json.loads(cached_followers)
        print('hit')
    else:
        print('miss')
        user = User.query.filter_by(id=user_id).first()

        follower_list = [serialize(follower, True) for follower in user.followers]
        # Cache followers in Redis
        redis.set(f'followers:{user_id}', json.dumps(follower_list))
    return jsonify({'followers': follower_list}), 200


@app.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    offset = request.args.get('offset', default=0, type=int)
    limit = 20  # Number of results per request
    # Check if user_id is cached in Redis
    cached_following = redis.get(f'following:{user_id}')
    if cached_following:
        following_list = json.loads(cached_following)
        if offset * limit >= len(following_list):
            return jsonify({'message': 'No more users to show'}), 404
        following_list = following_list[offset * limit: min((offset + 1) * limit, len(following_list))]
        print('hit')
    else:
        print('miss')
        user = User.query.filter_by(id=user_id).first()
        following_list = [serialize(following) for following in user.following]
        # Cache following in Redis
        redis.set(f'following:{user_id}', json.dumps(following_list))
        if offset * limit >= len(following_list):
            return jsonify({'message': 'No more users to show'}), 404
        following_list = following_list[offset * limit: min((offset + 1) * limit, len(following_list))]
    if len(following_list) == 0:
        return jsonify({'message': 'No more users to show'}), 404
    return jsonify({'following': following_list}), 200


if __name__ == '__main__':
    app.run(debug=True)
