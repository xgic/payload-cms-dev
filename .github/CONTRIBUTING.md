# Contributing to `payload-cms-dev-containers`

**Project**: [XGIC/payload-cms-dev-containers](https://github.com/XGIC/payload-cms-dev-containers)  
**Purpose**: A production-grade, open-source toolkit that enables the rapid creation and setup of highly optimized **Payload CMS** development environments using **Visual Studio Code Dev Containers** orchestrated via **Docker Compose**.  

We welcome contributions from the open-source community. Whether you are fixing a bug, adding support for a new Payload CMS version, improving Docker performance, enhancing documentation, or proposing architectural improvements, your work directly advances developer productivity across the Payload CMS ecosystem.

By participating, you agree to abide by our [Code of Conduct](#code-of-conduct) and the [Contributor License Agreement](#contributor-license-agreement) (implicitly accepted upon submission of a pull request).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Environment Setup](#development-environment-setup)
- [GitHub Flow & Branching Strategy](#github-flow--branching-strategy)
- [Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)](#step-by-step-guide-initiating-a-new-feature-branch-github-free-account)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Coding Standards & Best Practices](#coding-standards--best-practices)
- [Reporting Bugs & Requesting Features](#reporting-bugs--requesting-features)
- [Contributor License Agreement](#contributor-license-agreement)
- [Recognition](#recognition)

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct (v2.1)](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers at `conduct@xgic.net`.

## Coding Standards and Best Practices

This document outlines mandatory coding standards and recommended practices for all contributors. Adherence ensures consistency, maintainability, and high code quality across Unreal Engine 5.7.4 projects and associated Payload CMS web applications.

### Payload CMS Projects for Web-Based Applications
- **Core Development Approach**: Build all configurations and custom logic using Payload CMS’s code-first TypeScript methodology as detailed in the [official Payload CMS Documentation](https://payloadcms.com/docs). Define Collections, Globals, and endpoints in modular, separate TypeScript files for clarity and scalability.
- **Production and Deployment Standards**: Implement deployment following the [Payload CMS Production Deployment Guide](https://payloadcms.com/docs/production/deployment). This includes Next.js build optimization, secure management of environment variables (e.g., `PAYLOAD_SECRET`), Docker multi-stage builds, and hosting considerations for platforms such as Vercel or self-hosted environments.
- **TypeScript Implementation**: Apply the [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) for all Payload-related TypeScript code. Combine with [TypeScript ESLint](https://typescript-eslint.io/) rules to enforce type safety, consistent interfaces, and avoidance of `any` types.

### Full-Stack Web Development (Next.js, TypeScript, Tailwind CSS, HTML, CSS, JavaScript)
- **HTML and CSS**: Follow the [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html) for semantic HTML structure, consistent indentation, and maintainable CSS practices.
- **JavaScript**: Comply with the [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) for any non-TypeScript JavaScript code, focusing on clarity, modularity, and avoidance of global scope pollution.
- **TypeScript**: Use the [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) together with [TypeScript ESLint](https://typescript-eslint.io/) configuration for all application code, ensuring strong typing and modern ES module patterns.
- **Tailwind CSS**: Style exclusively according to the official [Tailwind CSS Styling with Utility Classes](https://tailwindcss.com/docs/styling-with-utility-classes) documentation. Prioritize utility-first classes for responsive design and minimize custom CSS to maintain consistency.
- **Next.js Framework**: Develop applications in accordance with the [official Next.js Documentation](https://nextjs.org/docs), with particular attention to App Router architecture, Server Components, static/dynamic rendering strategies, and performance best practices outlined in the “Building Your Application” sections.

### Cross-Project and Additional Industry Best Practices
- **Code Formatting and Linting**: Enforce consistent formatting using Prettier (for web projects) and project-specific linters. Maintain shared `.editorconfig` files and ESLint/Prettier configurations committed to the repository.
- **Version Control and Collaboration**: Adopt [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages. Use feature-branch workflows with mandatory pull request reviews, clear descriptions, and linked issue references.
- **Documentation Standards**: Provide thorough inline documentation—Doxygen-style comments for C++ and TSDoc/JSDoc for TypeScript. Keep README files, API references, and architectural decision records up to date.
- **Testing and Quality Assurance**: Implement comprehensive automated testing. Leverage Unreal Engine’s Automation Test Framework for C++ components and Jest, React Testing Library, or Playwright for web applications. Aim for high test coverage on critical paths.
- **Security**: Follow the [OWASP Top 10](https://owasp.org/www-project-top-ten/) guidelines for all web-facing code, including input validation, secure authentication, and protection against common vulnerabilities.
- **Accessibility**: Ensure web interfaces meet [WCAG 2.2](https://www.w3.org/WAI/WCAG21/quickref/) Level AA standards through semantic HTML, proper ARIA attributes, and keyboard navigation support.
- **Performance and Architecture**: Profile regularly using Unreal Insights (for UE) and Lighthouse/React Profiler (for web). Apply principles of clean architecture, SOLID design, and separation of concerns to all codebases.
- **Dependency and Tooling Management**: Maintain up-to-date dependencies with lockfiles, conduct regular vulnerability audits (e.g., `npm audit` or equivalent), and document all third-party libraries.

All contributors are expected to review this document before submitting code. Questions regarding interpretation should be raised in the project’s discussion channel or during code review.

## Development Environment Setup

The project itself is designed to be self-hosting. We strongly recommend using the **Dev Container** provided by this repository for all development work. This guarantees identical build, test, and lint environments for every contributor.

1. Fork the repository (see branching guide below).
2. Open your fork in **Visual Studio Code**.
3. VS Code will automatically detect the `.devcontainer/devcontainer.json` and prompt you to "Reopen in Container".
4. Once inside the container, run:
   ```bash
   docker compose up -d
   ```
5. The Payload CMS instance will be available at `http://localhost:3000`.

All scripts, tests, and linting commands are defined in `package.json` and executed inside the container.

## GitHub Flow & Branching Strategy

We follow the **GitHub Flow** model:
- The `main` branch is the only long-lived branch and is always in a releasable state.
- All changes are made in short-lived **feature branches** created from `main`.
- Every pull request targets `main`.
- Protected branch rules (enforced via repository settings) require passing status checks and at least one approving review before merging.

**Branch naming convention** (enforced via Conventional Commits tooling):
- `feat/...` – new features or enhancements
- `fix/...` – bug fixes
- `docs/...` – documentation changes
- `refactor/...` – code refactoring without functional change
- `test/...` – adding or updating tests
- `chore/...` – build, CI, or tooling changes

## Step-by-Step Guide: Initiating a New Feature Branch (GitHub Free Account)

GitHub Free accounts do **not** grant direct push access to organization repositories. Therefore, all external contributors **must** use the **Fork + Pull Request** workflow. The following guide is tailored specifically for contributors to `XGIC/payload-cms-dev-containers` and adheres to GitHub’s official best practices (GitHub Flow, fork model, and Conventional Commits).

### Step 1: Fork the Repository
1. Navigate to [https://github.com/XGIC/payload-cms-dev-containers](https://github.com/XGIC/payload-cms-dev-containers) in your browser.
2. Click the **Fork** button in the top-right corner.
3. Select your personal GitHub Free account as the destination.
4. Once the fork completes, you will be redirected to `https://github.com/YOUR-USERNAME/payload-cms-dev-containers`.

### Step 2: Clone Your Fork Locally
```bash
git clone https://github.com/YOUR-USERNAME/payload-cms-dev-containers.git
cd payload-cms-dev-containers
```

### Step 3: Add the Upstream Remote
This allows you to keep your fork synchronized with the official repository:
```bash
git remote add upstream https://github.com/XGIC/payload-cms-dev-containers.git
git remote -v   # verify remotes
```

### Step 4: Fetch the Latest Upstream Changes
Always start from the latest `main`:
```bash
git fetch upstream
git checkout main
git merge upstream/main   # or git rebase upstream/main
git push origin main
```

### Step 5: Create a New Feature Branch
```bash
git checkout -b feat/descriptive-feature-name
```
**Examples**:
- `feat/add-payload-3-0-support`
- `fix/docker-compose-healthcheck`
- `docs/improve-devcontainer-readme`

Branch names must be lowercase, use hyphens, and be descriptive.

### Step 6: Make Your Changes
- Work exclusively inside the Dev Container (recommended).
- Follow the [Coding Standards](#coding-standards--best-practices) below.
- Keep changes small, focused, and atomic.

### Step 7: Stage, Commit, and Push
Use **Conventional Commits** (see section below):
```bash
git add .
git commit -m "feat: add support for Payload CMS v3.0"
git push origin feat/descriptive-feature-name
```

### Step 8: Open a Pull Request
1. Go to your fork on GitHub.
2. Click **Compare & pull request**.
3. Ensure the base repository is `XGIC/payload-cms-dev-containers` and base branch is `main`.
4. Fill out the PR template completely.
5. Link any related issues using `Closes #123` or `Resolves #123`.

Your PR will automatically trigger CI checks (Docker build, linting, tests). All checks must pass before review.

## Commit Message Convention

All commits **must** follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types** (lowest to highest precedence):
- `fix`, `feat`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`, `style`

**Scope examples**: `docker`, `devcontainer`, `payload`, `docs`, `ci`

**Examples**:
```bash
feat(devcontainer): add Node.js 20 support for Payload CMS 3.x
fix(docker): resolve healthcheck race condition in postgres service
docs: update CONTRIBUTING.md with GitHub Free workflow
```

Commit messages are validated automatically by `commitlint` in the CI pipeline.

## Pull Request Guidelines

- One logical change per PR.
- Keep PRs under 500 lines of code (smaller is better).
- Include a clear title using Conventional Commits format.
- Fill out the entire PR template.
- Add tests for new functionality.
- Update documentation when behavior changes.
- Respond to review comments promptly.

Maintainers will merge only after at least one approval and successful CI.

## Coding Standards & Best Practices

- **Docker / Docker Compose**: Follow official [Docker Best Practices](https://docs.docker.com/build/building/best-practices/) and multi-stage builds where appropriate.
- **Dev Containers**: Adhere to the [Dev Container Specification](https://containers.dev/).
- **Shell scripts**: Use `shellcheck` and POSIX-compliant syntax.
- **TypeScript / Node.js**: Strict ESLint + Prettier configuration (enforced).
- **Security**: Never commit secrets; use `.devcontainer/.env.example` to store default values for new environment variables.
- **Performance**: Optimize layer caching in Dockerfiles.
- **Documentation**: All new features must include usage examples in README.md.

## Reporting Bugs & Requesting Features

1. Search existing issues to avoid duplicates.
2. Open a new issue using the appropriate template.
3. For bugs, provide:
   - Steps to reproduce
   - Expected vs. actual behavior
   - Payload CMS version, Docker version, host OS
   - `docker compose logs` output

## Contributor License Agreement

All contributions are licensed under the project’s [MIT License](LICENSE). By submitting a pull request, you affirm that you have the right to license your contribution under these terms.

## Recognition

Contributors are recognized in:
- The `CONTRIBUTORS.md` file (updated on merge).
- Release notes.
- The XGIC open-source hall of fame.

---

**Thank you for helping make Payload CMS development faster, more reliable, and more accessible for the entire community.**

Questions? Open an issue or reach out to the maintainers via Discussions.  
Last updated: May 21, 2026