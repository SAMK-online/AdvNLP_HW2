from typing import AnyStr, Any
from gentopia.tools.basetool import *
import re
import math

class PaperReadabilityScoreArgs(BaseModel):
    text: str = Field(..., description="The text of the research paper to analyze.")

class PaperReadabilityScorer(BaseTool):
    name = "paper_readability_scorer"
    description = "Assesses the readability of research papers using Flesch-Kincaid Grade Level and Flesch Reading Ease scores."
    args_schema: Optional[Type[BaseModel]] = PaperReadabilityScoreArgs

    def _count_syllables(self, word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def _calculate_scores(self, text):
        sentences = re.findall(r'\w+[.!?][\s]{1,2}', text)
        words = re.findall(r'\w+', text)
        
        total_sentences = len(sentences)
        total_words = len(words)
        total_syllables = sum(self._count_syllables(word) for word in words)

        if total_sentences == 0 or total_words == 0:
            return None, None

        avg_sentence_length = total_words / total_sentences
        avg_syllables_per_word = total_syllables / total_words

        flesch_kincaid_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        flesch_reading_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

        return round(flesch_kincaid_grade, 2), round(flesch_reading_ease, 2)

    def _interpret_scores(self, fk_grade, flesch_ease):
        grade_interpretation = f"Flesch-Kincaid Grade Level: {fk_grade}. "
        if fk_grade <= 6:
            grade_interpretation += "This text is very easy to read, suitable for elementary school level."
        elif 6 < fk_grade <= 10:
            grade_interpretation += "This text is easy to read, suitable for middle school to early high school level."
        elif 10 < fk_grade <= 14:
            grade_interpretation += "This text is fairly difficult to read, suitable for high school to college level."
        else:
            grade_interpretation += "This text is very difficult to read, suitable for college graduate level and above."

        ease_interpretation = f"Flesch Reading Ease Score: {flesch_ease}. "
        if flesch_ease >= 90:
            ease_interpretation += "The text is very easy to read and understand."
        elif 70 <= flesch_ease < 90:
            ease_interpretation += "The text is easy to read."
        elif 50 <= flesch_ease < 70:
            ease_interpretation += "The text is fairly difficult to read."
        else:
            ease_interpretation += "The text is very difficult to read."

        return grade_interpretation + "\n" + ease_interpretation

    def _run(self, text: AnyStr) -> Any:
        fk_grade, flesch_ease = self._calculate_scores(text)
        if fk_grade is None or flesch_ease is None:
            return "Unable to calculate readability scores. The text might be too short or contain no complete sentences."
        
        interpretation = self._interpret_scores(fk_grade, flesch_ease)
        return interpretation

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    