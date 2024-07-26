import json
from . import settings


class Stylecheck:
    def check(self, lines, settings_path):
        setting = settings.Settings()
        result = ['####################################################',
                  '                 CHECKING THE STYLE                 ',
                  '####################################################']
        result.extend(self._check_style(lines, settings_path))

        result += ['####################################################',
                   '               ADDITIONAL INFORMATION               ',
                   '####################################################']
        result.extend(setting.checking_for_errors(lines))
        result.extend(setting.analyze_code(lines))
        return result

    def _check_style(self, lines, settings_path):
        setting = settings.Settings()
        count = 0
        result = []
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
        result.extend(['', f'Total errors: {count}'])
        return result
