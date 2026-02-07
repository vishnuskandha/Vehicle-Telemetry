# GitHub & Contribution Guidelines

Complete guide for managing the repository, submitting contributions, and maintaining code quality.

---

## Table of Contents

1. [Repository Setup](#repository-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Git Workflow](#git-workflow)
6. [Pull Requests](#pull-requests)
7. [Issues & Bug Reports](#issues--bug-reports)
8. [Release & Versioning](#release--versioning)
9. [Maintenance & Support](#maintenance--support)

---

## Repository Setup

### Cloning

```bash
# HTTPS (no SSH key required)
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# SSH (requires SSH key)
git clone git@github.com:vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry
```

### Initial Setup

```bash
# Configure git (one time)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Or set globally (all repos on this machine)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git config --list
```

### Forking (for External Contributors)

1. Click **Fork** on GitHub.com
2. Clone your fork:
   ```bash
   git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
   cd Vehicle-Telemetry
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/vishnuskandha/Vehicle-Telemetry.git
   ```
4. Fetch upstream changes regularly:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

---

## Project Structure

### Directory Layout

```
Vehicle-Telemetry/
├── sensors/
│   ├── sensors_dashboard.py      # Main Pygame UI (550 lines)
│   ├── sensors_logger.py         # CSV data logger (50 lines)
│   ├── sensors_reader.py         # Shared hardware abstraction (440 lines)
│   ├── sensors_log.csv           # Output data log (auto-generated)
│   ├── sensors_logger.py          # Legacy logger (refactored)
│   ├── i2c_scan.py               # I2C device scanner utility
│   └── [other utilities]
│
├── .github/
│   ├── workflows/                # GitHub Actions CI/CD
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── pull_request_template.md
│
├── docs/                         # Additional documentation
│   ├── HARDWARE_SETUP.md
│   ├── WIRING_DIAGRAMS.md
│   └── TROUBLESHOOTING.md
│
├── README.md                     # Project overview
├── ARCHITECTURE.md               # System design
├── INSTALLATION.md               # Setup instructions
├── USAGE.md                      # Operational guide
├── COMMANDS.md                   # Command reference
├── GITHUB.md                     # This file
├── PROJECT_SUMMARY.md            # High-level overview
├── LICENSE                       # MIT / Apache 2.0 (choose one)
├── .gitignore                    # Git ignore rules
└── .editorconfig                 # Editor settings
```

### Key Files Explained

| File | Purpose | Owner |
|------|---------|-------|
| **sensors_dashboard.py** | Pygame fullscreen UI; main application | Core maintainer |
| **sensors_logger.py** | CSV data logger; runs continuously | Core maintainer |
| **sensors_reader.py** | Shared hardware abstraction layer | Core maintainer |
| **ARCHITECTURE.md** | System design & component breakdown | Documentation maintainer |
| **README.md** | Quick-start & feature overview | Documentation maintainer |
| **INSTALLATION.md** | Hardware wiring & pip dependencies | Maintainers |
| **LICENSE** | Legal terms (MIT recommended) | Project owner |

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/vishnuskandha/Vehicle-Telemetry.git
cd Vehicle-Telemetry

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt
```

### Requirements Files

**requirements.txt** (production dependencies)
```
pygame==2.6.1
adafruit-blinka==8.47.0
adafruit-circuitpython-ds3231==2.3.11
RPi.GPIO==0.7.0
lgpio==0.2.2.0
```

**requirements-dev.txt** (development tools)
```
-r requirements.txt
pytest==7.4.0
pytest-cov==4.1.0
black==23.9.1
flake8==6.1.0
mypy==1.5.0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=sensors --cov-report=html

# Run specific test file
pytest tests/test_sensors_reader.py

# Run with verbose output
pytest -v
```

### Code Style

**Black** (Python formatter)
```bash
# Format all Python files
black sensors/

# Check without modifying
black --check sensors/
```

**Flake8** (Linter)
```bash
# Check code style
flake8 sensors/ --max-line-length=100

# Generate report
flake8 sensors/ --format=json > flake8_report.json
```

**MyPy** (Type checker)
```bash
# Check type hints
mypy sensors/sensors_reader.py

# Strict mode
mypy --strict sensors/
```

---

## Git Workflow

### Branch Naming Conventions

Create branches with descriptive names:

```
feature/short-description      # New feature
bugfix/short-description       # Bug fix
docs/short-description         # Documentation update
refactor/short-description     # Code refactoring
perf/short-description         # Performance optimization
ci/short-description           # CI/CD changes
```

### Examples

```bash
# Feature branch
git checkout -b feature/add-data-export

# Bugfix branch
git checkout -b bugfix/fix-heading-drift

# Documentation branch
git checkout -b docs/add-api-reference

# From main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### Commit Messages

**Format:** Use imperative mood, be descriptive

```
# Good
git commit -m "Add CSV export feature to dashboard

- Add ExportDialog widget to main UI
- Implement file format conversion (CSV, Excel)
- Add timezone support for timestamps
- Update USAGE.md with export examples"

# Bad
git commit -m "fixed dashboard"  # Too vague
git commit -m "Refactored code"  # No details
```

**Guidelines:**
- First line: **50 characters max**, summary only
- Blank line
- Body: **72 characters per line**, explain WHY not WHAT
- List changes with `- ` bullets
- Reference issues: `Fixes #123` or `Closes #456`

### Keeping Your Branch Updated

```bash
# From your feature branch
git fetch origin
git merge origin/main

# Or (preferred): rebase for linear history
git rebase origin/main

# Handle conflicts if they occur
git status  # See conflicting files
# Edit files to resolve conflicts
git add .
git rebase --continue
```

---

## Pull Requests

### Creating a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **On GitHub.com:** Click "Compare & Pull Request"

3. **Fill PR template:**
   ```markdown
   ## Summary
   Brief description of what this PR does.

   ## Type
   - [ ] Feature
   - [ ] Bugfix
   - [ ] Documentation
   - [ ] Refactoring

   ## Related Issues
   Fixes #123, partially addresses #456

   ## Changes Made
   - Added method X to class Y
   - Refactored function Z
   - Updated documentation

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Manual tests on Raspberry Pi
   - [ ] No breaking changes to API

   ## Before & After
   **Before:**
   ```python
   # Old code
   ```
   
   **After:**
   ```python
   # New code
   ```

   ## Additional Notes
   Any special considerations or edge cases.
   ```

4. **Wait for reviews**
   - GitHub Actions CI runs automatically
   - At least 1 approval required
   - All conversations must be resolved

5. **Merge**
   - Squash & merge (for cleaner history)
   - OR merge (if commits are logical)
   - Delete branch after merge

### PR Checklist

Before submitting a PR, verify:

- [ ] Code follows PEP 8 (run `black`)
- [ ] No lint errors (run `flake8`)
- [ ] Type hints added (`mypy` passes)
- [ ] Tests written and passing
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with `main`

### PR Review Process

**Reviewers should check:**
1. Code quality & style
2. Documentation completeness
3. Test coverage
4. No breaking changes to API
5. Performance implications
6. Security concerns

**Comments:**
```
# Request changes (blocks merge)
👎 "This doesn't handle edge case X"

# Approve (allows merge)
👍 "Looks good!"

# Approve with suggestions (doesn't block)
✅ "Approved, but consider Y for future work"
```

---

## Issues & Bug Reports

### Issue Templates

**Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.md`)
```markdown
---
name: Bug Report
about: Report a bug
labels: bug
---

## Describe the Bug
Clear description of what's broken.

## Steps to Reproduce
1. Start dashboard with `...`
2. Set sensor to `...`
3. Observe error

## Expected vs Actual
**Expected:** Dashboard shows RPM gauge
**Actual:** Dashboard crashes with KeyError

## Environment
- Raspberry Pi 5
- Python 3.13
- Pygame 2.6.1
- OS: Raspberry Pi OS Bookworm

## Error Message
```
Traceback (most recent call last):
  File "sensors_dashboard.py", line 123, in update
    rpm = data["speed"]
KeyError: 'speed'
```

## Possible Cause
sensors_reader.py may not be setting the key correctly

## Workaround
(If any)

## Screenshots
(If applicable)
```

**Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.md`)
```markdown
---
name: Feature Request
about: Suggest a new feature
labels: enhancement
---

## Summary
One-line description of the feature.

## Motivation
Why would this feature be useful?

## Proposed Solution
How should it work?

## Alternatives Considered
Any other approaches?

## Additional Context
Mockups, links, references.
```

---

## Release & Versioning

### Semantic Versioning

Follow [semver](https://semver.org/) (MAJOR.MINOR.PATCH):

- **MAJOR (x.0.0):** Breaking changes (API incompatible)
- **MINOR (0.x.0):** New features (backwards compatible)
- **PATCH (0.0.x):** Bug fixes (backwards compatible)

**Examples:**
```
1.0.0       # First release
1.1.0       # Added new dashboard widget (minor)
1.1.1       # Fixed heading drift bug (patch)
2.0.0       # Complete UI redesign (major)
```

### Release Process

1. **Update version** in:
   - `./__init__.py` (if package)
   - `CHANGELOG.md`
   - `README.md` (version badge)

2. **Commit & tag:**
   ```bash
   git add .
   git commit -m "Release v1.2.0"
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin main --tags
   ```

3. **Create release** on GitHub.com:
   - Title: `v1.2.0`
   - Description: Copy from CHANGELOG.md
   - Attach any assets (e.g., prebuilt binaries)

4. **Announce** (optional):
   - Email to users
   - Blog post
   - GitHub Discussions

### CHANGELOG Format

```markdown
# Changelog

All notable changes to this project are documented in this file.

## [1.2.0] - 2026-02-15

### Added
- CSV export feature with timezone support
- Data analysis script template
- New heading calibration tool

### Changed
- Improved gauge smoothing algorithm (SMOOTHING=0.18)
- Refactored sensors_reader.py for better modularity

### Fixed
- #234: Heading drift on long trips
- #238: Dashboard crash when I2C disconnects

### Deprecated
- Old TkinterUI (removed in v2.0)

### Security
- Updated dependencies to latest patches

## [1.1.0] - 2026-01-20

### Added
- Autostart via XDG .desktop entry
- Systemd service (fallback)
```

---

## Maintenance & Support

### Code Ownership

| Component | Owner | Backup |
|-----------|-------|--------|
| sensors_reader.py | @core-maintainer | @dev2 |
| sensors_dashboard.py | @ui-developer | @core-maintainer |
| sensors_logger.py | @data-engineer | @core-maintainer |
| Documentation | @tech-writer | @core-maintainer |

### Review SLAs

| Type | Response Time | Resolution |
|------|---|---|
| Critical bugs | 24 hours | 1 week |
| Regular issues | 3-5 days | 2 weeks |
| Features | 1 week | Next minor release |
| Documentation | 2-3 days | ASAP |

### Communication Channels

- **Issues/PRs:** GitHub (preferred)
- **Urgent bugs:** GitHub Issues + label `critical`
- **Discussions:** GitHub Discussions (Q&A)
- **Email:** [maintainer@example.com]
- **Discord** (optional): [Invite link]

### Contributor Recognition

Include contributors in:
- README.md (Contributors section)
- CHANGELOG.md (Thanks to...)
- Release notes (GitHub release)

---

## Scripts & Automation

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run linting & type checks before committing

set -e

echo "Running black..."
black sensors/

echo "Running flake8..."
flake8 sensors/ --max-line-length=100

echo "Running mypy..."
mypy sensors/

echo "✓ Pre-commit checks passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions CI/CD

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Lint with flake8
        run: flake8 sensors/
      - name: Format check with black
        run: black --check sensors/
      - name: Type check with mypy
        run: mypy sensors/
      - name: Run tests
        run: pytest --cov=sensors
```

---

## Best Practices

### For Contributors

1. **Start small**
   - Begin with documentation improvements
   - Then tackle bugs
   - Finally propose features

2. **Communicate early**
   - Open an issue before large features
   - Discuss approach with maintainers
   - Avoid surprise PRs

3. **Test thoroughly**
   - Test on actual Raspberry Pi hardware
   - Test on different Python versions
   - Add unit tests for new code

4. **Documentation first**
   - Update docs with code changes
   - Include examples
   - Link related issues/PRs

### For Maintainers

1. **Respond promptly**
   - Acknowledge issues within 24 hours
   - Provide clear feedback on PRs
   - Be respectful & inclusive

2. **Automate boring tasks**
   - Use GitHub Actions for CI/CD
   - Pre-commit hooks for code quality
   - Auto-label issues & PRs

3. **Maintain quality**
   - Require reviews for all code
   - Run tests before merging
   - Enforce code standards

---

## Troubleshooting Git

| Problem | Solution |
|---------|----------|
| Accidentally committed to main | `git reset HEAD~1` (undo last commit) |
| Merge conflicts | Use `git mergetool` or `git add` after manual editing |
| Lost commits | `git reflog` to recover |
| Wrong branch pushed | `git push origin --delete branch-name` then push correct branch |
| Want to undo public commit | `git revert <hash>` (creates new commit) |

---

## Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://pep8.org/)

---

For questions or discussions, open a GitHub Issue or start a Discussion.

