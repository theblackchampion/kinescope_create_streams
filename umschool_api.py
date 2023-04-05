import requests
from utils import umsch_login, umsch_password

def insert_video_link(lesson_id, lesson_link):
    auth_data = {
        "username": umsch_login,
        "password": umsch_password
    }

    insert_data = {
        "video": lesson_link,
        "with_chat": True
    }

    try:
        api_url = "https://umschool.net/api/"
        s = requests.Session()
        refresh_access = s.post(f"{api_url}auth/obtain/", data=auth_data).json()

        token_auth_main = {"refresh": refresh_access["refresh"], "access": refresh_access["access"]}

        r = requests.patch(f"{api_url}lessons/{lesson_id}/",
                           headers={"Authorization": "Bearer " + token_auth_main["access"]},
                           data=insert_data)

        if r.status_code == 200:
            return True
        return False
    except:
        return False
