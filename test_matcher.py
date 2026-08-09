import json


def calculate_match(user1, user2):

    user1_strengths = set(user1["strengths"])
    user1_weaknesses = set(user1["weaknesses"])

    user2_strengths = set(user2["strengths"])
    user2_weaknesses = set(user2["weaknesses"])

    # User 1 ki weakness jo User 2 ki strength hai
    user1_can_learn = user1_weaknesses & user2_strengths

    # User 2 ki weakness jo User 1 ki strength hai
    user2_can_learn = user2_weaknesses & user1_strengths

    # User 1 kitna User 2 se seekh sakta hai
    if len(user1_weaknesses) > 0:
        user1_to_user2 = (
            len(user1_can_learn) /
            len(user1_weaknesses)
        ) * 100
    else:
        user1_to_user2 = 0

    # User 2 kitna User 1 se seekh sakta hai
    if len(user2_weaknesses) > 0:
        user2_to_user1 = (
            len(user2_can_learn) /
            len(user2_weaknesses)
        ) * 100
    else:
        user2_to_user1 = 0

    # Two-way average
    final_score = (
        user1_to_user2 +
        user2_to_user1
    ) / 2

    return {
        "score": final_score,
        "user1_to_user2": user1_to_user2,
        "user2_to_user1": user2_to_user1,
        "user1_can_learn": list(user1_can_learn),
        "user2_can_learn": list(user2_can_learn)
    }


def get_match_quality(score):

    if score >= 90:
        return "Excellent Match"

    elif score >= 75:
        return "Very Good Match"

    elif score >= 50:
        return "Good Match"

    else:
        return "Weak Match"


def generate_reason(match):

    reasons = []

    if match["user1_can_learn"]:
        skills = ", ".join(match["user1_can_learn"])

        reasons.append(
            f"They can help you with: {skills}"
        )

    if match["user2_can_learn"]:
        skills = ", ".join(match["user2_can_learn"])

        reasons.append(
            f"You can help them with: {skills}"
        )

    return reasons


# Load users
with open("data/user.json", "r") as file:
    users = json.load(file)


MIN_MATCH_SCORE = 50

# Currently testing with first user
user1 = users[0]

results = []


# Compare user1 with every other user
for user in users:

    # Don't compare user with themselves
    if user["id"] == user1["id"]:
        continue

    match = calculate_match(user1, user)

    score = match["score"]

    # Ignore weak matches
    if score < MIN_MATCH_SCORE:
        continue

    quality = get_match_quality(score)

    reasons = generate_reason(match)

    results.append({
        "name": user["name"],
        "score": score,

        "quality": quality,
        "reasons": reasons,

        "user1_to_user2": match["user1_to_user2"],
        "user2_to_user1": match["user2_to_user1"],

        "user1_can_learn": match["user1_can_learn"],
        "user2_can_learn": match["user2_can_learn"]
    })


# Highest score first
results.sort(
    key=lambda x: x["score"],
    reverse=True
)


# Display results
for result in results:

    print("\n----------------------")

    print(
        result["name"],
        "->",
        round(result["score"], 2),
        "%"
    )

    print(
        "You can learn:",
        result["user1_can_learn"]
    )

    print(
        "You can teach:",
        result["user2_can_learn"]
    )

    print(
        "Your learning coverage:",
        round(result["user1_to_user2"], 2),
        "%"
    )

    print(
        "Their learning coverage:",
        round(result["user2_to_user1"], 2),
        "%"
    )

    print(
        "Quality:",
        result["quality"]
    )

    print("Why this match?")

    for reason in result["reasons"]:
        print("✓", reason)