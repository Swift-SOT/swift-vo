# Makefile

# Define variables
VENV_DIR = .venv
SYSTEM_PYTHON = $(shell command -v python3.12 || command -v python3.11 || command -v python || command -v python3)
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
UV = $(VENV_DIR)/bin/uv
PIP_SYNC_ARGS = pip sync
PIP_INSTALL_ARGS = pip install -r
LINTER = $(VENV_DIR)/bin/pre-commit
LINTER_ARGS = run --all-files
TYPE_CHECKER = $(VENV_DIR)/bin/mypy
TYPE_CHECKER_ARGS = `git ls-files '*.py'`
PIP_COMPILE = ${UV}
PIP_COMPILE_ARGS = pip compile --quiet
FASTAPI = $(VENV_DIR)/bin/fastapi
REQUIREMENTS = requirements.txt
DEV-REQUIREMENTS = requirements-dev.txt
MODULE_FILE = swift_too_api/_version.py
VERSION = $(shell sed -n 's/^__version__ *= *"\(.*\)"/\1/p' $(MODULE_FILE))
# Next bit enables passing arguments to make commands
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

# .PHONY targets ensure that Make runs them every time, regardless of file changes
.PHONY: all setup lint format dev clean build docker process_jobs

# Run all steps (setup, lint, and run)
all: setup lint format type install

# Set up development environment
init: setup pip-install-dev

# Install UV to do super-fast pip-install-dev/pip-compile
${UV}: setup
	@command -v ${UV} >/dev/null 2>&1 || { \
		echo "Installing uv for super-fast pip-sync/pip-compile..."; \
		${PIP} install uv; \
	}

# Set up the virtual environment and install depends
setup: $(VENV_DIR)
$(VENV_DIR):
	@if ! command -v $(SYSTEM_PYTHON) > /dev/null 2>&1; then \
		echo "Python command not found"; \
		exit 1; \
	elif ! $(SYSTEM_PYTHON) -c "import sys; sys.exit(0) if sys.version_info >= (3, 11) else sys.exit(1)" >/dev/null 2>&1; then \
		echo "Python 3.11 or higher is required"; \
		exit 1; \
	else \
		echo "Using Python version: $$( $(SYSTEM_PYTHON) --version)"; \
	fi


	@${SYSTEM_PYTHON} -m venv $(VENV_DIR)
	@echo "Created virtual environment in $(VENV_DIR)"

# Install the dependencies needed for a development environment
pip-install-dev: setup ${UV}
	@echo "Syncing dependencies..."
	@${UV} ${PIP_INSTALL_ARGS} ${DEV-REQUIREMENTS}

# Install the dependencies needed for a production environment
pip-sync-prod: setup ${UV}
	@echo "Syncing dependencies..."
	@${UV} ${PIP_SYNC_ARGS} ${REQUIREMENTS}


# Generate the requirements files
requirements: ${REQUIREMENTS} ${DEV-REQUIREMENTS}

${REQUIREMENTS}: ${PIP_COMPILE} pyproject.toml
	@${PIP_COMPILE} ${PIP_COMPILE_ARGS} --output-file=${REQUIREMENTS} pyproject.toml
	@echo "Updated ${REQUIREMENTS}"

${DEV-REQUIREMENTS}: ${PIP_COMPILE} pyproject.toml
	@${PIP_COMPILE} ${PIP_COMPILE_ARGS} --extra=dev --output-file=${DEV-REQUIREMENTS} pyproject.toml
	@echo "Updated ${DEV-REQUIREMENTS}"

# Lint the code
lint: pip-install-dev
	@echo "Linting code..."
	@$(LINTER) ${LINTER_ARGS}

# Run type checker
type: pip-install-dev .venv/bin/fastapi
	@echo "Running type checker..."
	@$(TYPE_CHECKER) ${TYPE_CHECKER_ARGS}

# Run the API code in development mode
dev: pip-install-dev
	@${UV} pip install setuptools wheel
	@${FASTAPI} dev app.py

# Run the API in production mode
prod: pip-sync-prod
	@${UV} pip install setuptools wheel
	@${FASTAPI} run app.py --workers=4

# Clean up the virtual environment and other generated files
clean:
	@rm -rf $(VENV_DIR)
	@echo "Removed virtual environment"

# pip install the package into the virtual environment, with only necessary
# packages (so will remove any packages not *required* to run the API)
install: setup ${UV} pip-sync-prod
	@${UV} pip install setuptools wheel
	@${UV} pip install -r requirements.txt
	@$(PIP) install .

# Add a package from pyproject.toml and regenerate requirements files
add: setup ${UV}
	@$(UV) add $(RUN_ARGS)
	@echo
	@rm -f uv.lock
	@make requirements

# Remove a package from pyproject.toml and regenerate requirements files
remove: setup ${UV}
	@$(UV) remove $(RUN_ARGS)
	@rm -f uv.lock
	@make requirements

# Add a package from pyproject.toml for  dev only dependencies  and regenerate requirements files
add-dev: setup ${UV}
	@$(UV) add $(RUN_ARGS) --optional=dev
	@rm -f uv.lock
	@make requirements

# Remove a package from pyproject.toml for dev only dependencies and regenerate requirements files
remove-dev: setup ${UV}
	@$(UV) remove $(RUN_ARGS) --optional=dev
	@rm -f uv.lock
	@make requirements

# Build the API Docker image
build:
	@git archive -o /tmp/repo.tar HEAD
	@docker build -t swift-too-api \
	--build-arg SWIFT_TOO_API_VERSION=${VERSION} \
	--build-arg BUILD_DATE=$(shell date -u +'%Y-%m-%dT%H:%M:%SZ') \
	-f Dockerfile - < /tmp/repo.tar

# Run the API Docker image
docker: build
	# Run and pass minimal environment variables needed for test environment
	@docker run \
		--name swift-too-api \
		-p 8000:8000 \
		--env-file .env \
		swift-too-api

# Run the job worker
process_jobs: setup pip-install-dev install
	@${PYTHON} ./process_jobs.py

# The following allows to use the syntax `make run <args>` to run things. It's
# entirely optional, but it's a nice convenience.
run:
	@$(MAKE) $(RUN_ARGS)
