import json
user = {"id": None, "name": None, "weight": None, "age": None, "exp": None,
        "goal": None, "choice": None, "gender": None, "pos": None}

with open('text.txt', "w") as file:
    json.dump(user, file)

