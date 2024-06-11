import json
from settings import Settings

class Stylecheck:
    def check(self, lines, settings_path): # lines[tokens[Token]], file
        settings = Settings()
        with open(settings_path, 'r', encoding='utf-8') as f:
            properties = json.loads(f.read())
        for property in properties:
            settings.execute(property, properties[property], lines)


