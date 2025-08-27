import requests
import json
import os
import psycopg2

dir_path = os.path.dirname(os.path.realpath(__file__))
api = 'https://opentdb.com/api.php?amount=10'


def get_questions_info():
    '''
    Requests questions from API Trivia 
    and stores them in a json file 
    '''
    response = requests.get(api)

    if response.status_code == 200:
        questions_data = json.loads(response.text)
        with open(f'{dir_path}/questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=4, sort_keys=True)
    else:
        print('Failed to retrieve data')


# add try-except handling 

get_questions_info()

# after each game: 
#   - drop table if exists




