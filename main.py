
class Destination:
    def __init__(self, name, location, description):
        self.name = name
        self.location = location
        self.description = description
        self.reviews = []

    def add_review(self, tourist, comment, rating):
        if not 1 <= rating <= 5:
            print("Rating must be between 1 and 5.")
            return

        self.reviews.append({
            "tourist": tourist,
            "comment": comment,
            "rating": rating
        })
        print("Review added successfully!")

    def display(self):
        print(f"\nDestination: {self.name}")
        print(f"Location: {self.location}")
        print(f"Description: {self.description}")

        if self.reviews:
            print("Tourist Reviews:")
            for review in self.reviews:
                print(f"  Tourist: {review['tourist']}")
                print(f"  Rating: {review['rating']}/5")
                print(f"  Comment: {review['comment']}")
        else:
            print("No reviews yet.")


destinations = [
    Destination(
        "Dal Lake",
        "Srinagar, Kashmir",
        "A beautiful lake famous for houseboats."
    ),
    Destination(
        "Gulmarg",
        "Baramulla, Kashmir",
        "A scenic destination famous for mountains."
    )
]

destinations[0].add_review(
    "Ayesha",
    "Beautiful scenery and a peaceful experience.",
    5
)

destinations[1].add_review(
    "Rahul",
    "Amazing mountain views.",
    4
)

print("\n=== Travel Explorer & Review System ===")

for destination in destinations:
    destination.display()

