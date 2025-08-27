import config, json, requests, os, random, time, html


class Game:
    """This class simulates a game of Who Wants to be a Millionaire!?"""
    def __init__(self):
        self.current_question = 3
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
        """
        Returns the next question based on current_question index,
        with HTML entities decoded for readability.
        """
        money = self.money_ladder[self.current_question][0]

        with open(f'{config.dir_path}/questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)

        question = questions[self.current_question]

        # Remove random characters from questions/answers
        q_text = html.unescape(question['question'])
        correct_answer = html.unescape(question['correct_answer'])
        options = [html.unescape(opt) for opt in question['incorrect_answers']] + [correct_answer]

        # Shuffle the options so correct answer doesn't appear in the same place
        random.shuffle(options)

        return q_text, correct_answer, options, money


g = Game()
# g.get_questions_info()
print(g.fetch_question())

