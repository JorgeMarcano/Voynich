def mergeCounts(a, b):
    for key in b:
        if key not in a:
            a[key] = b[key]
        else:
            a[key] += b[key]

class Character():
    def __init__(self, index=-1, value=None, isFirst=False, isLast=False, isSpace=False, isStrikethrough=False):
        self.setup(index, value, isFirst, isLast, isSpace, isStrikethrough)

    def setup(self, index=-1, value=None, isFirst=False, isLast=False, isSpace=False, isStrikethrough=False):
        self.value = value
        self.index = index
        self.isFirst = isFirst
        self.isLast = isLast
        self.isSpace = isSpace
        self.isStrikethrough = isStrikethrough

    def isUnknown(self):
        return (self.value == '?')

    def __eq__(self, other):
        if other == None:
            return False
        
        if self.value != other.value:
            return False
        if self.isSpace != other.isSpace:
            return False
        if self.isStrikethrough != other.isStrikethrough:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return Character(self.index, self.value, self.isFirst, self.isLast, self.isSpace, self.isStrikethrough)
    
    def print(self, ignoreStrike=False):
        print_str = self.value

        if self.value == "-" or self.value == "~":
            print_str = "<"+self.value+">"

        if ord(self.value) >= 128:
            print_str = f"@{ord(self.value)};"

        if not ignoreStrike:
            if self.isStrikethrough:
                print_str = '{' + print_str + '}'

        return print_str

class Word():
    def __init__(self, index=-1, chars=None, isNonWord=False, isLineBegin=False, isLineEnd=False, altChars=None):
        self.setup(index, chars, isNonWord, isLineBegin, isLineEnd, altChars)

    def setup(self, index=-1, chars=None, isNonWord=False, isLineBegin=False, isLineEnd=False, altChars=None):
        self.chars = [] if (chars == None) else chars
        self.altChars = {} if (altChars == None) else altChars
        self.isNonWord = isNonWord
        self.isLineBegin = isLineBegin
        self.isLineEnd = isLineEnd
        self.index = index

    def addChar(self, newChar):
        self.chars.append(newChar)

    def getLen(self):
        return len(self.chars)

    def hasAlt(self):
        return (len(self.altChars) != 0)

    def startAlt(self, index=-1):
        true_ind = index
        if index == -1:
            true_ind = self.getLen()

        self.altChars[true_ind] = []

        return true_ind

    def addAltChar(self, newChar, altIndex):
        self.altChars[altIndex].append(newChar)

    def __eq__(self, other):
        if len(self.chars) != len(other.chars):
            return False
        
        for index in range(len(self.chars)):
            if self.chars[index] != other.chars[index]:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def contains(self, subWord):
        if len(subWord.chars) > len(self.chars):
            return False

        for i in range(len(self.chars) - len(subWord.chars) + 1):
            j = 0
            isMatch = (self.chars[i+j] == subWord.chars[j])
            while isMatch:
                j += 1
                if j == len(subWord.chars):
                    return True
                isMatch = (self.chars[i+j] == subWord.chars[j])

        return False

    def print(self):
        print_str = ""

        isStrike = False
        for char in self.chars:
            if (char.isStrikethrough) and (not isStrike):
                isStrike = True
                print_str += "{"
            elif (not char.isStrikethrough) and (isStrike):
                isStrike = False
                print_str += "}"
                
            print_str += char.print(ignoreStrike=True)

        if isStrike:
            print_str += "}"

        return print_str

    def getCharCount(self):
        counts = {}
        for char in self.chars:
            if char.value not in counts:
                counts[char.value] = 1
            else:
                counts[char.value] += 1

        return counts

    def copy(self, deep=True):
        new_chars = self.chars if not deep else [char.copy() for char in self.chars]
        return Word(self.index, new_chars, self.isNonWord, self.isLineBegin, self.isLineEnd, self.altChars)

