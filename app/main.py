from app.matcher import recommend_users
from app.data_loader import load_users


users = load_users()

user1 = users[0]

results = recommend_users(
    user1,
    users,
    min_score=50
)


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
        round(
            result["user1_to_user2"],
            2
        ),
        "%"
    )

    print(
        "Their learning coverage:",
        round(
            result["user2_to_user1"],
            2
        ),
        "%"
    )

    print(
        "Quality:",
        result["quality"]
    )

    print("Why this match?")

    for reason in result["reasons"]:
        print("✓", reason)