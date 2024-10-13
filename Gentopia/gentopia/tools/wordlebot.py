import random
from typing import List
from gentopia.tools.basetool import *
import nltk
from nltk.corpus import words

class WordlePlayerArgs(BaseModel):
    action: str = Field(..., description="Action to perform: 'generate', 'evaluate', or 'hint'")
    word: str = Field("", description="The secret word (for evaluation)")
    guess: str = Field("", description="The player's guess (for evaluation)")

class WordlePlayer(BaseTool):
    name = "wordlebot"
    description = "A tool that manages Wordle games, generates words, evaluates guesses, and provides hints."
    args_schema: Optional[Type[BaseModel]] = WordlePlayerArgs

    word_list: List[str] = Field(default_factory=list)
    current_word: str = Field(default="")
    guesses: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        nltk.download('words', quiet=True)
        self.word_list = [word.lower() for word in words.words() if len(word) == 5]
        self.current_word = ""
        self.guesses = []

    def generate_word(self) -> str:
        self.current_word = random.choice(self.word_list)
        self.guesses = []
        return "A new word has been generated. You can start guessing!"

    def evaluate_guess(self, secret_word: str, guess: str) -> str:
        if len(guess) != 5 or guess not in self.word_list:
            return "Invalid guess. Please enter a valid 5-letter word."

        self.guesses.append(guess)
        feedback = ""
        for s, g in zip(secret_word, guess):
            if s == g:
                feedback += "🟩"  # Green
            elif g in secret_word:
                feedback += "🟨"  # Yellow
            else:
                feedback += "⬜"  # Gray

        guess_count = len(self.guesses)
        if guess == secret_word:
            return f"Correct! You guessed the word in {guess_count} {'try' if guess_count == 1 else 'tries'}.\n{feedback}"
        elif guess_count >= 6:
            return f"Game over! The word was {secret_word}.\n{feedback}"
        else:
            return f"Guess {guess_count}/6: {feedback}"

    def provide_hint(self) -> str:
        if not self.current_word:
            return "No active game. Generate a new word first!"

        unused_letters = set('abcdefghijklmnopqrstuvwxyz') - set(''.join(self.guesses))
        hint_letter = random.choice(list(set(self.current_word) & unused_letters))
        return f"Hint: The word contains the letter '{hint_letter}'."

    def _run(self, action: str, word: str = "", guess: str = "") -> str:
        if action == "generate":
            return self.generate_word()
        elif action == "evaluate":
            if not word:
                word = self.current_word
            if not word:
                return "No word has been generated yet. Use 'generate' action first."
            return self.evaluate_guess(word, guess)
        elif action == "hint":
            return self.provide_hint()
        else:
            return f"Invalid action: {action}. Use 'generate', 'evaluate', or 'hint'."

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

# Example usage
if __name__ == "__main__":
    wordle_player = WordlePlayer()
    
    print(f"Word list size: {len(wordle_player.word_list)}")
    
    # Start a new game
    print(wordle_player._run("generate"))
    
    # Simulate some guesses
    guesses = ["apple", "beach", "chair", "dance", "eagle", "flute"]
    for guess in guesses:
        result = wordle_player._run("evaluate", guess=guess)
        print(f"Guessed '{guess}': {result}")
        if "Correct" in result or "Game over" in result:
            break
    
    # Ask for a hint
    print(wordle_player._run("hint"))
    
    # Start a new game
    print(wordle_player._run("generate"))