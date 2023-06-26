import requests

BASE_URL = 'http://localhost:5000'  # Update with your actual API base URL


def test_follow_user():
    url = f'{BASE_URL}/follow'
    data = {'follower_id': 1, 'followed_id': 2}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.content}')


def test_unfollow_user():
    url = f'{BASE_URL}/unfollow'
    data = {'follower_id': 1, 'followed_id': 2}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.content}')


def test_get_followers():
    user_id = 2  # User ID for which to get the follower list
    url = f'{BASE_URL}/followers/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.content}')


def test_get_following():
    user_id = 1  # User ID for which to get the following user list
    url = f'{BASE_URL}/following/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f'Error: {response.status_code} - {response.content}')


# Run the tests
if __name__ == '__main__':
    test_follow_user()
    test_get_followers()
    test_get_following()
    test_unfollow_user()
