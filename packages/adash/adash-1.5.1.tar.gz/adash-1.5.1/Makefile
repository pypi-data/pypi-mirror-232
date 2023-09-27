# Makefile for automating release tasks

# Get project name from pyproject.toml
PROJECT_NAME=$(shell grep name pyproject.toml | head -n 1 | awk -F= '{print $$2}' | xargs)
# Get the current version using `rye version`
NEW_VERSION=$(shell rye version)
# Bump type (major, minor, patch). Default is 'patch'.
BUMP_TYPE=patch

# Step 1: Create PR
release-step1: create-branch bump-version build-publish gen-docs gen-changelog commit create-pr

create-branch:
	git checkout -b pre-release

bump-version:
	rye version --bump $(BUMP_TYPE)
	$(eval NEW_VERSION := $(shell rye version))

build-publish:
	rye build -c && rye publish

gen-docs:
	pdoc --html --output-dir=docs --force $(PROJECT_NAME)

gen-changelog:
	git cliff --tag $(NEW_VERSION) -o CHANGELOG.md

commit:
	git add --all
	git commit -m "🚀 new release setup $(PROJECT_NAME)"

create-pr:
	gh pr create --title "New release $(NEW_VERSION)" --body "Release version $(NEW_VERSION)" --json number -q 'number' > pr_id.txt


# Step 2: Merge PR, tag, and cleanup
release-step2: approve-pr merge-pr tag-version pull-main delete-branch

approve-pr:
	gh pr review --approve $(shell cat pr_id.txt)

merge-pr:
	gh pr merge --merge

tag-version:
	git tag $(NEW_VERSION)
	git push origin $(NEW_VERSION)

pull-main:
	git checkout main
	git pull origin main

delete-branch:
	git branch -D pre-release
	gh pr close --delete-branch

# Help information
help:
	@echo "Available tasks:"
	@echo "  make release-step1     - Step 1: Create and push a PR for the new release."
	@echo "  make release-step2     - Step 2: Approve PR, merge, tag and cleanup."
	@echo ""
	@echo "Examples:"
	@echo "  make release-step1 BUMP_TYPE=major  - Create a PR for a major version bump."
	@echo "  make release-step2                  - Complete the release after manual verification."
	@echo "  make help                           - Display this help message."
