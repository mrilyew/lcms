## Экстракторы

Экстракторы позволяют получить контент, вернув его в JSON-формате.

Экстрактор возвращает результат в формате словаря. В нём один элемент: "entities".

Если экстрактор возвращает одно Entity, массив должен содержать словарь формата:

"file" — словарь с элементами "extension", "upload_name" и "filesize".

"indexation_content" — контент, в котором будет вестись поиск.

"entity_internal_content" — JSON контент

"source" — источник

Если больше двух, то должны возвращаться Peewee-модели, и в результате создастся коллекция.
