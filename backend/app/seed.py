import json

from app.database import Base, SessionLocal, engine
from app.models.database_models import ProblemModel


def seed_problems():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        if db.query(ProblemModel).count() > 0:
            print("Problems already exist.")
            return

        problems = [
            ProblemModel(
                title="Parking Lot",
                description=(
                    "Design a parking lot system that supports multiple "
                    "floors, different vehicle types, parking spots, "
                    "ticket generation, and fee calculation."
                ),
                requirements=json.dumps([
                    "Support multiple floors",
                    "Support different vehicle types",
                    "Support different parking spot types",
                    "Assign an appropriate parking spot",
                    "Generate a parking ticket",
                    "Calculate parking fees",
                    "Handle vehicle entry and exit"
                ])
            ),

            ProblemModel(
                title="Vending Machine",
                description=(
                    "Design a vending machine that allows users to select "
                    "products, insert money, purchase products, and receive "
                    "change."
                ),
                requirements=json.dumps([
                    "Display available products",
                    "Allow product selection",
                    "Accept coins and notes",
                    "Validate payment",
                    "Dispense products",
                    "Return change",
                    "Handle insufficient payment",
                    "Handle out-of-stock products"
                ])
            ),

            ProblemModel(
                title="Elevator System",
                description=(
                    "Design an elevator system for a building with multiple "
                    "floors and elevators. The system should receive requests "
                    "and decide which elevator should handle them."
                ),
                requirements=json.dumps([
                    "Support multiple elevators",
                    "Support multiple floors",
                    "Accept elevator requests",
                    "Accept floor selection",
                    "Move elevators between floors",
                    "Track elevator state",
                    "Assign elevators to requests"
                ])
            )
        ]

        db.add_all(problems)
        db.commit()

        print("Problems seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_problems()