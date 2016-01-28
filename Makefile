# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

PROJECT  := hypothesis_couchdb
COVERAGE := coverage
FLAKE8   := flake8
GIT      := git
PIP      := pip3
PYLINT   := pylint
PYTHON   := python3
PYTHON33 := python3.3
PYTHON34 := python3.4


ENSURECMD=which $(1) > /dev/null 2>&1 || (echo "*** Make sure that $(1) is installed and on your path" && exit 1)


.PHONY: help
# target: help - Prints this help
help:
	@egrep "^# target:" Makefile | sed -e 's/^# target: //g' | sort


.PHONY: venv
# target: venv - Setups virtual environment
venv: $(PYTHON)
	@$(PYTHON) -m venv venv
	@echo "Virtuanenv has been created. Don't forget to run . venv/bin/active"


.PHONY: dev
# target: dev - Installs project for further developing
dev: $(PIP)
	@$(PIP) install -e .[dev]


.PHONY: install
# target: install - Installs hypothesis_couchdb package
install: $(PYTHON)
	@$(PYTHON) setup.py install


.PHONY: clean
# target: clean - Removes intermediate and generated files
clean: $(PYTHON)
	@find $(PROJECT) -type f -name '*.py[co]' -delete
	@find $(PROJECT) -type d -name '__pycache__' -delete
	@rm -f .coverage
	@rm -rf {build,cover,coverage}
	@rm -rf "$(PROJECT).egg-info"
	@$(PYTHON) setup.py clean


.PHONY: purge
# target: purge - Removes all unversioned files and resets repository
purge: $(GIT)
	@$(GIT) reset --hard HEAD
	@$(GIT) clean -xdff


.PHONY: check
# target: check - Runs tests
check: $(PYTHON)
	@$(PYTHON) setup.py test


.PHONY: check-all
# target: check-all - Runs lint checks, tests and generates coverage report
check-all: flake pylint-errors check-cov


.PHONY: check-cov
# target: check-cov - Runs tests and generates coverage report
check-cov: coverage-run coverage-report


coverage-run: $(COVERAGE)
	@$(COVERAGE) run setup.py test -q
coverage-report: $(COVERAGE)
	@$(COVERAGE) report -m --fail-under=100 --show-missing


.PHONY: distcheck
# target: distcheck - Checks if project is ready to ship
distcheck: distcheck-clean distcheck-33 distcheck-34
distcheck-clean:
	@rm -rf distcheck
distcheck-33: $(PYTHON33)
	@mkdir -p distcheck
	@virtualenv --python=python3.3 distcheck/venv-3.3
	@distcheck/venv-3.3/bin/python setup.py install
	@distcheck/venv-3.3/bin/python setup.py test
distcheck-34:  $(PYTHON34)
	@mkdir -p distcheck
	@$(PYTHON34) -m venv distcheck/venv-3.4
	@distcheck/venv-3.4/bin/python setup.py install
	@distcheck/venv-3.4/bin/python setup.py test


flake:
	@$(FLAKE8) --max-line-length=80 --statistics --exclude=tests --ignore=E501,F403 $(PROJECT)


.PHONY: pylint-report
# target: pylint-report - Generates pylint report
pylint-report: $(PYLINT)
	@$(PYLINT) --rcfile=.pylintrc $(PROJECT)


.PHONY: pylint-errors
# target: pylint-errors - Reports about pylint errors
pylint-errors: $(PYLINT)
	@$(PYLINT) --rcfile=.pylintrc -E $(PROJECT)


.PHONY: pypi
# target: pypi - Uploads package on PyPI
pypi: $(PYTHON)
	$(PYTHON) setup.py sdist register upload


$(COVERAGE):
	@$(call ENSURECMD,$@)
$(GIT):
	@$(call ENSURECMD,$@)
$(FLAKE8):
	@$(call ENSURECMD,$@)
$(PIP):
	@$(call ENSURECMD,$@)
$(PYLINT):
	@$(call ENSURECMD,$@)
$(PYTHON):
	@$(call ENSURECMD,$@)
$(PYTHON33):
	@$(call ENSURECMD,$@)
$(PYTHON34):
	@$(call ENSURECMD,$@)