class Line():
    def __init__(self, index=-1, words=None, style=None, subStyle=None, relationWithPrev=None, isParagraphBegin=False, isParagraphEnd=False):
        self.setup(index, words, style, subStyle, relationWithPrev, isParagraphBegin, isParagraphEnd)

    def setup(self, index=-1, words=None, style=None, subStyle=None, relationWithPrev=None, isParagraphBegin=False, isParagraphEnd=False):
        self.words = [] if (words == None) else words
        self.index = index
        self.style = style
        self.subStyle = subStyle
        self.relationWithPrev = relationWithPrev
        self.isParagraphBegin = isParagraphBegin
        self.isParagraphEnd = isParagraphEnd

    def addWord(self, newWord):
        self.words.append(newWord)

    def getLen(self):
        return len(self.words)

    def print(self, includeLocus=False, folio='x', RV='x'):
        print_str = ""
        if includeLocus:
            # TODO
            print_str += f"<f{folio}{RV}.{self.index+1},{self.relationWithPrev}{self.style}{self.subStyle}>\t"

        for word in self.words:
            print_str += word.print()

        return print_str

    def getCharCount(self):
        counts = {}
        for word in self.words:
            mergeCounts(counts, word.getCharCount())

        return counts

    def getWordCount(self):
        counts = {}
        for word in self.words:
            if word.print() not in counts:
                counts[word.print()] = 1
            else:
                counts[word.print()] += 1

        return counts

class Paragraph():
    def __init__(self, index=-1, lines=None, style=None, subStyle=None, isPageBegin=False, isPageEnd=False):
        self.setup(index, lines, style, subStyle, isPageBegin, isPageEnd)

    def setup(self, index=-1, lines=None, style=None, subStyle=None, isPageBegin=False, isPageEnd=False):
        self.lines = [] if (lines == None) else lines
        self.index= index
        self.style = style
        self.subStyle = subStyle
        self.isPageBegin = isPageBegin
        self.isPageEnd = isPageEnd

    def addLine(self, newLine):
        self.lines.append(newLine)

    def getLen(self):
        return len(self.lines)

    def print(self, includeLocus=False):
        print_str = ""

        for line in self.lines:
            print_str += line.print(includeLocus) + '\n'

        return print_str

    def getCharCount(self):
        counts = {}
        for line in self.lines:
            mergeCounts(counts, line.getCharCount())

        return counts

    def getWordCount(self):
        counts = {}
        for line in self.lines:
            mergeCounts(counts, line.getWordCount())

        return counts

class Page():
    def __init__(self, index=-1, paragraphs=None, image=None, language=None, hand_1=None, hand_2=None, extra=None, folio=-1, rectoVerso=None, unParsed=None):
        self.setup(index, paragraphs, image, language, hand_1, hand_2, extra, folio, rectoVerso, unParsed)

    def setup(self, index=-1, paragraphs=None, image=None, language=None, hand_1=None, hand_2=None, extra=None, folio=-1, rectoVerso=None, unParsed=None):
        self.paragraphs = [] if (paragraphs == None) else paragraphs
        self.index = index
        self.image = image
        self.language = language
        self.hand_1 = hand_1
        self.hand_2 = hand_2
        self.extra = extra
        self.folio = folio
        self.rectoVerso = rectoVerso
        self.unParsed = unParsed

    def addParagraph(self, newParagraph):
        self.paragraphs.append(newParagraph)

    def getLen(self):
        return len(self.paragraphs)

    def print(self, includeLocus=False):
        print_str = ""

        for paragraph in self.paragraphs:
            print_str += paragraph.print(includeLocus)
            print_str += "#\n"

        return print_str

    def getCharCount(self):
        counts = {}
        for paragraph in self.paragraphs:
            mergeCounts(counts, paragraph.getCharCount())

        return counts

    def getWordCount(self):
        counts = {}
        for paragraph in self.paragraphs:
            mergeCounts(counts, paragraph.getWordCount())

        return counts

class Book():
    def __init__(self, pages=None):
        self.pages = [] if (pages == None) else pages

    def addPage(self, newPage):
        self.pages.append(newPage)

    def getCategory(self, category):
        pageSet = []
        for page in self.pages:
            if page.category == category:
                pageSet.append(page)

        return pageSet

    def getLen(self):
        return len(self.pages)

    def getCharCount(self):
        counts = {}
        for page in self.pages:
            mergeCounts(counts, page.getCharCount())

        return counts

    def getWordCount(self):
        counts = {}
        for page in self.pages:
            mergeCounts(counts, page.getWordCount())

        return counts
