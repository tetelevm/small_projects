# !! An updated and improved version is in `lorem_text_bot` project

"""
Pseudoword generator using books/text.
Requires prefetched data.

The algorithm is as follows:
  1) collect the entire text array
  2) move the cursor to a random place
  3) memorize the next two letters and write them into the resulting text
  4) move the cursor to a random place
  5) move the cursor forward to the first occurrence of these letters
     in the text
  6) if the resulting text is still insufficient, return to step 3)
"""

import os
import re
from random import randint
from pathlib import Path


# on Windows, this should have the format
# PATH_TO_TEXT = 'C:\\Users\\t\\folder_with_text\\'
PATH_TO_TEXT = '/home/t/folder_with_text/'
CHARS_LEN = 3
WORD_COUNT = 500

LETTERS = r'А-Яа-яЁё'  # now only for russian language
END_SENTENCE_MARKS = r'.'
OTHER_MARKS = r','
PUNCTUATION_MARKS = END_SENTENCE_MARKS + OTHER_MARKS

class LoremGenerator:
    def __init__(self, path=PATH_TO_TEXT):
        self.input_text = self.get_text(path)
        self.len_text = len(self.input_text)

    @staticmethod
    def read_text(path) -> str:
        """
        A method that searches for a file/files with text and reads text
        from it. If the path is a folder, all files with the extension
        `.txt` are searched.

        :param path: the path to the folder or file
        :return: text from files
        """

        path = Path(path)

        if path.is_dir():
            paths_to_text = list()
            for (folder, _, files) in os.walk(path):
                txt_files = (
                    file
                    for file in files
                    if file.endswith('.txt')
                )
                for file in txt_files:
                    paths_to_text.append(f'{folder}/{file}')
        elif path.is_file():
            paths_to_text = [path]
        else:
            raise ValueError(f'{path} is not file or dir!')

        text = '\n'.join(
            open(file, encoding="utf8").read()
            for file in paths_to_text
        )
        return text

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        It converts the raw text to the form required for the algorithm.
        :param text: raw text
        :return: processed text
        """
        text = text.lower()
        text = ' '.join(line.rstrip().lstrip() for line in text.splitlines())

        text = re.sub(fr'[^{LETTERS}\s{PUNCTUATION_MARKS}]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.rstrip().lstrip()

        return text

    @classmethod
    def get_text(cls, path):
        text = cls.read_text(path)
        text = cls.preprocess_text(text)
        return text

    def generate_raw_lorem(self, words: int, chars_len: int) -> str:
        input_text = self.input_text + self.input_text[:chars_len]
        max_index = self.len_text - chars_len

        set_cursor = lambda: randint(0, max_index)
        resulting_text = ' '
        current_chars = ''

        while resulting_text.count(' ') < words + 1:
            # get chars
            start = set_cursor()
            first_index = input_text.find(current_chars, start, max_index)
            if first_index == -1:
                first_index = input_text.find(current_chars)
            first_index += chars_len
            current_chars = input_text[first_index : first_index + chars_len]

            # add chars
            chars_to_set = current_chars

            if resulting_text[-1] == ' ' and chars_to_set[0] == ' ':
                # this should not happen, since there are no two spaces
                # in a row, but still
                chars_to_set = chars_to_set[1:]

            if (
                resulting_text[-1] in PUNCTUATION_MARKS
                and chars_to_set[0] in PUNCTUATION_MARKS
            ):
                chars_to_set = chars_to_set[1:]

            resulting_text += chars_to_set

        return resulting_text

    @staticmethod
    def postprocess_lorem(text: str) -> str:
        """
        Processing raw text into humanoid text.

        :param text: generated text
        :return: humanoid text
        """

        if text[0] == '.':
            text = text[1:]
        text = text.lstrip().rstrip()

        # only one punctuation mark consecutive
        dot_dot_pattern = re.compile(fr'([{PUNCTUATION_MARKS}])+')
        text = dot_dot_pattern.sub(r'\1', text)

        # spaces after punctuation marks
        dot_word_pattern = re.compile(fr'([{PUNCTUATION_MARKS}])([{LETTERS}])')
        text = dot_word_pattern.sub(r'\1 \2', text)

        # no spaces before punctuation marks
        space_dot_pattern = re.compile(fr'(\s)+([{PUNCTUATION_MARKS}])')
        text = space_dot_pattern.sub(r'\2', text)

        # the first letter in the sentence should be capitalized
        sentences_pattern = re.compile(fr'([{END_SENTENCE_MARKS}]\s)')
        text = ''.join(
            sentence.capitalize()
            for sentence in sentences_pattern.split(text)
        )

        if text[-1] not in END_SENTENCE_MARKS:
            if text[-1] in OTHER_MARKS:
                text = text[:-1]
            text += '.'
        return text

    def generate_lorem(self, words=WORD_COUNT, chars_len=CHARS_LEN) -> str:
        resulting_text = self.generate_raw_lorem(words, chars_len)
        resulting_text = self.postprocess_lorem(resulting_text)
        return resulting_text


if __name__ == '__main__':
    generator = LoremGenerator()
    print(generator.generate_lorem())
