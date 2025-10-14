import os

import requests
import yaml

# URL для запроса
url = "http://localhost:8000/openapi.json"

# Сделать GET запрос
response = requests.get(url)
response.raise_for_status()  # Проверка на ошибки

# Получить JSON данные из ответа
json_data = response.json()

# Конвертировать JSON в YAML
yaml_data = yaml.dump(json_data, allow_unicode=True)

# Путь для сохранения файла на уровень выше
save_path = os.path.join(os.getcwd(), "openapi.yaml")

# Записать YAML в файл
with open(save_path, "w", encoding="utf-8") as f:
    f.write(yaml_data)

print(f"YAML файл сохранён по пути: {save_path}")
