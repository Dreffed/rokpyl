# Workflow

## Target Flow
ARCH / Design -> SPECs -> TDD / Code -> test -> deploy

## Artifacts by Stage
- ARCH: `docs/ARCH.md` (system boundaries, components, data flow)
- Design: `docs/DESIGN.md` (module layout, interfaces, config)
- SPECs: `docs/SPEC.md` (behavioral contracts and acceptance criteria)
- TDD / Code: implementation plus `docs/TEST_PLAN.md`
- Test: unit, integration, and CLI e2e
- Deploy: Docker image + runbook

## Gate Checks
- Architecture aligns with constraints and plugin strategy.
- Design maps to SPEC behaviors and flags.
- Tests map 1:1 to acceptance criteria.

