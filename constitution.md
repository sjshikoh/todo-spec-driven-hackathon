# Todo Console Application – System Constitution (Phase I)

## 1. Purpose
This system is a command-line Todo application built for Hackathon II – Phase I.
Its purpose is to demonstrate strict Spec-Driven Development using Claude Code
without any manual coding by the developer.

The system must prioritize clarity, correctness, and traceability over complexity.

---

## 2. Non-Negotiable Rules

1. **No Manual Code**
   - The human developer must not write or edit implementation code.
   - All source code must be generated exclusively by Claude Code.

2. **Spec-Driven Development**
   - No code may be generated without an approved specification.
   - If behavior is incorrect, the specification must be refined and regenerated.
   - Code must never be patched manually.

3. **Phase I Scope**
   - In-memory storage only (no files, no databases).
   - Python console application only.
   - Single-user, synchronous execution.

---

## 3. Architectural Principles

- Separation of concerns:
  - CLI handling
  - Task management logic
  - Data representation
- Deterministic behavior (same input → same output)
- Simple, readable, maintainable structure
- Explicit error handling (no silent failures)

---

## 4. Data Constraints

- All tasks exist only in runtime memory.
- Application state is lost on exit.
- Each task must have a unique identifier within the session.

---

## 5. Error Handling Philosophy

- User-facing errors must be:
  - Human-readable
  - Actionable
- Invalid commands must not crash the application.
- Invalid inputs must be rejected gracefully with clear messages.

---

## 6. CLI Behavior Rules

- Commands must be explicit and predictable.
- No interactive prompts unless defined in a spec.
- Output must be consistent and formatted for readability.

---

## 7. Testing & Verification

- System correctness is verified through:
  - CLI examples in specs
  - Manual execution against defined scenarios
- No automated tests required in Phase I.

---

## 8. Claude Code Authority

Claude Code is the sole implementation agent.
It must:
- Follow this constitution
- Follow the active specification
- Refuse to invent behavior not described in specs

---

## 9. Change Control

- Changes to system behavior require:
  1. Updating the relevant spec
  2. Regenerating code via Claude Code
- No retroactive justification of code behavior is allowed.

---

## 10. Phase Boundaries

This constitution applies only to Phase I.
Future phases may extend or override rules via updated constitutions.
