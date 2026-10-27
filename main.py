
class Destination:
    def __init__(self, name, location, description):
        self.name = name
        self.location = location
        self.description = description
        self.reviews = []

    def add_review(self, tourist, comment, rating, picture=""):
        if not 1 <= rating <= 5:
            print("Rating must be between 1 and 5.")
            return

        self.reviews.append({
            "tourist": tourist,
            "comment": comment,
            "rating": rating,
            "picture": picture
        })
        print("Review added successfully!")

    def average_rating(self):
        if not self.reviews:
            return 0

        total = sum(review["rating"] for review in self.reviews)
        return total / len(self.reviews)

    def display(self):
        print(f"\nDestination: {self.name}")
        print(f"Location: {self.location}")
        print(f"Description: {self.description}")

        if self.reviews:
            print(f"Average Rating: {self.average_rating():.1f}/5")
            print("Tourist Reviews:")

            for review in self.reviews:
                print(f"  Tourist: {review['tourist']}")
                print(f"  Rating: {review['rating']}/5")
                print(f"  Comment: {review['comment']}")

                if review["picture"]:
                    print(f"  Picture: {review['picture']}")
        else:
            print("No reviews yet.")


def search_destination(destinations, keyword):
    results = [
        destination for destination in destinations
        if keyword.lower() in destination.name.lower()
        or keyword.lower() in destination.location.lower()
    ]

    if results:
        for destination in results:
            destination.display()
    else:
        print("No matching destinations found.")


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
    5,
    "pictures/dal_lake.jpg"
)

destinations[1].add_review(
    "Rahul",
    "Amazing mountain views.",
    4,
    "pictures/gulmarg.jpg"
)

print("\n=== Travel Explorer & Review System ===")
print("1. View all destinations")
print("2. Search destinations")
print("3. Exit")

while True:
    choice = input("\nEnter your choice: ")

    if choice == "1":
        for destination in destinations:
            destination.display()

    elif choice == "2":
        keyword = input("Enter destination name or location: ")
        search_destination(destinations, keyword)

    elif choice == "3":
        print("Thank you for using Travel Explorer!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
