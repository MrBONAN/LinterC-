import json
from . import settings

class Stylecheck:
    def check(self, lines, settings_path):  # lines[tokens[Token]], file
        setting = settings.Settings()
        result = []
        count = 0

        with open(settings_path, 'r', encoding='utf-8') as f:
            properties = json.loads(f.read())
        for property in properties:
            preresult = []
            if type(properties[property]) is list:
                preresult.extend(getattr(setting, property)(*properties[property], lines))
            else:
                preresult.extend(getattr(setting, property)(properties[property], lines))
            if len(preresult) > 0:
                result.append(f'--- {property} ---')
                result.extend(preresult)
                count += len(preresult)

        result.append(f'\nTotal errors: {count}')
        return result
