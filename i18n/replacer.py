po_file = "ar_001.po"
translated_words = "translated.txt"

with open(translated_words, "r") as file3:
    translations = [line.strip() for line in file3]
    # added to fix first match in po file
    translations.insert(0, "")


new_file_content = []
with open(po_file, "r") as file1:
    word = 'msgstr "'
    counter = 0
    for line in file1:
        if line.startswith(word):
            new_line = f'{word}{translations[counter]}"\n'
            counter += 1
            new_file_content.append(new_line)
            continue
        new_file_content.append(line)
with open(po_file, "w") as file1:
    for line in new_file_content:
        file1.write(line)
