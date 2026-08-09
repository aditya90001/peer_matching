import json


def load_users():

    with open("data/user.json", "r") as file:
        users = json.load(file)

    return users


def load_subjects():

    with open("data/subjects.json", "r") as file:
        subjects = json.load(file)

    return subjects