import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.evaluator import (
    Evaluator,
    EvaluationResult
)


load_dotenv()


class LLMEvaluator(Evaluator):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        # We can try another model if one is temporarily unavailable.
        self.models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash"
        ]

    def evaluate(
        self,
        problem: str,
        solution: str
    ) -> EvaluationResult:

        prompt = f"""
You are an expert Low-Level Design interviewer.

Evaluate the learner's LLD solution.

PROBLEM:

{problem}

LEARNER SOLUTION:

{solution}

Evaluate the solution based on:

1. Responsibility distribution
2. SOLID principles
3. Coupling and cohesion
4. Abstraction and interfaces
5. Extensibility
6. Appropriate design patterns
7. Missing requirements
8. Potential design problems
9. Trade-offs

Important:

- There can be multiple valid LLD solutions.
- Do not assume there is only one correct architecture.
- Give concrete and actionable feedback.
- Do not judge the learner personally.
- Explain WHY something could be improved.
- Only identify missing requirements that are explicitly mentioned
  in the problem.
- Do not invent requirements.
- Do not recommend design patterns just for the sake of using them.

Return JSON with exactly these fields:

{{
    "strengths": ["..."],
    "issues": ["..."],
    "suggestions": ["..."],
    "tradeoffs": ["..."]
}}
"""

        last_error = None

        # Try models one by one.
        for model in self.models:

            try:
                print(f"Trying model: {model}")

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    )
                )

                data = json.loads(response.text)

                return EvaluationResult(
                    strengths=data.get(
                        "strengths",
                        []
                    ),
                    issues=data.get(
                        "issues",
                        []
                    ),
                    suggestions=data.get(
                        "suggestions",
                        []
                    ),
                    tradeoffs=data.get(
                        "tradeoffs",
                        []
                    )
                )

            except Exception as error:

                print(
                    f"Model {model} failed: {error}"
                )

                last_error = error

                # Small delay before trying another model.
                time.sleep(1)

        # All models failed.
        raise RuntimeError(
            f"All Gemini models failed: {last_error}"
        )