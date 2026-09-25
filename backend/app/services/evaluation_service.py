from app.services.evaluator import (
    EvaluationResult,
    RuleBasedEvaluator
)

from app.services.llm_evaluator import (
    LLMEvaluator
)


class EvaluationService:

    def __init__(self):
        self.rule_evaluator = RuleBasedEvaluator()
        self.llm_evaluator = LLMEvaluator()

    def evaluate(
        self,
        problem: str,
        solution: str
    ) -> EvaluationResult:

        rule_result = self.rule_evaluator.evaluate(
            problem,
            solution
        )

        llm_result = self.llm_evaluator.evaluate(
            problem,
            solution
        )

        return EvaluationResult(
            strengths=(
                rule_result.strengths
                + llm_result.strengths
            ),

            issues=(
                rule_result.issues
                + llm_result.issues
            ),

            suggestions=(
                rule_result.suggestions
                + llm_result.suggestions
            ),

            tradeoffs=(
                rule_result.tradeoffs
                + llm_result.tradeoffs
            )
        )