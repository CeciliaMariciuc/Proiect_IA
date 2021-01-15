import re
from collections import Counter
from nltk import pos_tag, word_tokenize
import nltk


def read_text(file):
    lines = open(file).read().split('\n')
    return ' '.join(lines)


def split_into_sentences(text):
    sentences = re.split(r'(?<=[^A-Z].[.?!]) +(?=[A-Z])', text)
    return sentences


def check_stopword(word):
    fopen = open("english", 'r')
    lines = fopen.readlines()
    for line in lines:
        if word == line[-1]:
            return True
    return False


def elim_stopwords(text):
    words = text_tokenize(text)
    for word in words:
        if check_stopword(word.lower()) is True:
            words.remove(word)
    return words


def tokens(sentence):
    words = re.findall(r'[^\s!,.?":;0-9]+', sentence)
    words = [word for word in words if not check_stopword(word)]
    return words


def get_words(text):
    sentences = split_into_sentences(text)

    words = []
    for sentence in sentences:
        words += tokens(sentence)
    return words


def text_tokenize(book):
    tokenize = word_tokenize(book)
    return tokenize


def tagging(tokens):
    tagged_text = pos_tag(tokens)
    return tagged_text


def find_words(list_words, search_words, count):
    """
    verifica daca lista search_words apare in lista de cuvinte in ordinea data
    """
    for i in range(len(list_words) - count):
        if count == 2:
            if search_words[0] == list_words[i].lower() and search_words[1] == list_words[i + 1].lower():
                return True
        elif count == 3:
            if search_words[0] == list_words[i].lower() and search_words[1] == list_words[i + 1].lower() and \
                    search_words[2] == \
                    list_words[i + 2].lower():
                return True
    return False


def find_proper_nouns(tagged_text, all_words):
    """
    gaseste substantive/perechi/triplete de substantive cu majuscula
    """
    proper_nouns = []
    i = 0
    while i < len(tagged_text):
        if tagged_text[i][1] == 'NNP':
            if tagged_text[i + 1][1] == 'NNP':
                if tagged_text[i + 2][1] == 'NNP':
                    found_triplet = [tagged_text[i][0].lower(), tagged_text[i + 1][0].lower(),
                                     tagged_text[i + 2][0].lower()]
                    if find_words(all_words, found_triplet, 3):
                        proper_nouns.append(tagged_text[i][0].lower() +
                                            " " + tagged_text[i + 1][0].lower() +
                                            " " + tagged_text[i + 2][0].lower())
                        i += 2  # extra increment added to the i counter to skip the next word
                else:
                    found_pair = [tagged_text[i][0].lower(), tagged_text[i + 1][0].lower()]
                    if find_words(all_words, found_pair, 2):
                        proper_nouns.append(tagged_text[i][0].lower() +
                                            " " + tagged_text[i + 1][0].lower())
                        i += 1
            else:
                proper_nouns.append(tagged_text[i][0].lower())
        i += 1  # increment the i counter
    return proper_nouns


def get_nouns(proper_nouns):
    """
    EX: Henry cu ponderea x, Uncle Henry cu ponderea y
    => un singur personaj: Uncle Henry cu ponderea x+y
    """
    keys = list(proper_nouns.keys())
    deleted_keys = list()
    for i in range(len(proper_nouns) - 1):
        for j in range(i + 1, len(proper_nouns)):
            nouns1 = keys[i]
            nouns2 = keys[j]
            words1 = text_tokenize(nouns1)
            words2 = text_tokenize(nouns2)
            intersection = set(words1).intersection(set(words2))
            if len(intersection) == len(words2) or len(intersection) == len(words1):
                if len(words1) < len(words2):
                    weight = proper_nouns.get(nouns1)
                    deleted_keys.append(nouns1)
                    proper_nouns[nouns2] += weight
                else:
                    weight = proper_nouns.get(nouns2)
                    deleted_keys.append(nouns2)
                    proper_nouns[nouns1] += weight
    for key in set(deleted_keys):
        del proper_nouns[key]
    return {k: v for k, v in sorted(proper_nouns.items(), key=lambda item: item[1], reverse=True)}


def summarize_text(proper_nouns, top_num):
    """
    afla cuvintele de top din lista data
    """
    counts = dict(Counter(proper_nouns).most_common(top_num))
    return counts


def get_characters(nouns):
    """
    returneaza lista de personaje principale si personaje secundare
    """
    keys = list(nouns.keys())
    highest_difference = -1
    first_index = 0
    for i in range(len(nouns) - 1):
        noun = keys[i]
        next_noun = keys[i + 1]
        difference = nouns.get(noun) - nouns.get(next_noun)
        if difference > highest_difference:
            highest_difference = difference
            first_index = i + 1
    main_characters = keys[:first_index]

    highest_difference = -1
    snd_index = 0
    for i in range(first_index, len(nouns) - 1):
        noun = keys[i]
        next_noun = keys[i + 1]
        difference = nouns.get(noun) - nouns.get(next_noun)
        if difference > highest_difference:
            highest_difference = difference
            snd_index = i + 1
    secondary_characters = keys[first_index:snd_index + 1]

    return main_characters, secondary_characters


def get_dynamic_verbs(tagged_text):
    """
    returneaza verbele de miscare din textul dat
    """
    fopen = open("stative_verbs", 'r')
    stative_words = fopen.readlines()
    dynamic_verbs = []
    for i in range(len(stative_words)):
        stative_words[i] = stative_words[i][:-1]
    for i in range(len(tagged_text)):
        if "VB" in tagged_text[i][1] and tagged_text[i][0].lower() not in stative_words:
            dynamic_verbs.append(tagged_text[i][0])
    return set(dynamic_verbs)


def get_tagged_text(text):
    """
    returneaza cuvintele insotite de taguri(VB,NNP etc)
    """
    tokens_text = elim_stopwords(text)
    tagged_text = tagging(tokens_text)
    return tagged_text
