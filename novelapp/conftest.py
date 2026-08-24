"""
Project-wide pytest configuration.
"""


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
