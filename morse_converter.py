class MorseConverter:

    special_chars = ['.', ',', '?', ' ']

    alphabet_to_morse = {'a':'.-', 'b':'-...', 'c':'-.-.', 'd':'-..', 'e':'.', 'f':'..-.', 'g':'--.', 'h':'....', \
                     'i': '..', 'j':'.---', 'k':'-.-', 'l':'.-..', 'm':'--', 'n':'-.', 'o':'---', 'p':'.--.', \
                     'q': '--.-', 'r': '.-.', 's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', \
                     'x': '-..-', 'y': '-.--', 'z': '--..', '0': '-----', '1': '.----', '2': '..---', \
                     '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', \
                     '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', ' ': '*'}

    @staticmethod
    def _textToMorse(text):
        morse = ''
        text = text.lower()
        if not MorseConverter._isText(text):
            print('Error: Text input must include alphabet or numbers or punctuation marks or a question mark.')
            return '-'
        for i in range(len(text)):
            morse += MorseConverter.alphabet_to_morse[text[i]]
            if text[i] == ' ' or i == (len(text)-1):
                continue
            morse += '*'
        return morse

    @staticmethod
    def _morseToText(morse):
        if not MorseConverter._isMorse(morse):
            return "Error: Invalid morse code"
        morse_array = morse.split('*')
        text_array = [None] * len(morse_array)

        for code in morse_array:
            if code not in MorseConverter.alphabet_to_morse.values() and code != '':
                return 'Error: Invalid Morse Code'

        for i in range(len(morse_array)):
            if morse_array[i] == '':
                morse_array[i] = '*'
            text_array[i] = [text for text, morse in MorseConverter.alphabet_to_morse.items() if morse == morse_array[i]][0]

        return ''.join(text_array)

    @staticmethod
    def _isMorse(morse):
        for char in set(morse):
            if char == '.' or char == '-' or char == '*':
                continue
            else:
                return False
        return True

    @staticmethod
    def _isText(text):
        for char in set(text):
            if (not char.isalnum()) and (char not in MorseConverter.special_chars):
                return False
        return True
