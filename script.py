# This is not a particular script, just working on stuff
from bookTypes import *
from parser import setup

# This looks through an entire book and prints each line that contains the search word
def getLineWithWord(book, searchWord):
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    if word == searchWord:
                        print(line.print(True, page.folio, page.rectoVerso))

# Gets all words with character
def getWordWithChar(book, searchChar):
    ret_words = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    if searchChar in word.chars:
                        if word not in ret_words:
                            ret_words.append(word.copy())

    return ret_words

# Gets all words with syllable (subword)
def getWordWithSyl(book, subWord):
    ret_words = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    if word.contains(subWord):
                        if word not in ret_words:
                            ret_words.append(word.copy())

    return ret_words

# Gets a copy of every word that has a certain length
def getWordOfLen(book, length, ignoreNonWords=False, ignoreDuplicates=False):
    ret_words = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    if len(word.chars) == length:
                        if ignoreNonWords and word.isNonWord:
                            continue

                        if ignoreDuplicates:
                            isDuplicate = False
                            for foundWord in ret_words:
                                if word == foundWord:
                                    isDuplicate = True
                                    break

                            if isDuplicate:
                                continue

                        ret_words.append(word.copy())

    return ret_words

# Gets all characters that are only finals
def getCharLast(book, ignoreIsolates=False):
    all_chars = []
    middle_chars = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    for char in word.chars:
                        if char not in all_chars:
                            all_chars.append(char.copy())

                        if not char.isLast:
                            if char not in middle_chars:
                                middle_chars.append(char.copy())

                        if ignoreIsolates:
                            if char.isLast and char.isFirst:
                                if char not in middle_chars:
                                    middle_chars.append(char.copy())

    ret_chars = []
    for char in all_chars:
        if char not in middle_chars:
            ret_chars.append(char)

    return ret_chars

# Gets all characters that are only initials
def getCharFirst(book, ignoreIsolates=False):
    all_chars = []
    middle_chars = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    for char in word.chars:
                        if char not in all_chars:
                            all_chars.append(char.copy())

                        if not char.isFirst:
                            if char not in middle_chars:
                                middle_chars.append(char.copy())
                                

                        if ignoreIsolates:
                            if char.isLast and char.isFirst:
                                if char not in middle_chars:
                                    middle_chars.append(char.copy())

    ret_chars = []
    for char in all_chars:
        if char not in middle_chars:
            ret_chars.append(char)

    return ret_chars

# Gets all characters that are only isolates
def getCharIsolates(book):
    all_chars = []
    middle_chars = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    for char in word.chars:
                        if char not in all_chars:
                            all_chars.append(char.copy())

                        if not char.isFirst or not char.isLast:
                            if char not in middle_chars:
                                middle_chars.append(char.copy())

    ret_chars = []
    for char in all_chars:
        if char not in middle_chars:
            ret_chars.append(char)

    return ret_chars

# Gets all characters that are only isolates
def getCharMiddles(book):
    all_chars = []
    middle_chars = []
    for page in book.pages:
        for para in page.paragraphs:
            for line in para.lines:
                for word in line.words:
                    for char in word.chars:
                        if char not in all_chars:
                            all_chars.append(char.copy())

                        if char.isFirst or char.isLast:
                            if char not in middle_chars:
                                middle_chars.append(char.copy())

    ret_chars = []
    for char in all_chars:
        if char not in middle_chars:
            ret_chars.append(char)

    return ret_chars

# Gets the word count of certain pages, given in list of tuples [(folio, RV),()]
def getFilteredWordCount(book, pages):
    counts = {}
    for page in book.pages:
        combo = (page.folio, page.rectoVerso)
        if combo in pages:
            mergeCounts(counts, page.getWordCount())

    return counts

book = setup("ZL3a-n.txt")
