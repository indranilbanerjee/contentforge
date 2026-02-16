# Contributing to ContentForge

Thank you for your interest in contributing to ContentForge! This document provides guidelines and instructions for contributing.

---

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful:** Treat everyone with respect and kindness
- **Be collaborative:** Work together and help each other
- **Be inclusive:** Welcome diverse perspectives and experiences
- **Be professional:** Focus on what's best for the project and community

---

## How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Gather relevant information (version, platform, steps to reproduce)

**Bug Report Template:**
```markdown
**Description:** Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:** What should happen

**Actual Behavior:** What actually happens

**Environment:**
- ContentForge version:
- Claude Code/Cowork version:
- Platform (OS):
- Node version (if relevant):

**Additional Context:** Screenshots, logs, etc.
```

### Suggesting Enhancements

**Enhancement Proposal Template:**
```markdown
**Feature Description:** Clear description of the proposed feature

**Use Case:** Why is this feature needed? What problem does it solve?

**Proposed Solution:** How should this work?

**Alternatives Considered:** Other approaches you've thought about

**Priority:** Low / Medium / High
```

### Contributing Code

**Priority Areas:**
1. **Additional Content Type Templates** (landing pages, email sequences, press releases)
2. **Alternative MCP Integrations** (Notion, Airtable, Confluence)
3. **Industry-Specific Rubrics** (Finance, Healthcare, Legal compliance)
4. **Humanization Patterns** (non-English languages)
5. **Test Coverage** (unit tests for individual agents)
6. **Documentation** (tutorials, video guides, examples)

---

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- Claude Code or Cowork installed
- Google Cloud account (for Sheets/Drive testing)
- Git

### Setup Steps

1. **Fork the repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/contentforge.git
   cd contentforge
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Install dependencies** (if any)
   ```bash
   npm install
   ```

4. **Set up test environment**
   ```bash
   # Copy example configs
   cp .mcp.json.example .mcp.json
   # Edit with your service account credentials
   ```

5. **Make your changes**
   - Edit agent files in `agents/`
   - Add/update templates in `templates/`
   - Modify configs in `config/`
   - Update docs if needed

6. **Test your changes**
   ```bash
   # Test manually with Claude Code
   claude code
   /contentforge "test with your changes"
   ```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All agent files use consistent markdown formatting
- [ ] Documentation is updated (README, agent comments)
- [ ] Changes are tested manually
- [ ] Commit messages are clear and descriptive

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Changes Made
- Bullet list of specific changes

## Testing Done
- How you tested these changes
- Example runs with results

## Screenshots (if applicable)
- Before/after screenshots or output samples

## Checklist
- [ ] My code follows the project style
- [ ] I have updated the documentation
- [ ] I have added tests (if applicable)
- [ ] All tests pass
- [ ] I have tested this with Claude Code/Cowork
```

### Review Process

1. **Submit PR:** Create pull request against `main` branch
2. **Automated Checks:** Wait for any CI checks (if implemented)
3. **Code Review:** Maintainers will review your code
4. **Address Feedback:** Make requested changes
5. **Approval:** Once approved, maintainer will merge
6. **Release:** Changes included in next version

### After PR is Merged

- Delete your feature branch
- Pull latest changes from main
- Your contribution will be acknowledged in release notes!

---

## Coding Standards

### Agent File Structure

**All agent files should follow this structure:**
```markdown
# Agent Name — ContentForge Phase X

**Role:** One-line description

---

## INPUTS
[List of inputs from previous phases]

---

