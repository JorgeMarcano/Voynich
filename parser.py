from bookTypes import *

def getMatching(line, character, start=0):
    index = -1
    try:
        index = line[start:].index(character) + start
    except ValueError:
        index = -1

    return index

def setup(filename=None):
    if filename == None:
        # Get filename
        filename = input("Filename [ZL3a-n[.txt]] > ")
        if len(filename) == 0:
            filename = "ZL3a-n"
        if '.' not in filename:
            filename += ".txt"

    # Read all the lines and immediately close the file
    all_lines = []
    with open(filename, 'r') as file:
        all_lines = file.readlines()

    # Create book
    book = Book()

    curr_page = None
    curr_paragraph = None
    curr_line = None
    curr_word = None
    # Go through each line
    for line_nb, text_line_unstripped in enumerate(all_lines):
        # Get rid of whitespaces, tabs, newlines(shouldn't have any anyways)
        text_line = text_line_unstripped.strip()

        # If the line is empty, skip
        if len(text_line) == 0:
            continue
        # If the line is a comment, skip
        if text_line[0] == '#':
            # Optional debug lines to know what page we are at
    ##        if ("# page" in text_line):
    ##            print(text_line)
            continue
        # If line doesn't begin with '<', something is wrong
        # Warn and ignore
        if text_line[0] != '<':
            print(f"ERROR with line {line_nb}: \"{text_line}\"")
            continue

        # Get matching closing bracket
        index = getMatching(text_line, '>')
        # If couldn't find or if another bracket is opened before closing, wrong
        if index == -1 or ('<' in text_line[1:index]):
            print(f"ERROR with line {line_nb}: \"{text_line}\"")
            continue

        locus = text_line[1:index]
        locus = locus.split(',')
        # Check to see if there is no paragraph info
        if len(locus) == 1:
            # This is a new page, get relevant info
            locus = locus[0]
            # If locus doesn't start with f or end with v or r, something wrong
            if locus[0] != 'f':
                print(f"ERROR with locus in line {line_nb}: {locus}")
                input("Press enter to quit")
                exit()

            # Get folio and rectoVerso
            rectoVerso = 'x'
            folio = -1
            # Special Case ! (Not happy with this tbf)
            if (locus == "fRos"):
                folio = "Ros"
                rectoVerso = 'x'
            elif not (locus[-1] == 'r' or locus[-1] == 'v'):
                # Might be a foldout
                if not (locus[-2] == 'r' or locus[-2] == 'v'):
                    print(f"ERROR with locus in line {line_nb}: {locus}")
                    input("Press enter to quit")
                    exit()

                rectoVerso = locus[-2:]
                folio = int(locus[1:-2])
            else:
                rectoVerso = locus[-1]
                folio = int(locus[1:-1])

            # Get optional extra info, look for next '<'
            image = None
            language = None
            hand_1 = None
            hand_2 = None
            extra = None
            extra_index = getMatching(text_line, '<', index)
            if (extra_index != -1) and text_line[extra_index+1] == '!':
                extra_close = getMatching(text_line, '>', extra_index)
                if (extra_close == -1):
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                    input("Press enter to quit")
                    exit()
                extra_section = text_line[extra_index+2 : extra_close].strip().split(' ')

                # TODO: currently ignore Q P F and B since it is all paging info
                for info in extra_section:
                    match info[:2]:
                        case "$I":
                            image = info[-1]
                        case "$L":
                            language = info[-1]
                        case "$H":
                            hand_1 = info[-1]
                        case "$C":
                            hand_2 = info[-1]
                        case "$X":
                            extra = info[-1]

            # Create page and add to book
            curr_page = Page(book.getLen(), None, image, language, hand_1, hand_2, extra, folio, rectoVerso, text_line)
            book.addPage(curr_page)

            # If the page ended, then curr paragraph was last one of previous page
            if curr_paragraph != None:
                curr_paragraph.isPageEnd = True

            # Done parsing the line, move to the next line
            continue
            
        # If it is not a new page, must be a new line
        # Must get line info from locus
        position = locus[0].split('.')
        if len(position) != 2:
            # Something is wrong
            print(f"ERROR with locus in line {line_nb}: {locus}")
            input("Press enter to quit")
            exit()

        # make sure proper formatting of locus
        if position[0][0] != 'f':
            print(f"ERROR with locus in line {line_nb}: {locus}")
            input("Press enter to quit")
            exit()

        folio = -1
        rectoVerso = 'x'
        # Special Case ! (Not happy with this tbf)
        if (position[0] == "fRos"):
            folio = "Ros"
            rectoVerso = 'x'
        elif not (position[0][-1] == 'r' or position[0][-1] == 'v'):
            # Might be a foldout
            if not (position[0][-2] == 'r' or position[0][-2] == 'v'):
                print(f"ERROR with locus in line {line_nb}: {locus}")
                input("Press enter to quit")
                exit()

            rectoVerso = position[0][-2:]
            folio = int(position[0][1:-2])
        else:
            rectoVerso = position[0][-1]
            folio = int(position[0][1:-1])

        # Make sure this matches current page info
        if (curr_page.folio != folio or curr_page.rectoVerso != rectoVerso):
            print(f"ERROR inconsistent locus in line {line_nb}: {locus}")
            input("Press enter to quit")
            exit()

        # line_nb is reduced by one to make is ZERO-indexed
        line_nb = int(position[1]) - 1

        # Get line style information
        info = locus[1]
        relation = info[0]
        style = info[1]
        subStyle = info[2]

        # Lazy way of checking for this
        isParaStart = "<%>" in text_line
        isParaEnd = "<$>" in text_line

        # Create Line with info
        curr_line = Line(line_nb, None, style, subStyle, relation, isParaStart, isParaEnd)

        # if stand-alone, not a paragraph
        if (style != "P"):
            # It is a paragraph start
            isFirst = (curr_page.getLen() == 0)
            curr_paragraph = Paragraph(curr_page.getLen(), None, style, subStyle, isFirst, False)
            curr_page.addParagraph(curr_paragraph)
            curr_line.isParagraphBegin = True
            curr_line.isParagraphEnd = True

        # Isolate the actual text part
        char_line = text_line[index+1:].strip()

        # Line always starts with new word
        curr_word = Word(0, None, False, True, False)
        curr_line.addWord(curr_word)
        curr_char = None
        # Must go through each character
        str_ind = 0
        curr_strikethrough = False
        curr_alt = -1
        alt_ind = -1
        while (str_ind < len(char_line)):
            # Deal with special cases
            if (char_line[str_ind] == '<'):
                matching = getMatching(char_line, '>', str_ind+1)
                if (matching == -1) or ('<' in char_line[str_ind+1:matching]):
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                    input("Press enter to quit")
                    exit()

                cmd = char_line[str_ind+1 : matching]
                if (cmd[0] == '!'):
                    # It is a comment, skip and ignore (FIXME?)
                    pass
                elif (cmd == "%"):
                    # It is a paragraph start
                    isFirst = (curr_page.getLen() == 0)
                    curr_paragraph = Paragraph(curr_page.getLen(), None, style, subStyle, isFirst, False)
                    curr_page.addParagraph(curr_paragraph)
                elif (cmd == "$"):
                    # It is a paragraph end, nothing really to do
                    pass
                elif (cmd == "-"):
                    # It is an interruption by image, will be counted as a space
                    if curr_char != None:
                        curr_char.isLast = True
                    curr_word = Word(curr_line.getLen(), None, True, False, False)
                    curr_char = Character(0, '-', False, False, True, False)
                    curr_word.addChar(curr_char)
                    curr_line.addWord(curr_word)
                    curr_char = None
                    # Immediately start next word
                    curr_word = Word(curr_line.getLen(), None, False, False, False)
                    curr_line.addWord(curr_word)

                elif (cmd == "~"):
                    # It is an askew interruption by image, will be counted as a space
                    if curr_char != None:
                        curr_char.isLast = True
                    curr_word = Word(curr_line.getLen(), None, True, False, False)
                    curr_char = Character(0, '~', False, False, True, False)
                    curr_word.addChar(curr_char)
                    curr_line.addWord(curr_word)
                    curr_char = None
                    # Immediately start next word
                    curr_word = Word(curr_line.getLen(), None, False, False, False)
                    curr_line.addWord(curr_word)

                str_ind = matching+1
                continue

            # Deal with strikethrough
            if char_line[str_ind] == '{':
                if curr_strikethrough:
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                curr_strikethrough = True
                str_ind += 1
                continue
            if char_line[str_ind] == '}':
                if not curr_strikethrough:
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                curr_strikethrough = False
                str_ind += 1
                continue

            # Deal with spaces
            if char_line[str_ind] == '.' or char_line[str_ind] == ',':
                # It is an askew interruption by image, will be counted as a space
                if curr_char != None:
                    curr_char.isLast = True
                curr_word = Word(curr_line.getLen(), None, True, False, False)
                curr_char = Character(0, char_line[str_ind], False, False, True, False)
                curr_word.addChar(curr_char)
                curr_line.addWord(curr_word)
                curr_char = None
                # Immediately start next word
                curr_word = Word(curr_line.getLen(), None, False, False, False)
                curr_line.addWord(curr_word)
                
                str_ind += 1
                continue

            # Deal with multiple readings
            if char_line[str_ind] == '[':
                matching = getMatching(char_line, ']', str_ind+1)
                if (matching == -1) or (':' not in char_line[str_ind+1:matching]):
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                    input("Press enter to quit")
                    exit()

                # ASSUMPTION: No spaces appear within [], all within word
    ##            alt_ind = curr_word.startAlt()

                curr_alt = getMatching(char_line, ':', str_ind+1) + 1

                str_ind += 1
                continue

            if char_line[str_ind] == ':' and curr_alt != -1:# and char_line[curr_alt] == "]":
    ##            # Reached end of alternative readings
    ##            str_ind = curr_alt+1
                curr_alt = -1
                matching = getMatching(char_line, ']', str_ind+1)
                str_ind = matching + 1
                continue

            value = char_line[str_ind]
    ##        # Deal with alt being longer than this one
    ##        if char_line[str_ind] == ':' and curr_alt != -1:
    ##            value = '*'
    ##
    ##            # Will have +1 added at the end, to ensure it stays here until alt is done
    ##            str_ind -= 1
                
            # Deal with special characters
            if char_line[str_ind] == '@':
                matching = getMatching(char_line, ';', str_ind+1)
                if (matching == -1) or (len(char_line[str_ind+1:matching]) != 3):
                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
                    input("Press enter to quit")
                    exit()
                value = chr(int(char_line[str_ind+1:matching]))

                # Will have the +1 added at the end
                str_ind = matching
            
            # Deal with regular character
            isFirst = (curr_word.getLen() == 0)
            curr_char = Character(curr_word.getLen(), value, isFirst, False, False, curr_strikethrough)
            curr_word.addChar(curr_char)

            str_ind += 1

            # If there is an alternative reading to deal with
    ##        if curr_alt != -1:
    ##            value = char_line[curr_alt]
    ##            # Deal with size difference
    ##            if 
    ##            # Deal with special characters
    ##            if char_line[str_ind] == '@':
    ##                matching = getMatching(char_line, ';', str_ind+1)
    ##                if (matching == -1) or (len(char_line[str_ind+1:matching]) != 3):
    ##                    print(f"ERROR with line {line_nb}: \"{text_line}\"")
    ##                    input("Press enter to quit")
    ##                    exit()
    ##                value = chr(int(char_line[str_ind+1:matching]))
    ##
    ##                # Will have the +1 added at the end
    ##                str_ind = matching
    ##            
    ##            # Deal with regular character
    ##            isFirst = (curr_word.getLen() == 0)
    ##            curr_char = Character(curr_word.getLen(), char_line[str_ind], isFirst, False, curr_strikethrough)
    ##            curr_word.addChar(curr_char)
                


        # If line ended, last word processed is last word of the line
        curr_word.isLineEnd = True
        # Once done processing line, add to current paragraph
        curr_paragraph.addLine(curr_line)

    return book

if __name__ == "__main__":
    book = setup()
