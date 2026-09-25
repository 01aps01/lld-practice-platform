from app.services.llm_evaluator import LLMEvaluator


evaluator = LLMEvaluator()

result = evaluator.evaluate(
    problem="""
    Design a Parking Lot system supporting
    multiple floors, vehicle types, parking spots,
    ticket generation and fee calculation.
    """,

    solution="""
    class ParkingLot {
        List<ParkingFloor> floors;

        void parkVehicle(Vehicle vehicle) {
        }
    }

    interface FeeCalculator {
        double calculateFee(Ticket ticket);
    }

    class ParkingSpot {
        Vehicle vehicle;
    }
    """
)

print("STRENGTHS:")
print(result.strengths)

print("\nISSUES:")
print(result.issues)

print("\nSUGGESTIONS:")
print(result.suggestions)

print("\nTRADEOFFS:")
print(result.tradeoffs)