import config, json, requests

class Game:

    def __init__(self, current_question):
        self.current_question = 0
        questions_money_ladder = [(100, 'easy'),(200, 'easy'),(300, 'easy'),(500, 'easy'),(1000, 'easy'),
                          (2000, 'medium'),(4000, 'medium'),(8000, 'medium'), (16000, 'medium'), (32000, 'medium'),
                          (64000, 'hard'), (125000, 'hard'), (250000, 'hard'), (500000, 'hard'), (1000000, 'hard')]


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


    def fetch_question(self):
        '''
        Gets question from json file based on difficulty 
        displays question/answer options and money to win to the user 
        '''
        
        # set the variables for question, correct_answer, options 
        # i need to return these variables so i can use them in check_answer to check 
        # user input == check answer when the user answers to the question 

    def present_question(self):
        '''
        Presents question, option and money to user 
        '''


    def user_answer(self):
        '''
        Asks user for their response A/B/C/D or lifeline option if relevant
        checks if user input valid 
        if valid: return user response (A/B/C/D) or call relevant method for lifeline option and remove it after used
        '''

    def check_answer(self):
        '''
        Check the answer of the user if equal to fetch_question 
        
        '''
        # if correct > self.current_question += 1 
        # if incorrect > while loop breaks and we give summary 



