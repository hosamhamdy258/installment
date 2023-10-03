import argparse
import re


class Translator:
    """
    Translate module in Odoo using a .po file.

    example: $ python translation.py ar_001.po

    This script simplifies the process of translating Odoo modules by performing the following steps:

    1. Extract translated and untranslated words from the specified .po file.
    2. Generate a TXT file with translatable words formatted as "original word, translated word".
       (Default value for "untranslated" is used if the word is missing in the .po file.)
    3. Generate a TXT file containing a list of untranslated words and update modified words.
       (Unmodified words are ignored and not updated in the .po file.)

    Parameters:
    - po_file (str): Path to the input .po file.

    Usage:
    - Create an instance of Translator with the path to the .po file.
    - Call the translate() method to perform translation tasks interactively.
    - Follow the on-screen instructions to generate translation files and update the .po file.
    """

    def __init__(self, po_file) -> None:
        self.po_file = po_file
        self.translated_file = "translated.txt"
        self.un_translated_file = "un_translated.txt"
        self.translated_list = []
        self.un_translated_list = []
        self.original_words = []
        self.modified_words = []

    def extract_words_from_po(self):
        original_word_pattern = 'msgid "(.*?)"'
        modified_word_pattern = 'msgstr "(.*?)"'

        with open(self.po_file, "r") as input_file:
            content = input_file.read()

            self.original_words = re.findall(original_word_pattern, content)
            self.modified_words = re.findall(modified_word_pattern, content)

            # Remove the first match in the PO file
            self.original_words.pop(0)
            self.modified_words.pop(0)

            if len(self.original_words) != len(self.modified_words):
                raise Exception("Translated and untranslated words lists must match")

    def prepare_files(self):
        self.extract_words_from_po()
        for original, modified in zip(self.original_words, self.modified_words):
            line = []
            if not original:
                original = "untranslated"
            if not modified:
                modified = "untranslated"
                self.un_translated_list.append(original)

            line.append(original)
            line.append(modified)
            self.translated_list.append(",".join(line))

    def generate_translation_file(self):
        self.file_writer(self.translated_file, self.translated_list)

    def generate_un_translation_file(self):
        if not self.un_translated_list:
            print("There's no untranslated words found in the PO file")
        self.file_writer(self.un_translated_file, self.un_translated_list)

    def file_writer(self, file, data_list, add_new_line=True):
        with open(file, "w") as output_file:
            for data in data_list:
                output_file.write(data)
                if add_new_line:
                    output_file.write("\n")

    def update_po_file(self):
        with open(self.un_translated_file, "r") as file3:
            translations = [line.strip() for line in file3]

        # Fix the first match in the PO file
        translations.insert(0, "")
        self.un_translated_list.insert(0, "")

        new_file_content = []
        with open(self.po_file, "r") as file1:
            word = 'msgstr ""'
            counter = 0
            for line in file1:
                if line.startswith(word):
                    if self.un_translated_list[counter] == translations[counter]:
                        new_file_content.append(line)
                    else:
                        new_file_content.append(f'msgstr "{translations[counter]}"\n')
                    counter += 1
                else:
                    new_file_content.append(line)
        self.file_writer(self.po_file, new_file_content, False)

    def translate(self):
        self.prepare_files()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate module in Odoo.")
    parser.add_argument("po_file", help="Path to the .po file")

    args = parser.parse_args()
    translator = Translator(args.po_file)
    translator.translate()
    choices = [
        "Enter choice from list:",
        "1 - Generate Translation Files (translated.txt and un_translated.txt)",
        "2 - Update PO file from un_translated.txt",
        "3 - Exit",
        "choice : ",
    ]
    input_text = ""
    while not input_text in ["exit", "EXIT", "Exit", "3"]:
        input_text = input("\n".join(choices))
        if input_text == "1":
            translator.generate_translation_file()
            translator.generate_un_translation_file()
            print("generated translations files done successfully exiting now ...")
            break
        elif input_text == "2":
            translator.update_po_file()
            print("updated po_file successfully exiting now ...")
            break
