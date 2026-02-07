# Contributing to Vehicle Telemetry

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

Follow **PEP 8** with these tools:

```bash
# Format code
black sensors/

# Lint
flake8 sensors/ --max-line-length=100

# Type check
mypy sensors/

# Test
pytest -v
```

### Commit Messages

Use imperative mood, be descriptive:

```
Add CSV export feature to dashboard

- Implement ExportDialog widget
- Support multiple formats (CSV, Excel)
- Add timezone support
- Update USAGE.md with examples

Fixes #123
```

### Testing

- Write tests for new features
- Test on actual Raspberry Pi 5 hardware
- Verify hardware sensors work correctly

```bash
pytest --cov=sensors --cov-report=html
```

### Documentation

Update docs for code changes:
- [USAGE.md](docs/USAGE.md) — Operational changes
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Design changes
- [INSTALLATION.md](docs/INSTALLATION.md) — Dependency/setup changes

## Pull Request Process

1. **Ensure tests pass**
   ```bash
   pytest
   flake8 sensors/
   black --check sensors/
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature
   ```

3. **Open Pull Request on GitHub**
   - Title: Concise description
   - Body: What changed and why
   - Reference related issues: `Fixes #123`

4. **Respond to review feedback**
   - Address comments respectfully
   - Push additional commits if needed
   - Request re-review when ready

5. **Await merge** (maintainers will merge when approved)

## Reporting Bugs

### Before Reporting

- Check [existing issues](https://github.com/vishnuskandha/Vehicle-Telemetry/issues)
- Reproduce on latest `main` branch
- Gather relevant info (error message, hardware, OS version)

### Submit Bug Report

Click "[New Issue](https://github.com/vishnuskandha/Vehicle-Telemetry/issues/new)" and use template:

```
## Describe the Bug
Brief description of what's broken.

## Steps to Reproduce
1. Start dashboard with ...
2. Set sensor to ...
3. Observe error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- Raspberry Pi model
- Python version
- OS (Bookworm, etc.)
- Hardware (MPU6050, FC-33, etc.)

## Error Message
Full traceback if available.

## Additional Context
Screenshots, logs, etc.
```

## Feature Requests

### Submit Feature Request

Click "[New Issue](https://github.com/vishnuskandha/Vehicle-Telemetry/issues/new)" with:

```
## Summary
One-line description.

## Motivation
Why is this useful?

## Proposed Solution
How should it work?

## Alternatives
Other approaches considered?

## Additional Context
Mockups, links, references.
```

## Project Structure

```
vehicle-telemetry/
├── sensors_reader.py    # Sensor abstraction (don't break API)
├── sensors_dashboard.py # UI rendering
├── sensors_logger.py    # CSV logging
├── docs/                # Documentation
├── tests/               # Test suite
├── requirements*.txt    # Dependencies
└── LICENSE
```

### Key Files

| File | Owner | Approval Needed |
|------|-------|-----------------|
| `sensors_reader.py` | @core-maintainer | Yes |
| `sensors_dashboard.py` | @ui-developer | Yes |
| `sensors_logger.py` | @data-engineer | Yes |
| `docs/` | Community | 1+ review |

## Review Guidelines

### For Reviewers

1. **Code Quality** — Follows style guide, readable, well-commented
2. **Tests** — Adequate coverage, passes on real hardware
3. **Docs** — Updated to reflect changes
4. **Backwards Compatibility** — No breaking changes unless major version
5. **Performance** — No significant CPU/memory regression

### Review Checklist

- [ ] Code style (PEP 8, black, flake8)
- [ ] Type hints correct (mypy passes)
- [ ] Tests added + passing
- [ ] Documentation updated
- [ ] No breaking API changes
- [ ] Commits are logical

## Release Process

1. **Create release branch** from `main`
2. **Update version** in code/docs
3. **Update CHANGELOG.md**
4. **Tag release** (`git tag v1.2.0`)
5. **Create GitHub Release** with notes
6. **Announce** to community

## Communication Channels

- **Issues/PRs:** [GitHub](https://github.com/vishnuskandha/Vehicle-Telemetry)
- **Discussions:** [GitHub Discussions](https://github.com/vishnuskandha/Vehicle-Telemetry/discussions)
- **Email:** [maintainer@example.com]

## Questions?

- Check [GITHUB.md](GITHUB.md) for repo guidelines
- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Browse [existing issues](https://github.com/vishnuskandha/Vehicle-Telemetry/issues) for answers

Thank you for contributing! 🚀
