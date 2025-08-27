import config, json, requests




def get_questions_info():
    '''
    Requests questions from API Trivia 
    and stores them in a json file 
    '''
    response = requests.get(config.api)

    if response.status_code == 200:
        questions_data = json.loads(response.text)
        with open(f'{config.dir_path}/questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=4, sort_keys=True)
    else:
        print('Failed to retrieve data')