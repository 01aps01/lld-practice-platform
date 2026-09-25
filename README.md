# LLD Practice Platform

A focused practice platform that helps learners practice Low-Level
Design problems, submit solutions, receive explainable feedback,
and review previous attempts.

## Features

- LLD problem library
- Practice workspace
- Solution submission
- Deterministic validation
- AI-powered LLD feedback
- Explainable feedback
- Attempt history
- Evaluation retry
- SQLite persistence

## Tech Stack

### Frontend
- React
- Vite
- React Router

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

### AI
- Google Gemini API

## Architecture

```text
React
  |
  v
FastAPI
  |
  +---- Problems
  |
  +---- Attempts
  |
  +---- EvaluationService
              |
              +---- RuleBasedEvaluator
              |
              +---- LLMEvaluator
                         |
                         v
                    Gemini API