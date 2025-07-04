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
- [ ] Add configuration options for model selection (local vs. HuggingFace Hub, etc.)
- [ ] Integrate LLM-based agent classes for frontend, database, and integration agents (optional, for full LLM pipeline)
- [ ] Test the full pipeline with a sample prompt
- [ ] Document the new architecture and usage in `README.md`
- [ ] Remove/clean up any legacy model code
- [ ] Push changes to remote branch (in progress)

---

## Future Scope
- Wrap this pipeline into a full agentic software that acts as a Dev team (agents hold meetings, share updates, and collaborate to deliver the final product)
- Add a QA team (agentic testers) and cover the full SDLC (Software Development Life Cycle) and STLC (Software Testing Life Cycle)
- Enable agentic meetings, status updates, and collaborative workflows among agents
- (Later) Integrate with or wrap the open source Cursor repo, or make a plugin to connect this agentic system with Cursor for seamless codebase management and agentic development

---

**Notes:**
- Ensure each agent is modular and can be swapped easily.
- Consider adding logging for each stage (planner, generator, refiner).
- Validate output at each stage for correctness.
- Next step: Consider immediate plugin or integration with Cursor, or wrap the full Cursor repo with this agentic application. 