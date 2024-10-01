import json

json_string = '{"product": "Kaspersky\u00A0Endpoint\u00A0Security для Windows"}'
data = json.loads(json_string)

print(data["product"])  # Выведет: Kaspersky Endpoint Security для Windows
