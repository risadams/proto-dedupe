
# Implementation Plan: Tarball Deduplication System

**Branch**: `001-python-application-to` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `A:\dedupe\specs\001-python-application-to\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, or `AGENTS.md` for all other agents).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Automated tarball deduplication system that processes nightly log archives, calculates SHA256 checksums for file contents, and maintains a PostgreSQL database to track duplicates across servers and time periods. Enables system administrators to identify and manage duplicate files efficiently.

## Technical Context
**Language/Version**: Python 3.12 or later  
**Primary Dependencies**: psycopg2 (PostgreSQL driver), tarfile (built-in), hashlib (built-in), argparse (CLI)  
**Storage**: PostgreSQL database for metadata, file system for tarball processing  
**Testing**: pytest with coverage>=90% requirement  
**Target Platform**: RHEL8 server (air-gapped environment)
**Project Type**: single - command-line application  
**Performance Goals**: Process multi-GB tarballs without excessive memory usage, <2s for duplicate queries  
**Constraints**: Air-gapped environment, memory-efficient processing, robust error handling  
**Scale/Scope**: Thousands of files per tarball, multiple servers, historical tracking

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Code Quality Standards: Static analysis configured, linting rules defined, complexity thresholds set
- [x] Test-First Development: TDD workflow planned, test coverage targets >=90% defined
- [x] User Experience Consistency: CLI design patterns documented, clear error messages planned
- [x] Performance Requirements: Performance targets defined (<2s complex queries, memory-efficient processing)
- [x] Development Workflow: Spec-driven process planned, CI/CD gates configured
- [x] Quality Assurance: Automated testing strategy covers functional, integration, performance, security

## Project Structure

### Documentation (this feature)
```
specs/001-python-application-to/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── dedupe/
│   ├── models/          # Database models and entities
│   ├── services/        # Business logic for tarball processing
│   ├── cli/            # Command-line interface
│   └── utils/          # Utility functions for hashing, file operations
├── config/
│   └── database.py     # Database configuration
└── main.py             # Application entry point

tests/
├── contract/           # Database schema and API contract tests
├── integration/        # End-to-end workflow tests
└── unit/              # Unit tests for individual components

sql/
├── schema.sql         # Database schema definitions
└── migrations/        # Database migration scripts

requirements.txt       # Python dependencies
setup.py              # Package configuration
```

**Structure Decision**: Single project layout chosen for command-line application. Structure supports modular design with clear separation between models, services, CLI, and utilities. Database schema managed separately for PostgreSQL.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (database schema, CLI interface, data model, quickstart)
- Database schema contract → schema creation and migration test tasks [P]
- CLI interface contract → command-line argument and output format test tasks [P]
- Each entity (TarballRecord, FileRecord, DuplicateGroup, ProcessingLog) → model creation task [P]
- Each CLI command (process, query, cleanup) → implementation and integration test tasks
- Quickstart scenarios → end-to-end integration test tasks

**Ordering Strategy**:
- TDD order: Database tests → Model tests → Service tests → CLI tests → Integration tests
- Dependency order: Database schema → Models → Services → CLI → Integration
- Mark [P] for parallel execution (independent components like different models)
- Sequential for dependent layers (models depend on schema, services depend on models)

**Specific Task Categories Planned**:
1. **Setup**: Project structure, dependencies (pytest, psycopg2, black, flake8)
2. **Database Tests [P]**: Schema validation, constraint testing, index performance
3. **Model Tests [P]**: Entity creation, validation, relationship testing
4. **Service Tests [P]**: Tarball processing, duplicate detection, database operations
5. **CLI Tests**: Argument parsing, command execution, output formatting
6. **Integration Tests**: End-to-end workflows from quickstart scenarios
7. **Performance Tests**: Memory usage, processing speed, query performance

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md with clear dependencies

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No constitutional violations identified. All principles align with the planned approach:
- Code Quality: Python linting and type checking planned
- Test-First: TDD workflow with >=90% coverage requirement
- User Experience: CLI with clear error messages and progress feedback
- Performance: Memory-efficient processing with <2s query performance targets

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
