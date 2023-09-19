import re

po_file = "ar_001.po"
un_translated = "words.txt"
translated_words = "translated.txt"


original_word_pattern = 'msgid "(.*?)"'
modified_word_pattern = 'msgstr "(.*?)"'

with open(po_file, "r") as input_file:
    content = input_file.read()

    original_word_matches = re.findall(original_word_pattern, content)
    modified_word_matches = re.findall(modified_word_pattern, content)
    # added to ignore first match in po file
    original_word_matches.pop(0)
    modified_word_matches.pop(0)
with open(un_translated, "w") as output_file:
    for match in original_word_matches:
        if match == "":
            output_file.write("untranslated" + "\n")
            continue
        output_file.write(match + "\n")
with open(translated_words, "w") as temp_file:
    for match in modified_word_matches:
        temp_file.write(match + "\n")
