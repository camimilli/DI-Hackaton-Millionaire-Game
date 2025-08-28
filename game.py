import config, json, requests, os, random, time, html, db
import google.generativeai as genai 

class Game:
    """This class simulates a game of Who Wants to be a Millionaire!?"""

    def __init__(self):
        self.current_round = 0
        self.lifelines = ['50/50', 'Ask The Audience', 'Call A Friend']
        self.money_ladder = [
            500, 1000, 2000, 3000, 5000,
            7500, 10000, 12500, 15000, 25000,
            50000, 100000, 250000, 500000, 1000000
        ]

        # Authenticate API call to Gemini
        genai.configure(api_key=config.gemini_api_key)

        # Configure Gemini AI model 
        self.ai_model = genai.GenerativeModel('models/gemini-1.5-flash')

        # path for questions file 
        questions_file = f"{config.dir_path}/questions.json"

        # Only fetch from API if JSON file does not exist, otherwise initialize questions AS get_questions_info method
        if not os.path.exists(questions_file):
            self.get_questions_info() 

        # If API exists, initialize questions as an attribute type dict
        with open(questions_file, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
    
    def get_questions_info(self):
            """
            Fetch exactly 5 questions per difficulty from Open Trivia DB
            Load them into a JSON file by order of difficulty.
            """
            difficulties = ["easy", "medium", "hard"]
            desired_count = 5
            all_questions = {"easy": [], "medium": [], "hard": []}

            print("Loading game...")

            for diff in difficulties:
                attempts = 0
                
                # Will move to next difficulty once length of list is 5 or more 5 attempts are made
                while len(all_questions[diff]) < desired_count and attempts < 5:
                    response = requests.get(
                        config.api_trivia,
                        params={"amount": 15, "type": "multiple", "difficulty": diff}  # Parameters are added to the base
                    )                                                                  # API using the defined variables
                    
                    # Ensures that the method will continue working until 5 unique questions are extracted from API
                    # 429 Response Code = Too Many Requests
                    if response.status_code == 429:
                        print('Initializing questions...')
                        time.sleep(2)
                        attempts += 1
                        continue
                    
                    # If no successful connection is made to the API, the program will end
                    if response.status_code != 200:
                        print(f"Failed to fetch {diff} questions. Status:", response.status_code)
                        break

                    batch = response.json().get("results", [])
                    # Remove duplicates
                    existing_texts = {q["question"] for q in all_questions[diff]}
                    new_questions = [q for q in batch if q["question"] not in existing_texts]


                    remaining_slots = desired_count - len(all_questions[diff])
                    all_questions[diff].extend(new_questions[:remaining_slots])

                    # Small delay to avoid rate limit
                    time.sleep(1)
                    attempts += 1

                if len(all_questions[diff]) < desired_count:
                    print(f"Warning: Only fetched {len(all_questions[diff])} {diff} questions from API.")
            
            # Flatten questions in order: easy → medium → hard
            ordered_questions = all_questions["easy"] + all_questions["medium"] + all_questions["hard"]

            with open(f"{config.dir_path}/questions.json", "w", encoding="utf-8") as f:
                json.dump(ordered_questions, f, indent=4, ensure_ascii=False)


    def fetch_question(self)->tuple:
        """
        Takes the dictionary of the question 
        at the current index and returns 4 variables
        the question text, the money value, the correct answer
        and the 4 answer options
        """

        # money value is assigned to each question depending on the current round
        money = self.money_ladder[self.current_round]

        # retrieves the dictionary of the current question
        question_dict = self.questions[self.current_round]

        # set the value of the desired variables using the dict values
        question = html.unescape(question_dict['question'])
        correct_answer = html.unescape(question_dict['correct_answer'])

        # incorrect answers + correct answers need to be combined into a single list
        options = [html.unescape(opt) for opt in question_dict['incorrect_answers']] + [correct_answer]

        # Shuffle so that correct answer always is in a random place
        random.shuffle(options)

        return question, correct_answer, options, money
    

    def display_question(self, question, options, money)->str:
        '''
        Prints the current question and answer options (in A,B,C,D format)
        '''

        print(f"\nYour ${money} Question is:\n")
        print(question)
        letters = ['A', 'B', 'C', 'D']
        for letter, option in zip(letters, options):
            print(f"({letter}) {option}")
    

    def display_lifelines(self)->str:
        '''
        Prints the current lifelines available to the user
        '''
        for i, lifeline in enumerate(self.lifelines):
            print(f'({i}) {lifeline}')


    def get_user_input(self)->tuple:
        '''
        Asks the user whether they want to answer the question or use a lifeline
        '''

        while True:

            if self.lifelines:
                try:
                    user_input = int(input("\nWould you like to:\n(1) Answer\n(2) Use a Lifeline\n"))
                except ValueError:
                    print('Invalid Input. Enter 1 or 2')
                    continue

            else:
                # If no lifelines are left, force them to answer
                print("\nYou don't have any lifelines left. You must answer.")
                user_input = 1

            if user_input == 1:
                answer = self.get_user_answer()
                return ('ANSWER', answer)
            
            elif user_input == 2:
                lifeline_idx = self.choose_lifeline()
                return ('LIFELINE', lifeline_idx)
            
    
    def get_user_answer(self)->str:
        '''Prompts the user to enter an answer(A-D) or to go back (X)'''
        while True:
            answer = input("Enter your answer or press (9) to go back: ").upper().strip()
            if answer not in ['A','B','C','D','9']:
                print("Invalid Input.")
                continue 
            return answer


    def choose_lifeline(self):
        """Display lifelines and prompt the player to choose one."""
        while True:
            print("\nYour Lifelines:")
            self.display_lifelines()
            try:
                lifeline_index = int(input("Pick a lifeline or (9) to go back: "))
            except ValueError:
                print("Invalid input. Choose one of the above numbers.")
                continue

            if lifeline_index == 9:
                return 9
            elif lifeline_index not in range(len(self.lifelines)):
                print("Invalid input. Choose one of the above numbers.")
                continue
            else:
                # remove the chosen lifeline from self and return it
                chosen_lifeline = self.lifelines.pop(lifeline_index)
                return chosen_lifeline

    def check_answer(self, player_choice, options, correct_answer):
        '''Checks if the user's choice is the correct answer. Returns True or False'''
        letters = ['A','B','C','D']
        letters_to_options = dict(zip(letters,options))

        selected = letters_to_options.get(player_choice)

        if selected == correct_answer:
            return True
        else:
            return False
    
    def use_lifeline(self, question, correct_answer, options, lifeline):
        if lifeline == '50/50':
             help = self.lifeline_50_50(options, correct_answer) 
        elif lifeline == 'Ask The Audience':
            help = self.lifeline_ask_the_audience(question, options)
        else:
            help = self.lifeline_call_a_friend(question, options)        
        return help 


    def lifeline_50_50(self, options, correct_answer)->list:
        '''
        Removes two incorrect answers from the given options and returns a list 
        containing one incorrect answer and the correct answer
        '''
        incorrect_answers = [opt for opt in options if opt != correct_answer]
        random.shuffle(incorrect_answers)
        new_options = [correct_answer, incorrect_answers[0]]
        random.shuffle(new_options)
        return f"\nYour new options are: {new_options[0]} or {new_options[1]}"
        

    def lifeline_call_a_friend(self, question, options):
        '''
        Simulates a phone call to a friend using Gemini API
        so the user can get help 
        '''

        # Phone call simulation
        print("📞 Dialing your friend...", end='', flush=True)
        for _ in range(3):
            time.sleep(1)
            print(" .", end='', flush=True)
        time.sleep(1)
        print("\nYour friend is on the line 🙋")

        # API call - prompt and response 
        prompt = f"I'm on the 'Who Wants To Be a Millionaire Gameshow' and I've called you as I need your help.\
            the questions is: '{question}'. The options are: {options}. Please give me your best guess and a short explanation,\
            but don't just say 'the answer is X'. Say something like, 'I'm pretty sure it's...' or 'I think I remember hearing that...'.\
            Give a hint or reason behind your choice and say something funny at the end to end the call like 'If you win, take me on that vacation you promised' \
            or ask how's the weather or something similar."
        response = self.ai_model.generate_content(prompt)
        return f"\nYour friend says:\n{response.text}"


    def lifeline_ask_the_audience(self, question, options):

        # Simulate audience voting
        print("Let's ask the audience what they think 🤔")
        print("\nAudience voting now...", flush=True)

        # Dramatic wait 
        for _ in range(3):
            time.sleep(1)
            print(".", flush=True)
        time.sleep(1)

        # API call - prompt and response
        prompt = f"You are simulating a 'Who Wants To Be a Millionaire' show audience. The player has asked for a vote.\
                   The question is: '{question}'\
                   The four options are: {options}\
                   Please respond with a list of vote percentages for each option. Make it look like real audience votes, where the correct answer has a higher percentage,\
                   but not always a 100% majority. Present the percentages as a simple list.\
                   Example response: Make sure you substitute Option 1, 2, 3... with the options I gave you for the question on the same order\
                   and you remove the Option 1, Option 2...\
                   Option 1: 75%\
                   Option 2: 10%\
                   Option 3: 5%\
                   Option 4: 10%"
        
        print("\nAudience Results: 🗳️")
        time.sleep(1)

        response = self.ai_model.generate_content(prompt)
        audience_votes = response.text 
        return audience_votes


    def play_round(self):

        # Initiate values for round 
        question, correct_answer, options, money = self.fetch_question()

        # Display question to user 
        self.display_question(question, options, money)

        while True:
            action, value = self.get_user_input()

            if action == 'ANSWER':
                if value == '9':
                    self.display_question(question, options, money)
                    # Go back to choose ANSWER or LIFELINE
                    continue
                
                else: 
                    is_correct = self.check_answer(value, options, correct_answer)

                    # log answer to db 
                    db.log_answer(question, value, correct_answer, money)

                    if is_correct:
                        print(f'You guessed correctly and won ${money}!')
                        self.current_round += 1 
                        return True
                    else:
                        print('Wrong answer!')
                        return False 
                    
            elif action == 'LIFELINE':
                lifeline_chosen = value 

                if lifeline_chosen == 9:
                    self.display_question(question, options, money)
                    # Go back to choose ANSWER or LIFELINE
                    continue
                else:
                    help_message = self.use_lifeline(question, correct_answer, options, lifeline_chosen)
                    if help_message:
                        print(help_message)
                    self.display_question(question, options, money)
                    continue 