"""
Project-wide pytest configuration.
"""
import os

# Belt-and-braces alongside the same setting in settings_test.py: setting it
# here too, at the top of the root conftest.py, is more reliably early than
# relying on Django settings-module import timing, which can race against
# pytest-playwright's session-scoped fixtures when multiple test files are
# collected together. See settings_test.py for the full explanation of why
# this is needed and why it's safe (no async views/consumers in this project).
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


def pytest_collection_modifyitems(session, config, items):
    """
    Append each test's trace ID (set via @pytest.mark.trace("T-FUNC-...")) to
    its reported node ID, so it's visible in -v output and JUnit XML without
    renaming the underlying test function. Requirements traceability source:
    data/requirements/phase-1-run-2-scope.yaml.

    Note: this modifies item._nodeid, which also flows into JUnit XML's
    classname/name attributes -- useful for the Phase 4 trace-mapping script,
    but worth knowing if reports look different from bare function names.
    """
    for item in items:
        marker = item.get_closest_marker('trace')
        if marker and marker.args:
            trace_id = marker.args[0]
            item._nodeid = f"{item.nodeid} [{trace_id}]"
