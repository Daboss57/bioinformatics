# Contributing to PanGenome Insight Platform (PGIP)

Thanks for your interest in strengthening PGIP! We welcome students, researchers, and professionals who want to grow the project or use it in coursework. This guide explains how to get started, propose changes, and maintain project quality.

## Ways to Contribute

- **Report bugs**: Open an issue with steps to reproduce, expected vs actual behavior, and relevant logs.
- **Suggest enhancements**: Share ideas for new plugins, visualizations, or workflow improvements.
- **Add plugins**: Implement prediction or annotation modules that follow the plugin spec in `docs/plugin-spec.md`.
- **Improve docs**: Clarify onboarding steps, write tutorials, or translate existing guides.
- **Benchmark + datasets**: Contribute test datasets, benchmarking results, or reproducible workflows.

## Development Workflow

1. Fork the repository and create a feature branch.
2. Set up the development environment:
   - Backend: `python -m pip install -r backend/requirements-dev.txt`
   - Frontend: `npm install` (future milestone)
   - Workflows: Install Nextflow and required container runtimes.
3. Run the test suite and linters relevant to your change:
   - Python: `pytest`
   - Formatting: `ruff check` (future milestone)
4. Commit with clear messages and open a pull request describing:
   - The problem and context
   - The solution and rationale
   - Testing performed
   - Any follow-up work or open questions

## Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python, enforced via `ruff` once configured.
- Limit FastAPI routes to thin controllers; place domain logic in services or utility modules.
- Prefer type hints and pydantic models for request/response schemas.
- For Nextflow, keep pipeline configuration modular and document container digests.
- For Rust components, include criterion benchmarks when optimizing critical paths.

## Commit & PR Checklist

- [ ] Tests cover new behavior or guard against regressions
- [ ] Documentation updated or added (README, docs/, API schema)
- [ ] New dependencies justified and pinned
- [ ] CI workflows pass

## Community Values

By participating, you agree to uphold the [Code of Conduct](CODE_OF_CONDUCT.md). Decisions about architecture and roadmap are documented in ADRs (to be added) and discussed openly via GitHub issues or community calls.

If you have questions, open an issue or email noelbobby01@gmail.com. We look forward to building PGIP together!
