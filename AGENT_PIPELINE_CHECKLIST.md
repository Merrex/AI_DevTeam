# Agent Pipeline Enhancement Checklist

**Branch:** `agent-pipeline-zephyr-mistral-wizardcoder`

## Goal
Implement a modular agent pipeline:
- **Planner:** Zephyr 1.3B
- **Code Generator:** Mistral or CodeGemma
- **Refiner:** WizardCoder

---

## Checklist

- [x] Update requirements.txt with all necessary model dependencies (transformers, torch, etc.)
- [x] Implement Zephyr 1.3B loading and inference in `planner.py` (`ZephyrPlanner` class)
- [x] Refactor planner logic to use Zephyr for prompt-to-plan (integrated in orchestration)
- [x] Implement Mistral/CodeGemma loading and inference in code generation agents (`MistralBackendAgent` in `backend_agent.py`)
- [x] Refactor code generation logic to use Mistral/CodeGemma (backend agent, orchestration)
- [x] Implement WizardCoder loading and inference in `refiner_agent.py` (`WizardCoderRefiner` class)
- [x] Refactor refiner logic to use WizardCoder for code review/refinement (orchestration)
- [x] Enhance agent orchestration logic in `repo_generator.py` to use new pipeline
- [x] Integrate LLM-based agent classes for frontend, database, and integration agents (for full LLM pipeline)
- [ ] Add configuration options for model selection (local vs. HuggingFace Hub, etc.)
- [ ] Test the full pipeline with a sample prompt
- [ ] Document the new architecture and usage in `README.md`
- [ ] Remove/clean up any legacy model code
- [ ] Push changes to remote branch (in progress)

---

## Future Scope & Subtasks

### Agentic Dev Team (MVP)
- [ ] Design agent communication protocol (messages, meetings, status updates)
- [ ] Implement agent meeting scheduler and agenda system
- [ ] Enable agents to share progress, blockers, and handoffs
- [ ] Add project manager agent to coordinate Dev agents
- [ ] Implement agentic reporting (daily standups, sprint reviews)

### Agentic QA Team & SDLC/STLC
- [ ] Add QA/tester agents (unit, integration, E2E, code review)
- [ ] Implement automated test plan and test case generation
- [ ] Enable bug/issue reporting and feedback loop to Dev agents
- [ ] Integrate test execution and result aggregation
- [ ] Document full SDLC/STLC agent workflow

### Agentic Collaboration & Delivery
- [ ] Enable multi-agent chat/meeting UI (web or CLI)
- [ ] Implement agentic delivery pipeline (handoff to deployment, release notes)
- [ ] Add feedback and retrospective agent for continuous improvement

### Cursor Integration & Plugins
- [ ] Research Cursor plugin API and extension points
- [ ] Prototype agentic plugin for Cursor (code suggestions, reviews, meetings)
- [ ] Optionally, wrap full open source Cursor repo with agentic orchestration
- [ ] Document integration steps and user workflow

---

**Notes:**
- Ensure each agent is modular and can be swapped easily.
- Consider adding logging for each stage (planner, generator, refiner, QA, meetings).
- Validate output at each stage for correctness.
- Next step: Consider immediate plugin or integration with Cursor, or wrap the full Cursor repo with this agentic application.