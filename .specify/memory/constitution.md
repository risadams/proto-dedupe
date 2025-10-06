<!--
SYNC IMPACT REPORT
Version change: TEMPLATE → 1.0.0 (MINOR: Initial constitution establishment)
Modified principles: All new principles created
Added sections:
- Core Principles: Code Quality Standards, Test-First Development, User Experience Consistency, Performance Requirements
- Development Workflow: Spec-driven development process requirements
- Quality Assurance: Automated testing and quality metrics requirements
- Governance: Constitutional compliance and amendment procedures
Removed sections: Template placeholders removed
Templates requiring updates:
✅ Updated: .specify/templates/plan-template.md (Constitution Check section + version reference)
✅ Validated: .specify/templates/tasks-template.md (already enforces TDD principle)
✅ Validated: .specify/templates/spec-template.md (supports testing scenarios)
⚠️ Pending: No commands/ directory found to validate
Follow-up TODOs: None - all placeholders replaced with concrete values
-->

# Dedupe Constitution

## Core Principles

### I. Code Quality Standards (NON-NEGOTIABLE)

All code MUST meet documented quality standards before merge. Code MUST be linted,
formatted consistently, and free of security vulnerabilities. Static analysis tools
MUST pass. No dead code, magic numbers, or hardcoded values permitted. Clear naming
conventions MUST be followed. Complexity metrics MUST stay within defined thresholds.

### II. Test-First Development (NON-NEGOTIABLE)

TDD methodology is mandatory: Tests written → User approved → Tests fail → Then implement.
Red-Green-Refactor cycle strictly enforced. Every feature MUST have unit tests achieving
>=90% coverage. Integration tests MUST cover all user workflows. All tests MUST pass
before merge. No implementation without corresponding test validation.

### III. User Experience Consistency

User interfaces MUST maintain consistent design patterns, terminology, and interaction
flows across all features. Error messages MUST be clear, actionable, and consistent in
tone. Loading states, empty states, and error states MUST be explicitly designed.
Accessibility standards (WCAG 2.1 AA) MUST be met. User testing feedback MUST be
incorporated before feature completion.

### IV. Performance Requirements

Performance targets MUST be defined and measured for all user-facing features.
Response times MUST be <200ms for interactive operations, <2s for complex queries.
Memory usage MUST stay within defined limits. Performance tests MUST be automated
and run in CI. Performance regressions block feature deployment. Monitoring and
alerting MUST track performance metrics in production.

## Development Workflow

All changes MUST follow the spec-driven development process: specification → planning →
implementation → validation. Features MUST be developed incrementally with regular
validation checkpoints. Code reviews MUST verify constitutional compliance. Continuous
integration MUST enforce all quality gates. Deployment MUST be automated and include
rollback capabilities.

## Quality Assurance

Automated testing MUST cover functional, integration, performance, and security aspects.
Manual testing MUST validate user experience and accessibility. Documentation MUST be
updated with each feature. Security scanning MUST be performed on all dependencies.
Quality metrics MUST be tracked and reported regularly.

## Governance

Constitution supersedes all other practices. Amendments require documentation, approval,
and migration plan. All PRs/reviews MUST verify compliance. Complexity MUST be justified.
Breaking constitutional principles requires explicit exception approval and remediation
timeline. Use agent-specific guidance files for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-10-06 | **Last Amended**: 2025-10-06