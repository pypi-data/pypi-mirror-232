import re
import datetime
import random


class Preprocessor:
    def __init__(self, source: str) -> None:
        self.__source = source

    def _get_random_word_from_russian_alphabet(self) -> list[str]:
        return random.choice([chr(i) for i in range(1072, 1104)])

    def _get_random_string_of_numbers(self, length: int) -> str:
        return ''.join(map(str, random.sample(range(0, 9), length)))

    def preprocess(self) -> str:
        self.__source = self.__source.replace(
            '%дата%',
            datetime.datetime.now().strftime('%d.%m.%Y')
        )

        current_date = datetime.datetime.now()
        for i in range(len(self.__source)):
            if self.__source[i:i + 6] == '%дата+' and self.__source[i + 6] != '%':
                add_days_count = ''

                for char in self.__source[i + 6:]:
                    if char == '%':
                        break
                    add_days_count += char

                incremented_date = (
                    current_date +
                    datetime.timedelta(days=int(add_days_count))
                ).strftime('%d.%m.%Y')

                self.__source = self.__source[:i] + incremented_date + \
                    self.__source[i + 7 + len(add_days_count):]

            if self.__source[i:i + 6] == '%дата-' and self.__source[i + 6] != '%':
                remove_days_count = ''

                for char in self.__source[i + 6:]:
                    if char == '%':
                        break
                    remove_days_count += char

                decremented_date = (
                    current_date -
                    datetime.timedelta(days=int(remove_days_count))
                ).strftime('%d.%m.%Y')

                self.__source = self.__source[:i] + decremented_date + \
                    self.__source[i + 7 + len(remove_days_count):]

        self.__source = self.__source.replace(
            '%арт%',
            f'{self._get_random_word_from_russian_alphabet()}-{self._get_random_string_of_numbers(5)}'
        )
        return self.__source
