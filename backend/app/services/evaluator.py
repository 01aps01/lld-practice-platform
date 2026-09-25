from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    strengths: list[str]
    issues: list[str]
    suggestions: list[str]
    tradeoffs: list[str]


class Evaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        problem: str,
        solution: str
    ) -> EvaluationResult:
        pass


class RuleBasedEvaluator(Evaluator):

    def evaluate(
        self,
        problem: str,
        solution: str
    ) -> EvaluationResult:

        strengths = []
        issues = []
        suggestions = []
        tradeoffs = []

        if len(solution.strip()) < 100:
            issues.append(
                "The solution is too short to demonstrate a meaningful LLD."
            )
        else:
            strengths.append(
                "The submission contains enough detail for an initial review."
            )

        if "interface" in solution.lower():
            strengths.append(
                "The solution appears to consider interfaces or abstractions."
            )
        else:
            suggestions.append(
                "Consider introducing interfaces where behavior may have multiple implementations."
            )

        if "class" not in solution.lower():
            issues.append(
                "No class definitions were detected in the submission."
            )

        suggestions.append(
            "Consider separating responsibilities so individual classes have focused responsibilities."
        )

        tradeoffs.append(
            "A simpler design may be easier to understand, while additional abstractions can improve extensibility."
        )

        return EvaluationResult(
            strengths=strengths,
            issues=issues,
            suggestions=suggestions,
            tradeoffs=tradeoffs
        )