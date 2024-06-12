import json
from settings import Settings


class Stylecheck:
    def check(self, lines, settings_path):  # lines[tokens[Token]], file
        settings = Settings()
        result = []
        with open(settings_path, 'r', encoding='utf-8') as f:
            properties = json.loads(f.read())
        for property in properties:
            result.append(f'--- {property} ---')
            if type(properties[property]) is list:
                result.extend(getattr(settings, property)(*properties[property], lines))
            else:
                result.extend(getattr(settings, property)(properties[property], lines))
        return result
