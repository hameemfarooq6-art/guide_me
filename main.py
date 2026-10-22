
class Destination:
    def __init__(self, name, location, description):
        self.name = name
        self.location = location
        self.description = description

    def display(self):
        print(f"\nDestination: {self.name}")
        print(f"Location: {self.location}")
        print(f"Description: {self.description}")


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

print("=== Travel Explorer ===")

for destination in destinations:
    destination.display()
