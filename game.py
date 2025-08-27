import config, json, requests, os, random, time, html


class Game:
    """This class simulates a game of Who Wants to be a Millionaire!?"""
    def __init__(self):
        self.current_question = 3
        self.lifelines = ['50/50', 'Ask The Audience', 'Call A Friend']
        self.money_ladder = [
        (500, "easy"), (1000, "easy"), (2000, "easy"), (3000, "easy"), (5000, "easy"),
        (7500, "medium"), (10000, "medium"), (12500, "medium"), (15000, "medium"), (25000, "medium"),
        (50000, "medium"), (100000, "hard"), (250000, "hard"), (500000, "hard"), (1000000, "hard")]


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
            while len(all_questions[diff]) < desired_count and attempts < 5:
                response = requests.get(
                    config.api,
                    params={"amount": 5, "type": "multiple", "difficulty": diff}
                )

                if response.status_code == 429:
                    print(f"Rate limit hit for {diff}. Waiting 2 seconds before retry...")
                    time.sleep(2)
                    attempts += 1
                    continue

                if response.status_code != 200:
                    print(f"Failed to fetch {diff} questions. Status:", response.status_code)
                    break

                batch = response.json().get("results", [])
                # Remove duplicates
                existing_questions = {q["question"] for q in all_questions[diff]}
                new_questions = [q for q in batch if q["question"] not in existing_questions]

                remaining_slots = desired_count - len(all_questions[diff])
                all_questions[diff].extend(new_questions[:remaining_slots])

                # Small delay to avoid rate limit
                time.sleep(1)
                attempts += 1

        # Flatten questions in order: easy → medium → hard
        ordered_questions = all_questions["easy"] + all_questions["medium"] + all_questions["hard"]

        with open(f"{config.dir_path}/questions.json", "w", encoding="utf-8") as f:
            json.dump(ordered_questions, f, indent=4, ensure_ascii=False)


    def fetch_question(self):
        """
        Returns the next question based on current_question index,
        with HTML entities decoded for readability.
        """
        money = self.money_ladder[self.current_question][0]

        with open(f'{config.dir_path}/questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)

        question_info = questions[self.current_question]

        # Remove random characters from questions/answers
        question = html.unescape(question_info['question'])
        correct_answer = html.unescape(question_info['correct_answer'])
        options = [html.unescape(opt) for opt in question_info['incorrect_answers']] + [correct_answer]

        # Shuffle the options so correct answer doesn't appear in the same place
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
            if answer.upper() not in ['A','B','C','D','X']:
                print("Invalid Input.")
            elif answer == 'X':
                return None
            else:
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
        '''Checks if the user's choice is the correct answer. Returns True if so.'''
        letters = ['A','B','C','D']
        letters_to_options = dict(zip(letters,options))

        selected = letters_to_options.get(player_choice)

        if selected == correct_answer:
            return True
        else:
            return False
    


# g = Game()
# # g.get_questions_info()
# g.display_question(g.fetch_question()[0], g.fetch_question()[2], g.fetch_question()[3])
# # g.display_lifelines()
# print(g.get_user_answer())