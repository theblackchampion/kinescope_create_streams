import json
import gspread
import requests
from datetime import datetime
from teachers_with_id_folders import id_folders_vod
from teachers_with_id_folders import id_folders_live
from teachers_with_id_folders import link_posters
from umschool_api import insert_video_link

url = "https://api.kinescope.io/v2/live/events"
url_poster = "https://uploader.kinescope.io/poster"
gc = gspread.service_account(filename="cedar-context-373016-19a269322637.json")

sh = gc.open_by_key("1VJnSXjIGxFY0WaOZZjjy8060szJ6mBE0l1YELTK1byI")
worksheet = sh.sheet1

headers = {"Authorization": "Bearer 70e1b60d-569b-432b-b133-dae869599023"}
def convert_month(date_lesson):
    month_dict = {"1": "ЯНВАРЬ", "2": "ФЕВРАЛЬ", "3": "МАРТ", "4": "АПРЕЛЬ", "5": "МАЙ", "6": "ИЮНЬ", "7": "ИЮЛЬ",
                  "8": "АВГУСТ", "9": "СЕНТЯБРЬ", "10": "ОКТЯБРЬ", "11": "НОЯБРЬ", "12": "ДЕКАБРЬ"}
    datetimesplit = date_lesson.split(".")
    month = datetimesplit[1]
    if month != "10":
        month = datetimesplit[1].replace("0", "")
    else:
        month = datetimesplit[1]
    return month_dict[month]

def convert_time(date_lesson, time_lesson): #2023-12-19T00:05:41.634922Z
    year_lesson = str(datetime.now().year)
    datetimesplit = date_lesson.split(".")
    numbermonth = datetimesplit[0]
    month = datetimesplit[1]
    timesplit = time_lesson.split(":")
    time = int(timesplit[0])-3
    time_lesson = str(time) + ":" + timesplit[1]
    datetime_lesson = year_lesson + "-" + month + "-" + numbermonth + "T" + time_lesson + ":00.000000Z"
    return datetime_lesson

#def find_class(i):
#    class_lesson = ["", "", ""]
#    class_dict = {0: "ЕГЭ", 1: "ОГЭ", 2: "10 класс"}
#    class_lesson[0] = worksheet.cell(i, 1).value
#    class_lesson[1] = worksheet.cell(i, 2).value
#    class_lesson[2]= worksheet.cell(i, 3).value
#    class_name = class_dict[class_lesson.index("TRUE")]
#    return class_name

def upload_poster(id_stream, teacher):
    payload = "<file contents here>"
    headers = {
        "Authorization": "Bearer 70e1b60d-569b-432b-b133-dae869599023",
        'X-Video-ID': id_stream,
        'X-Poster-URL': link_posters[teacher],
        'Content-Type': 'text/plain'
    }
    response = requests.post(url_poster, headers=headers, data=json.dumps(payload)).json()
    return print(response)

#def move_stream(id_stream, teacher):
#    url_move_stream = f"https://api.kinescope.io/v2/live/events/{id_stream}/move"
#    payload = {"parent_id": id_folders_live[teacher]}
#    headers = {"Authorization": "Bearer 70e1b60d-569b-432b-b133-dae869599023"}
#    response = requests.put(url_move_stream, headers=headers, data=json.dumps(payload)).json()
#    return print(response)

for i in range(1, 3):
    date_lesson = worksheet.cell(i, 4).value
    time_lesson = worksheet.cell(i, 9).value
    teacher = worksheet.cell(i, 6).value
    if teacher not in link_posters:
        worksheet.update_cell(i, 11, 'Ошибка при заполнении преподавателя!')
        continue
    datetime_lesson = convert_time(date_lesson, time_lesson)
    subject = worksheet.cell(i, 5).value
    lesson_live_link = worksheet.cell(i, 8).value
    #payload = {"name": "МАСТЕР-ГРУППА (АПРЕЛЬ) - " + subject, "type": "one-time", "auto_start": False, "dvr": True, "save_stream": True, "folder_id": id_folders[teacher], "scheduled_at": datetime_lesson}
    payload = {"name": f"МАСТЕР-ГРУППА ({convert_month(date_lesson)}) - " + subject + " с " + teacher,
               "type": "one-time",
               "auto_start": False,
               "dvr": True,
               "parent_id": id_folders_live[teacher],
               "scheduled": {"time": datetime_lesson},
               "record": {"parent_id": id_folders_vod[teacher]}
               }
    response = requests.post(url, headers=headers, data=json.dumps(payload)).json()
    lesson_link = response["data"]["play_link"]
    id_stream = response["data"]["id"]
    upload_poster(id_stream, teacher)
    #move_stream(id_stream, teacher)
    worksheet.update_cell(i, 11, lesson_link)
    #lesson_id = lesson_live_link.split('/')[4]
    #insert_video_link(lesson_id, lesson_link)
    print(response)

