import spacy
from spacy.tokens import Token
import os
import random
from enum import Enum

nlp = spacy.load("en_core_web_lg")

words = {}

directory = "language/words"
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="r", encoding="utf-8") as f:
        words[filename] = [l.strip() for l in f]


def replace_words_by_tag_random(text: str):

    doc = nlp(text)
    result = ""

    for tok in doc:

        word: str = tok.text
        tag = tok.tag_
        cap = tok.is_upper
        title = tok.is_title

        if not should_ignore(tok) and tag in words:
            word = random.choice(words[tag])
            if title:
                word = word.title()
            elif cap:
                word = word.upper()

        result += word
        result += tok.whitespace_

    return result


def should_ignore(tok: Token):

    return tok.lemma_ in words["IGNORE"]

