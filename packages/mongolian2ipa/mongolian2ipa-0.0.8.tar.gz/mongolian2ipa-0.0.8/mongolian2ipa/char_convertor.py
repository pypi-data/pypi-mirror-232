from mongolian2ipa.helpers import check_male_female_word, WordGender, vowels, check_first_level_vowel


# Characters functions
def a_convert(word: str, index: int) -> str:
    """
    а letter
    :param word:
    :param index:
    :return:
    """

    if not index == 0:
        if word[index - 1] in ['а', 'у', 'я']:
            return ''

    text = word[index:]

    is_ai = 'й' == text[1] if len(text) > 1 else False
    if is_ai:
        return 'æː'

    is_aa = 'а' == text[1] if len(text) > 1 else False

    # 'и', 'ь', 'ий'
    is_i = 'и' == text[2] if len(text) > 2 else False
    is_soft = 'ь' == text[2] if len(text) > 2 else False

    if is_aa:
        is_aa_i = 'и' == text[3] if len(text) > 3 else False
        is_aa_soft = 'ь' == text[3] if len(text) > 3 else False

        if is_aa_i or is_aa_soft:
            return 'æː'
        else:
            return 'aː'

    if not check_first_level_vowel(word, index):
        return 'ə'

    if is_i or is_soft:
        return 'æ'

    return 'a'


def w_convert(word: str, index: int) -> str:
    """
     В letter
    :param word:
    :param index:
    :return:
    """

    if len(word) > index + 1:
        next_char = word[index + 1]

        if next_char == 'т' or next_char == 'ц' or next_char == 'ч':
            return 'ɸ'

    return 'w'


def g_convert(word: str, index: int) -> str:
    """
     Г letter
    :param word:
    :param index:
    :return:
    """

    gender = check_male_female_word(word)

    if gender == WordGender.MALE:
        if len(word) == index + 1:
            return 'k'

        if len(word) > index + 1:
            if word[index + 1] in 'сш':
                return 'k'

        # гүй
        if len(word) > index + 2:
            if word[index + 1] == 'ү' and word[index + 2] == 'й':
                return 'k'

        if len(word) > index + 1:
            if word[index + 1] in vowels:
                return 'q'

    return 'k'


def o_convert(word: str, index: int) -> str:
    """
    О letter
    :param word:
    :param index:
    :return:
    """
    if not index == 0:
        if word[index - 1] in ['о', 'ё']:
            return ''

    text = word[index:]

    is_ai = 'й' == text[1] if len(text) > 1 else False
    if is_ai:
        return 'œː'

    is_oo = 'о' == text[1] if len(text) > 1 else False

    if is_oo:
        # Check if the substring contains 'и', 'ь', or 'ий'
        is_i = 'и' == text[3] if len(text) > 3 else False
        is_soft = 'ь' == text[3] if len(text) > 3 else False

        if is_i or is_soft:
            return 'œː'
        else:
            return 'ɔː'
    else:
        if not check_first_level_vowel(word, index):
            return 'ə'

        is_i = 'и' == text[2] if len(text) > 2 else False
        is_soft = 'ь' == text[2] if len(text) > 2 else False

        if is_i or is_soft:
            return 'œ'

    return 'ɔ'


def ou_convert(word: str, index: int) -> str:
    """
    Ө letter
    :param word:
    :param index:
    :return:
    """
    if not index == 0:
        if word[index - 1] in ['ө', 'е']:
            return ''

    text = word[index:]

    is_ui = 'ө' == text[1] if len(text) > 1 else False
    if is_ui:
        return 'өː'

    if not check_first_level_vowel(word, index):
        return 'ə'

    return 'ө'


def u_convert(word: str, index: int) -> str:
    """
    У letter
    :param word:
    :param index:
    :return:
    """

    if not index == 0:
        if word[index - 1] in ['у', 'ю']:
            return ''

    text = word[index:]

    is_ui = 'й' == text[1] if len(text) > 1 else False
    if is_ui:
        return 'oi'

    is_ua = 'а' == text[1] if len(text) > 1 else False
    if is_ua:
        is_uai = 'й' == text[2] if len(text) > 2 else False

        if is_uai:
            return 'wæː'

        return 'waː'

    is_uu = 'у' == text[1] if len(text) > 1 else False

    if is_uu:
        # Check if the substring contains 'и', 'ь', or 'ий'
        is_i = 'и' == text[3] if len(text) > 3 else False
        is_soft = 'ь' == text[3] if len(text) > 3 else False

        if is_i or is_soft:
            return 'ʏː'
        else:
            return 'oː'
    else:
        # Check if the substring contains 'и', 'ь', or 'ий'
        is_i = 'и' == text[2] if len(text) > 2 else False
        is_soft = 'ь' == text[2] if len(text) > 2 else False

        if is_i or is_soft:
            return 'ʏ'

    return 'o'


