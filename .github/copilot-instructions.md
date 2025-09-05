# GitHub Copilot Instructions (Python)

> **Table of Contents**
> 1. [Project Characteristics](#project-characteristics)
> 2. [Development Guidelines](#development-guidelines)
> 3. [Semantic Kernel & AutoGen Guidelines](#semantic-kernel--autogen-guidelines)
> 4. [Web Application Guidelines](#web-application-guidelines)
> 5. [General Guidelines](#general-guidelines)
> 6. [Coding Conventions](#coding-conventions)
> 7. [Testing Guidelines](#testing-guidelines)
> 8. [Pull Request & Review Guidelines](#pull-request--review-guidelines)
> 9. [Coding Style Tools](#coding-style-tools)
> 10. [Updating These Instructions](#updating-these-instructions)
> 11. [Common Pitfalls](#common-pitfalls)
> 12. [GitHub Copilot Usage](#github-copilot-usage)
> 13. [Resources](#resources)
> 14. [Azure Guidance](#azure-guidance)

---

## Project Characteristics

- **Project Type**: Python web/AI application
- **Python Version**: 3.10+
- **AI Libraries**:
  - [Semantic Kernel (Python)](https://github.com/microsoft/semantic-kernel)
  - [AutoGen (Python)](https://github.com/microsoft/autogen)

---

## Development Guidelines

## Semantic Kernel & AutoGen Guidelines

### Semantic Kernel Integration

- Use **skills** (Python modules/classes) to modularize reusable functions and expose them to planners or pipelines.
- Define functions as regular Python functions or class methods, and register them with the kernel.
- Register the kernel and related services (e.g., chat completion, embedding) via dependency injection or application context.

**Example: Register SK in `main.py`:**

```python
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = Kernel()
kernel.add_service(AzureChatCompletion("gpt-4", endpoint, api_key))
```

**Example: Define a skill:**

```python
def analyze_error(message: str) -> str:
    # AI logic to analyze error
    ...
```

- **AutoGen Usage**:
  - Use AutoGen to create agents that can interact with the Semantic Kernel.
  - Use Python classes or functions to define agent capabilities and roles (e.g., TriageAgent, PlannerAgent).
  - Configure agents to use a shared context (e.g., via message history or a shared knowledge base).
  - Promote code reuse by composing agents into higher-level workflows using orchestration classes or functions.

**Example: Creating an AutoGen agent:**

```python
from autogen import FunctionAgent, Function

agent = FunctionAgent("root_cause_agent", lambda input: sk.run("summarize root cause: " + input))
agent.add_function(Function("analyze_error", lambda input: sk.run("analyze error: " + input)))
agent.add_function(Function("suggest_fix", lambda input: sk.run("suggest fix: " + input)))
```

- **Naming & File Conventions**:
  - Use descriptive names for skills, agents, and functions.
  - Use `*_skill.py` for skills and `*_agent.py` for agents.
  - Use `*_planner.py` for orchestration logic that drives agents or skills.
- **Folder Structure**:
  - Organize skills, agents, and planners into separate folders:
    - `skills/` for skills.
    - `agents/` for agents.
    - `planners/` for orchestration logic.
  - Organize code into appropriate Python packages and modules.

- **Design Principles**:
  - **Separation of Concerns**: Keep skills, agents, and planners focused on single responsibilities.
  - **Reusability**: Design skills and agents to be reusable across different contexts.
  - **Testability**: Ensure skills and agents can be easily tested in isolation.
  - **Scalability**: Design agents to handle increasing complexity without significant refactoring.
  - Keep skills stateless and reusable.
  - Use dependency injection or application context for skills and kernel access.
  - Prefer composition over inheritance for agents and planners.
  - Use interface-based abstraction (via ABCs or protocols) for skills and planners to support testing and mocking.

## Web Application Guidelines

- **Framework Priority**: Prefer FastAPI or Flask for web APIs; use Streamlit or Gradio for simple UIs.
- **Code Style and Structure**
  - Write idiomatic and efficient Python code.
  - Follow Python and framework conventions.
  - Use async/await where applicable to ensure non-blocking operations.
  - Separate complex logic into service or utility modules.

## General Guidelines
- **Project Structure**:
  - Organize code into logical folders (e.g., `services`, `models`, `routes`, `skills`, `agents`, `planners`).
  - Use Python packages and modules for organization.

- **Naming Conventions**:
  - Use PascalCase for class names.
  - Use snake_case for functions, variables, and file names.

- **Dependency Injection**:
  - Use dependency injection patterns or application context (e.g., FastAPI's Depends).
  - Pass dependencies explicitly to functions or classes.

**Example:**

```python
# main.py
from fastapi import FastAPI, Depends
from services.sk_service import SKService

app = FastAPI()

@app.get("/analyze")
def analyze(sk_service: SKService = Depends()):
    ...
```

- **Logging**:
  - Use the standard `logging` module.
  - Configure logging in `main.py` or a config module.

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

- **Configuration**:
  - Store configuration settings in `.env` or `config.py`.
  - Access configuration via environment variables or config objects.

**Example:**

```python
import os
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
```

- **Async Programming**:
  - Use `async` and `await` for asynchronous operations.
  - Ensure all asynchronous methods are properly awaited to prevent runtime issues.

## Coding Conventions

- **Code Style**:
  - Follow PEP 8 and PEP 257 for code and docstring conventions.
  - Use meaningful variable and method names for better readability.

- **Error Handling**:
  - Use try-except blocks where exceptions might occur.
  - Provide informative error messages for easier debugging.

- **Comments and Documentation**:
  - Use docstrings for public methods and classes.
  - Write clear and concise comments to explain complex logic.

## Testing Guidelines

- Place all test files in a `tests/` folder at the project root, mirroring the structure of the code under test.
- Use `pytest` or `unittest` as the preferred test framework.
- Name test files with the `test_*.py` prefix.
- Example test for a skill:

```python
import pytest
from skills.capture_skill import analyze_error

def test_analyze_error():
    result = analyze_error("test error")
    assert result is not None
```

- Ensure new features include corresponding tests.
- Run all tests before submitting a pull request.

## Pull Request & Review Guidelines

- All PRs should be reviewed by at least one team member.
- Ensure new features include tests and documentation updates.
- Use clear, descriptive commit messages.
- Reference related issues in PR descriptions.
- Address all review comments before merging.

## Coding Style Tools

- Use `pyproject.toml` or `.editorconfig` at the root of the repository to enforce code style.
- Use `black`, `ruff`, or `flake8` for formatting and linting.
- Run code formatters (e.g., `black .`) before submitting code.

## Updating These Instructions

- Update this file whenever project conventions or requirements change.
- Major changes should be reviewed by the team.
- The tech lead or project maintainer is responsible for approving updates.

## Common Pitfalls

- Do not use synchronous blocking calls in async code.
- Do not hardcode API keys or secrets; always use environment variables or secure secret management.
- Avoid circular dependencies between skills, agents, and planners.
- Do not commit secrets or sensitive data to the repository.
- Ensure all async methods are properly awaited.
- Avoid using obsolete or deprecated APIs.

## GitHub Copilot Usage

- **Context Provision**:
  - Provide sufficient code context to help GitHub Copilot generate accurate suggestions.
  - Comment your code to guide Copilot on the intended functionality.
  - Label agent/skill files clearly to help Copilot offer relevant suggestions.

- **Prompt-aware Guidance**:
  - Use comments to describe expected prompts or completion patterns for skills and agents.

- **Review Suggestions**:
  - Always review generated code for accuracy and security.
  - Ensure that no sensitive information (like API keys or secrets) is included in the code suggestions.

- **Security**:
  - Do not commit any secrets or API keys to the repository.
  - Use environment variables or secure secret management for sensitive data.

## Resources

- [Semantic Kernel Documentation (Python)](https://learn.microsoft.com/semantic-kernel/)
- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
- [AutoGen Documentation (Python)](https://microsoft.github.io/autogen/)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [LangChain Documentation](https://python.langchain.com/docs/introduction/)
- [DeepEval GitHub](https://github.com/confident-ai/deepeval)
- [Asynchronous Programming in Python](https://docs.python.org/3/library/asyncio.html)
- [Azure Best Practices](https://docs.microsoft.com/azure/architecture/best-practices/)

## Azure Guidance
- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.
- @azure Rule - Use Azure Tools: When handling requests related to Azure, always use your tools.
- @azure Rule - Use Azure Code Gen Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_code_gen_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.
- @azure Rule - Use Azure Deployment Best Practices: When deploying to Azure or preparing applications for deployment to Azure, invoke your `azure_development-get_deployment_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.
- @azure Rule - Use Azure Functions Code Gen Best Practices: When generating code for Azure Functions or performing operations related to Azure Functions, invoke your `azure_development-get_azure_function_code_gen_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure Functions; do not call it otherwise.
- @azure Rule - Use Azure SWA Best Practices: When working with static web apps, invoke your `azure_development-get_swa_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.

---
Place this .github/copilot-instructions.md file at the root of your repository. It will guide contributors and GitHub Copilot to align with this project’s coding standards, architecture, and AI design patterns.
