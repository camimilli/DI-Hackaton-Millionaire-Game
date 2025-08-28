import config, json, requests, os, random, time, html

class Game:
    """This class simulates a game of Who Wants to be a Millionaire!?"""

    def __init__(self):
        self.current_round = 2
        self.lifelines = ['50/50', 'Ask The Audience', 'Call A Friend']
        self.money_ladder = [
            500, 1000, 2000, 3000, 5000,
            7500, 10000, 12500, 15000, 25000,
            50000, 100000, 250000, 500000, 1000000
        ]

        questions_file = f"{config.dir_path}/questions.json"

        # Only fetch from API if JSON file does not exist, otherwise initialize questions AS get_questions_info method
        if not os.path.exists(questions_file):
            self.questions = self.get_questions_info() 

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

            for diff in difficulties:
                attempts = 0
                
                # Will move to next difficulty once length of list is 5 or more 5 attempts are made
                while len(all_questions[diff]) < desired_count and attempts < 5:
                    response = requests.get(
                        config.api,
                        params={"amount": 15, "type": "multiple", "difficulty": diff}  # Parameters are added to the base
                    )                                                                  # API using the defined variables
                    
                    # Ensures that the method will continue working until 5 unique questions are extracted from API
                    # 429 Response Code = Too Many Requests
                    if response.status_code == 429:
                        print(f"Rate limit hit for {diff}. Waiting 2 seconds before retry...") 
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

    def fetch_question(self):
        """Takes the dictionary of the question 
        at the current index and returns 4 variables
        the question text, the money value, the correct answer
        and the 4 anser options"""

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
    

    def display_question(self, question, options, money):
        '''Prints the current question and answer options (in A,B,C,D format)'''
        print(f"\nYour ${money} Question is:\n")
        print(question)
        letters = ['A', 'B', 'C', 'D']
        for letter, option in zip(letters, options):
            print(f"({letter}) {option}")
    

    def display_lifelines(self):
        '''Prints the current lifelines available to the user'''
        for i, lifeline in enumerate(self.lifelines):
            print(f'({i}) {lifeline}')


    def get_user_input(self):
        '''Asks the user whether they want to answer the question or use a lifeline'''
        while True:
            try:
                user_input = int(input("Would you like to:\n(1) Answer\n(2) Use a Lifeline\n"))
            except ValueError:
                print('Invalid Input. Enter 1 or 2')
                continue

            if user_input == 1:
                answer = self.get_user_answer()
                if answer is not None:
                    return ('ANSWER', answer)
            
            elif user_input == 2:
                lifeline_idx = self.choose_lifeline()
                return ('LIFELINE', lifeline_idx)
            
    
    def get_user_answer(self):
        '''Prompts the user to enter an answer(A-D) or to go back (X)'''
        while True:
            answer = input("Enter your answer or press (X) to go back: ").upper().strip()
            if answer not in ['A','B','C','D','X']:
                print("Invalid Input.")
            return answer


    def choose_lifeline(self):
        """Display lifelines and prompt the player to choose one."""
        while True:
            print("\nChoose a Lifeline:")
            self.display_lifelines()
            try:
                lifeline_index = int(input("Enter the number of your chosen lifeline: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if lifeline_index not in range(len(self.lifelines)):
                print("Invalid input. Choose one of the above numbers.")
            else:
                return lifeline_index

    def check_answer(self, player_choice, options, correct_answer):
        '''Checks if the user's choice is the correct answer. Returns True or False'''
        letters = ['A','B','C','D']
        letters_to_options = dict(zip(letters,options))

        selected = letters_to_options.get(player_choice)

        if selected == correct_answer:
            return True
        else:
            return False
    


g = Game()
print(g.fetch_question())
# g.display_question(g.fetch_question()[0], g.fetch_question()[2], g.fetch_question()[3])
# g.display_lifelines()
# print(g.get_user_answer())