def oo_convert(word: str, index: int) -> str:
    """
    Ү letter
    :param word:
    :param index:
    :return:
    """

    if not index == 0:
        if word[index - 1] == 'ү':
            return ''

    text = word[index:]

    is_ooi = 'й' == text[1] if len(text) > 1 else False
    if is_ooi:
        return 'ui'

    is_oooo = 'ү' == text[1] if len(text) > 1 else False

    if is_oooo:
        return 'uː'

    return 'u'


def h_convert(word: str, index: int) -> str:
    """
    Х letter
    :param word:
    :param index:
    :return:
    """
    if not index == 0:
        if word[index - 1] == 'л':
            return ''

    gender = check_male_female_word(word)

    if gender == WordGender.MALE:
        if len(word) > index + 1:
            if not word[index + 1] in ['т', 'ц', 'ч']:
                return 'χ'
        else:
            return 'χ'

    return 'x'


def e_convert(word: str, index: int) -> str:
    """
    Э letter
    :param word:
    :param index:
    :return:
    """

    if not index == 0:
        if word[index - 1] in ['э', 'е']:
            return ''

    text = word[index:]

    is_ei = 'й' == text[1] if len(text) > 1 else False
    if is_ei:
        return 'eː'

    is_ee = 'э' == text[1] if len(text) > 1 else False
    if is_ee:
        return 'eː'

    if not check_first_level_vowel(word, index):
        return 'ə'

    return 'e'


def yu_convert(word: str, index: int) -> str:
    """
    Ю letter
    :param index:
    :param word:
    :return:
    """

    gender = check_male_female_word(word)

    if len(word) > index + 1:
        if not word[index + 1] in ['у', 'ү']:
            return 'jo'

    if gender == WordGender.MALE:
        return 'joː'
    else:
        return 'juː'


def ye_convert(word: str, index: int) -> str:
    """
    Е letter
    :param word:
    :param index:
    :return:
    """
    text = word[index]
    length = len(text)

    if check_first_level_vowel(word, index):
        if len(word) > index + 1:
            if index == 0 and word[index + 1] == 'э':
                return 'jeː'

            if word[index + 1] == 'ө':
                return 'jөː'

            if len(word) > index + 2:
                if word[index + 2] == 'ө':
                    return 'jө'

            if not word[index + 1] in vowels:
                return 'je'

            if not word[index + 1] == 'э':
                return 'jeː'
            else:
                return 'je'

    if len(word) > index + 1:
        if word[index + 1] == 'ө':
            return 'jөː'

    return 'jə'


def ya_convert(word: str, index: int) -> str:
    """
    Я letter
    :param word:
    :param index:
    :return:
    """

    if check_first_level_vowel(word, index):
        if len(word) > index + 2:
            if word[2] in ['ь', 'й']:
                return 'jæ'

        if len(word) > index + 1:
            if word[1] in ['й']:
                return 'jæː'

            if not word[index + 1] in vowels:
                return 'ja'
            else:
                return 'jaː'

    return 'jə'


def yo_convert(word: str, index: int) -> str:
    """
    Ё letter
    :param word:
    :param index:
    :return:
    """

    if check_first_level_vowel(word, index):
        if len(word) > index + 1:
            if 'ь' in word or 'й' in word or 'и' in word:
                return 'jœ'

            if not word[index + 1] in vowels:
                return 'jɔ'

            if word[index + 1] == 'о':
                return 'jɔː'


def i_convert(word: str, index: int) -> str:
    """
    И letter
    :param word:
    :param index:
    :return:
    """
    text = word[index:]
    length = len(text)

    if not check_first_level_vowel(word, index):
        return 'ə'

    if length > 2 and index + 1 < length and text[1] == 'й':
        return 'iː'
    else:
        return 'i'


def l_convert(word: str, index: int) -> str:
    """
    Л letter
    :param word:
    :param index:
    :return:
    """
    text = word[index:]
    length = len(text)

    if length > 2 and index + 1 < length and text[1] == 'х':
        return 'ɬʰ'

    return 'ɬ'


def n_convert(word: str, index: int) -> str:
    """
    Н letter
    :param word:
    :param index:
    :return:
    """
    text = word[index:]
    length = len(text)

    if length > 2 and index + 1 < length and text[1] in 'хгсш':
        return 'ŋ'

    if len(word) - 1 == index:
        return 'ŋ'
    else:
        return 'n'
