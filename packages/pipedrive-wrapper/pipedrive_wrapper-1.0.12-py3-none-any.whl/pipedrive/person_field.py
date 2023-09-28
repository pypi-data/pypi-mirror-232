from unidecode import unidecode

from .util import Util


class PersonField:
    def __init__(self, client) -> None:
        self.client = client
        self._util = Util()

    def get_all_person_fields(self):
        url_context = "/personFields"

        return self.client.get(url_context)

    def populate_person_fields(self, person):
        person_fields = self.get_all_person_fields()
        custom_fields = []

        for key, value in person.items():
            for person_field in person_fields:
                if person_field.get("key") == key:
                    if person_field.get("options"):
                        for option in person_field.get("options"):
                            if option.get("id") == value:
                                custom_fields.append({self.__snake_case(person_field.get("name")): option.get("value")})
                    else:
                        custom_fields.append({self.__snake_case(person_field.get("name")): value})

        for custom_field in custom_fields:
            person.update(custom_field)

        return person

    def __remove_accent_marks(self, text):
        return unidecode(text)

    def __snake_case(self, text):
        # Remover acentos e caracteres especiais
        text = self.__remove_accent_marks(text)

        # Substituir espaços por underscores
        text = text.replace(" ", "_")

        # Remover caracteres especiais e manter apenas letras, números e underscores
        text = "".join(filter(lambda char: char.isalnum() or char == "_", text))

        # Converter para letras minúsculas
        text = text.lower()

        return text
