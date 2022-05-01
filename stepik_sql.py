
from functools import reduce
import requests
import os
import time
import random
from dotenv import load_dotenv

url = 'https://stepik.org/api/steps'
url_courses = 'https://stepik.org/api/courses'
url_sections = 'https://stepik.org/api/sections'
url_units = 'https://stepik.org/api/units'
url_lessons = 'https://stepik.org/api/lessons'
url_steps = 'https://stepik.org/api/steps'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    load_dotenv(dotenv_file)

SESSION_ID = os.environ.get('SESSION_ID')
COURSE_ID = int(os.environ.get('COURSE_ID'))
USRER_ID = int(os.environ.get('USRER_ID'))

header_1 = {
    'Cookie': SESSION_ID,
    'Host': 'stepik.org',
}
page_number = 1
steps_id = []
req_courses = requests.get(
    url=url_courses, headers=header_1, params={'ids[]': COURSE_ID})

sql_ids_sections = req_courses.json()['courses'][0]['sections']
sections_param = '&'.join(map(lambda id: f'ids[]={id}', sql_ids_sections))
all_sections = requests.get(
    url=f'{url_sections}?{sections_param}', headers=header_1)
time.sleep(1 + random.random())

sql_ids_units_ls = reduce(
    lambda a, b: a + b, [value['units'] for value in all_sections.json()['sections']], [])
units_param = '&'.join(map(lambda id: f'ids[]={id}', sql_ids_units_ls))
all_units = requests.get(url=f'{url_units}?{units_param}', headers=header_1)
time.sleep(1 + random.random())


sql_ids_lessons = [value['lesson'] for value in all_units.json()['units']]
lessons_param = '&'.join(map(lambda id: f'ids[]={id}', sql_ids_lessons))
all_lessons = requests.get(url=f'{url_lessons}?{lessons_param}', headers=header_1)
time.sleep(1 + random.random())


sql_ids_steps = [value['steps'] for value in all_lessons.json()['lessons']]
sql_ids_steps_united = reduce(lambda a, b: a+b, sql_ids_steps, [])
steps_params = '&'.join(map(lambda id: f'ids[]={id}', sql_ids_steps_united))
all_steps = requests.get(url=f'{url_steps}?{steps_params}', headers=header_1)
time.sleep(1 + random.random())

tasks_sql = filter(lambda value: value['block']['name'] == 'sql' and value['status'] == 'ready', all_steps.json()['steps'])
tasks_sql_text = map(lambda value: value['block']['text'], tasks_sql)

steps_params_st = '&'.join(map(lambda id: f'steps[]={id}', sql_ids_steps_united))


def step_for_submission(tasks_sql):
    matched_data = []
    tasks = list(tasks_sql)
    requests_left = len(tasks)
    for value in tasks:
        step = value['id']
        text = value['block']['text']
        req_1 = requests.get(
            url='https://stepik.org/api/submissions',
            params={
                'order': 'desc',
                'user': USRER_ID,
                'step': step}, headers=header_1)
        submissions = req_1.json()['submissions']
        submission = submissions[-1] if len(submissions) > 0 else None
        result = submission['reply']['solve_sql'] if submission is not None else 'NOT SOLVED!'
        matched_data.append((text, result))
        requests_left -= 1
        print(requests_left)
        time.sleep(1 + random.random())
    return matched_data


html_data = ''.join([f'{value[0]} <br><hr><br> <pre><code class="hljs language-sql">{value[1]}</code></pre>' for value in step_for_submission(tasks_sql)])
with open('template/tasks.html', 'r') as ins:
    with open('result/tasks.html', 'w') as out:
        copy_data = ins.read()
        new_data = copy_data.replace('{{TASKS PLACEHOLDER}}', html_data)
        out.write(new_data)
