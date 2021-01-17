import sys
import textwrap
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import procces


def read_text(file):
    lines = open(file).read().split('\n')
    return ' '.join(lines)


def print_to_file(file, text):
    text = "\n".join(textwrap.wrap(text, 80))
    open(file, "w").write(text)


def get_summary(text, percent, freqTable):
    """
    rezumatul general al unui text in functie de procent:
    scorul propozitiilor este dat de suma frecventelor cuvintelor componente.
    """
    # Creating a dictionary to keep the score
    # of each sentence
    sentences = sent_tokenize(text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    average = int(sumValues / len(sentenceValue))

    sorted_sentences = {k: v for k, v in sorted(sentenceValue.items(), key=lambda item: item[1], reverse=True)}
    count_sentences = int(len(sorted_sentences) * percent / 100)
    key_sentence = list(sorted_sentences.keys())[count_sentences]
    min_value = sorted_sentences.get(key_sentence)

    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > min_value):
            summary += " " + sentence

    print_to_file("summary", summary)


def get_actions_character(character, text):
    """
       clasificarea actiunilor unui personaj dat
    """
    context = get_concordance_words(text, character)
    tagged_text = procces.get_tagged_text(text)
    verbs = procces.get_dynamic_verbs(tagged_text)
    freq = {}
    for item in context:
        if item in freq:
            freq[item] += 1
        else:
            freq[item] = 1
    actions_character = {}
    for key, value in freq.items():
        if key.lower() in verbs:
            actions_character[key] = value
    return {k: v for k, v in sorted(actions_character.items(), key=lambda item: item[1], reverse=True)}


def get_concordance_words(text, target_word):
    """
       returneaza contextul pentru un anumit cuvant
    """
    context_list = nltk.text.ConcordanceIndex(procces.elim_stopwords(text)).find_concordance(target_word)
    words = []
    for context in context_list:
        words += context.left
        words += context.right
    return words


def get_sentences_value(text, target_word, freqTable, include=False):
    """
      calculeaza scorul propozitiilor pe baza urmatoarei euristici:
      - cuvintele egale cu target-word primesc cel mai mare scor
      - cuvintele din contextul lui target-word primesc un scor relativ mare
      - restul cuvintelor: numarul de aparitii
    """
    sentences = sent_tokenize(text)
    sentence_value = dict()
    context = get_concordance_words(text, target_word)
    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    score = 0
                    if word.lower() in target_word.lower():
                        score = 1000
                    elif word in context:
                        score = 500
                    else:
                        score = freq
                    if include == False:
                        score *= (-1)
                    sentence_value[sentence] += score
                else:
                    sentence_value[sentence] = 0
    return sentences, sentence_value


def get_summary_character(text, character, percent, freqTable, include=True):
    """
        rezumatul unui text in functie de personaj( prin includerea sau excluderea acestuia):
    """
    sentences, sentenceValue = get_sentences_value(text, character, freqTable, include)
    sorted_sentences = {k: v for k, v in sorted(sentenceValue.items(), key=lambda item: item[1], reverse=True)}
    count_sentences = int(len(sorted_sentences) * percent / 100)
    key_sentence = list(sorted_sentences.keys())[count_sentences]
    min_value = sorted_sentences.get(key_sentence)

    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > min_value):
            summary += " " + sentence
    print_to_file("summary", summary)


def main(args):
    file = input("File name: ")
    text = read_text(file)
    tagged_text = procces.get_tagged_text(text)
    # Tokenizing the text
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Creating a frequency table to keep the
    # score of each word
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    if args[1] == "summary":
        if args[2] == "general":
            percent = int(input("Percent: "))
            get_summary(text, percent, freqTable)
            print("You can find the summary in the file with the same name")
        elif args[2] == "character":
            include = input("Include character?(False/True)")

            if include == "False":
                include = False
            else:
                include = True
            name = input("Character's name: ")

            tags = procces.find_proper_nouns(tagged_text, words)
            nouns = procces.summarize_text(tags, 100)
            main_charac, secondary_charac = procces.get_characters(procces.get_nouns(nouns))
            characters = main_charac + secondary_charac

            # print(characters)
            if name.lower() in characters:
                character_importance = characters.index(name.lower()) + 1
                if include:
                    percent = 50 - character_importance * 5
                else:
                    percent = 10 + character_importance * 5
            else:
                percent = 20

            print(percent)
            get_summary_character(text, name, percent, freqTable, include)
            print("You can find the summary in the file with the same name")
        else:
            chosed_action = False
            while not chosed_action:
                action = input("Action(Write help to get a list of available actions): ")
                if action == "help":
                    print(procces.get_dynamic_verbs(tagged_text))
                else:
                    chosed_action = True
                    get_summary_character(text, action, 15, freqTable, True)
                    print("You can find the summary in the file with the same name")
    elif args[1] == "get_characters":
        tags = procces.find_proper_nouns(tagged_text, words)
        nouns = procces.summarize_text(tags, 100)
        main_charac, secondary_charac = procces.get_characters(procces.get_nouns(nouns))
        print("Main characters:", main_charac)
        print("Secondary characters:", secondary_charac)
    elif args[1] == "get_actions_character":
        name = input("Character's name: ")
        print(get_actions_character(name, text))


if __name__ == '__main__':
    main(sys.argv)
# get_summary(text, 30)
# get_summary_character(text, "snow-white", 30, False)