## YOUR MISSION
[Clear description of agent's purpose]

---

## EXECUTION STEPS
### Step 1: [Step Name]
[Detailed instructions]

### Step 2: [Step Name]
[Detailed instructions]

---

## OUTPUT FORMAT
[Template for agent output]

---

## QUALITY GATE X CRITERIA CHECK
[Pass/fail criteria]

---

**Agent Name — Phase X Complete**
```

### Configuration Files

**JSON files must be:**
- Valid JSON (no comments, trailing commas)
- Properly indented (2 spaces)
- Include descriptive keys
- Documented with example usage

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Use markdown formatting consistently
- Add screenshots for complex steps
- Keep line length under 120 characters

---

## Testing Guidelines

### Manual Testing Checklist

**For agent changes:**
- [ ] Test with minimum input (edge case)
- [ ] Test with typical input
- [ ] Test with maximum input (stress test)
- [ ] Verify quality gate pass/fail logic
- [ ] Check feedback loop behavior

**For template changes:**
- [ ] Test with each content type
- [ ] Verify word count calculations
- [ ] Check readability targets
- [ ] Ensure citation requirements work

**For config changes:**
- [ ] Test with default values
- [ ] Test with industry overrides
- [ ] Verify backward compatibility
- [ ] Check edge cases (extreme values)

### Integration Testing

**Full pipeline test:**
```bash
# Create test requirement in Google Sheets
# Run full pipeline
/contentforge "Generate content for test row in [Sheet URL]"

# Verify:
# - All 9 phases complete
# - Quality score calculated correctly
# - Output .docx generated
# - Tracking sheet updated
# - Brand voice applied
```

---

## Specific Contribution Areas

### Adding a New Content Type

1. Create template in `templates/content-types/[type]-structure.md`
2. Define structure, word count, readability target, citation requirements
3. Update `agents/03-content-drafter.md` to handle new type
4. Add test case in testing docs
5. Update README with new type

**Example:**
```markdown
# Email Sequence Structure

**Target:** 300-500 words per email
**Flesch-Kincaid Grade:** 6-8 (very accessible)
**Citation Requirements:** 1-2 per email
**Emails in Sequence:** 3-5

[... continue with structure]
```

### Adding a New MCP Integration

1. Add MCP server config to `.mcp.json`
2. Update relevant agents to use new MCP (e.g., Phase 8 for new storage)
3. Add configuration docs
4. Test integration thoroughly
5. Update README with setup instructions

### Adding Industry-Specific Rubrics

1. Add industry override to `config/scoring-thresholds.json`
2. Define dimension weights for industry
3. Add compliance requirements to brand profile template
4. Document regulatory considerations
5. Test with sample brand in that industry

### Improving Humanization (Phase 6.5)

1. Add new AI telltale phrases to `config/humanization-patterns.json`
2. Add language-specific patterns (if non-English)
3. Test burstiness improvements
4. Validate SEO preservation
5. Document detection resistance improvements

---

## Git Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(humanizer): add support for Spanish language patterns

Added Spanish telltale phrases and sentence structure patterns
to Phase 6.5 Humanizer for multilingual content support.

Closes #123
```

```
fix(reviewer): correct dimension weight calculation

Fixed bug where dimension weights weren't applying correctly
for industry overrides. Now properly loads industry-specific
weights from scoring-thresholds.json.

Fixes #456
```

---

## Documentation Contributions

### README Updates
- Keep Quick Start section under 5 minutes
- Add new features to "What Was Built" section
- Update roadmap when features complete
- Add to FAQ if question comes up repeatedly

### Agent Documentation
- Add inline comments for complex logic
- Include examples for edge cases
- Document quality gate criteria clearly
- Explain loop conditions

### Tutorial Creation
- Step-by-step with screenshots
- Real-world use case examples
- Expected results at each step
- Common pitfalls and solutions

---

## Getting Help

**Questions about contributing?**
- Open a [Discussion](https://github.com/yourusername/contentforge/discussions)
- Comment on relevant issue
- Reach out to maintainers

**Stuck on implementation?**
- Check existing agent implementations for patterns
- Review SKILL.md for orchestration logic
- Look at similar features in other phases

---

## Recognition

**Contributors will be:**
- Listed in release notes
- Acknowledged in README (if significant contribution)
- Credited in commit history
- Part of shaping the future of enterprise content production!

---

## License

By contributing to ContentForge, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ContentForge!** 🚀

Your contributions help agencies, brands, and marketing teams produce better content faster.
