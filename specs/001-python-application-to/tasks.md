# Tasks: Tarball Deduplication System

**Input**: Design documents from `A:\dedupe\specs\001-python-application-to\`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Python 3.12+, psycopg2, PostgreSQL, CLI structure
2. Load design documents:
   → data-model.md: Extract entities → TarballRecord, FileRecord, DuplicateGroup, ProcessingLog
   → contracts/: Database schema, CLI interface → contract test tasks
   → research.md: Air-gapped deployment, memory-efficient processing
   → quickstart.md: Integration scenarios → end-to-end test tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, processing, logging
   → Polish: unit tests, performance, docs
4. Applied task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Numbered tasks sequentially (T001-T035)
6. Generated dependency graph
7. Created parallel execution examples
8. Validated task completeness:
   → All contracts have tests ✓
   → All entities have models ✓
   → All CLI commands implemented ✓
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths based on plan.md structure: src/dedupe/, tests/, sql/

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan in src/dedupe/, tests/, sql/ directories
- [ ] T002 Initialize Python 3.12+ project with requirements.txt (psycopg2-binary, pytest, black, flake8, mypy)
- [ ] T003 [P] Configure linting and formatting tools (black, flake8, mypy) with pyproject.toml
- [ ] T004 [P] Create setup.py and package configuration for dedupe-tarball CLI

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T005 [P] Contract test database schema creation in tests/contract/test_database_schema.py
- [ ] T006 [P] Contract test CLI process command interface in tests/contract/test_cli_process.py
- [ ] T007 [P] Contract test CLI query command interface in tests/contract/test_cli_query.py
- [ ] T008 [P] Contract test CLI cleanup command interface in tests/contract/test_cli_cleanup.py

### Model Tests
- [ ] T009 [P] Unit test TarballRecord model in tests/unit/test_tarball_record.py
- [ ] T010 [P] Unit test FileRecord model in tests/unit/test_file_record.py
- [ ] T011 [P] Unit test DuplicateGroup model in tests/unit/test_duplicate_group.py
- [ ] T012 [P] Unit test ProcessingLog model in tests/unit/test_processing_log.py

### Integration Tests (from quickstart scenarios)
- [ ] T013 [P] Integration test single tarball processing in tests/integration/test_process_single_tarball.py
- [ ] T014 [P] Integration test duplicate detection across tarballs in tests/integration/test_duplicate_detection.py
- [ ] T015 [P] Integration test query duplicate files in tests/integration/test_query_duplicates.py
- [ ] T016 [P] Integration test space savings report in tests/integration/test_space_savings.py
- [ ] T017 [P] Integration test dry-run analysis in tests/integration/test_dry_run.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Layer
- [ ] T018 Create database schema SQL files in sql/schema.sql and sql/migrations/
- [ ] T019 [P] TarballRecord model implementation in src/dedupe/models/tarball_record.py
- [ ] T020 [P] FileRecord model implementation in src/dedupe/models/file_record.py
- [ ] T021 [P] DuplicateGroup model implementation in src/dedupe/models/duplicate_group.py
- [ ] T022 [P] ProcessingLog model implementation in src/dedupe/models/processing_log.py
- [ ] T023 Database connection and session management in src/dedupe/config/database.py

### Service Layer
- [ ] T024 [P] Tarball extraction service in src/dedupe/services/tarball_service.py
- [ ] T025 [P] File hashing service in src/dedupe/services/hash_service.py
- [ ] T026 [P] Duplicate detection service in src/dedupe/services/duplicate_service.py
- [ ] T027 Database operations service in src/dedupe/services/database_service.py

### CLI Interface
- [ ] T028 CLI argument parser and main entry point in src/dedupe/cli/main.py
- [ ] T029 Process command implementation in src/dedupe/cli/process_command.py
- [ ] T030 Query command implementation in src/dedupe/cli/query_command.py
- [ ] T031 Cleanup command implementation in src/dedupe/cli/cleanup_command.py

## Phase 3.4: Integration
- [ ] T032 Configuration file handling (TOML) in src/dedupe/config/settings.py
- [ ] T033 Logging system setup in src/dedupe/utils/logger.py
- [ ] T034 Error handling and recovery in src/dedupe/utils/error_handler.py
- [ ] T035 Progress reporting utilities in src/dedupe/utils/progress.py

## Phase 3.5: Polish
- [ ] T036 [P] Performance test memory usage in tests/performance/test_memory_usage.py
- [ ] T037 [P] Performance test large tarball processing in tests/performance/test_large_files.py
- [ ] T038 [P] Performance test query response times in tests/performance/test_query_performance.py
- [ ] T039 [P] Update CLI help documentation and usage examples
- [ ] T040 [P] Create deployment documentation for air-gapped environments
- [ ] T041 Run final integration tests and validate acceptance criteria

## Dependencies
- Setup (T001-T004) before all other phases
- Contract tests (T005-T008) before model tests
- Model tests (T009-T012) before integration tests (T013-T017)
- All tests (T005-T017) before implementation (T018-T035)
- Database layer (T018-T023) before service layer (T024-T027)
- Service layer (T024-T027) before CLI layer (T028-T031)
- Core implementation (T018-T031) before integration (T032-T035)
- All implementation before polish (T036-T041)

## Parallel Example
```
# Phase 3.2 Contract Tests - can launch together:
Task: "Contract test database schema creation in tests/contract/test_database_schema.py"
Task: "Contract test CLI process command interface in tests/contract/test_cli_process.py"
Task: "Contract test CLI query command interface in tests/contract/test_cli_query.py"
Task: "Contract test CLI cleanup command interface in tests/contract/test_cli_cleanup.py"
```

```
# Phase 3.3 Model Implementation - can launch together:
Task: "TarballRecord model implementation in src/dedupe/models/tarball_record.py"
Task: "FileRecord model implementation in src/dedupe/models/file_record.py"
Task: "DuplicateGroup model implementation in src/dedupe/models/duplicate_group.py"
Task: "ProcessingLog model implementation in src/dedupe/models/processing_log.py"
```

```
# Phase 3.3 Service Layer - can launch together:
Task: "Tarball extraction service in src/dedupe/services/tarball_service.py"
Task: "File hashing service in src/dedupe/services/hash_service.py"
Task: "Duplicate detection service in src/dedupe/services/duplicate_service.py"
```

## Notes
- [P] tasks = different files, no dependencies between them
- Verify tests fail before implementing (TDD requirement)
- Commit after each task completion
- All tasks include specific file paths for clarity
- Memory-efficient processing requirement applies to T024, T025
- Air-gapped deployment considerations in T002, T040

## Task Generation Rules Applied

1. **From Contracts**:
   - Database schema contract → T005 schema test, T018 schema implementation
   - CLI interface contract → T006-T008 CLI tests, T028-T031 CLI implementation
   
2. **From Data Model**:
   - Each entity → model test + implementation: T009-T012, T019-T022
   - Database relationships → T023 connection management, T027 database service
   
3. **From Quickstart Scenarios**:
   - Each scenario → integration test: T013-T017
   - Performance requirements → T036-T038 performance tests

4. **From Research Decisions**:
   - Air-gapped environment → T002 dependency management, T040 deployment docs
   - Memory efficiency → T024, T025 service implementations
   - Error handling → T034 error utilities

## Validation Checklist
*GATE: Verified before task list completion*

- [x] All contracts have corresponding tests (database schema, CLI interface)
- [x] All entities have model tasks (TarballRecord, FileRecord, DuplicateGroup, ProcessingLog)
- [x] All quickstart scenarios have integration tests
- [x] All tests come before implementation (TDD enforced)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Constitutional requirements addressed (quality, testing, performance)