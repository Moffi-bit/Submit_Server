import requests

def post_user():
    user_json = {
        "first": "john",
        "last": "larry",
        "email": "yessir@gmail",
        "user": "geek",
        "pass": "coding",
    }

    user_id = requests.post('http://127.0.0.1:5000/login/user/', data=user_json)

    return user_id.text

def post_class():
    user_json = {
        "name": "math400",
    }

    class_id = requests.post('http://127.0.0.1:5000/login/class/', data=user_json)

    return class_id.text

def get_user(id):
    return requests.get(f'http://127.0.0.1:5000/login/user/{id}').text

def main():
    id_of_new_user = post_user()
    id_of_new_class = post_class()
    print(get_user(id_of_new_user))

if __name__ == "__main__":
    main()
