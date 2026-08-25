#!/usr/bin/env python
"""
trace_report.py

Bridges pytest's JUnit XML output into the novel-it-docs test-results YAML
files (data/test-results/*.yaml), using the @pytest.mark.trace(...) IDs
embedded in each test's reported name -- via conftest.py's
pytest_collection_modifyitems hook -- to know which requirement and which
source_file each result belongs to (looked up from
data/requirements/phase-1.yaml).

Usage:
    pytest --junitxml=/tmp/results.xml
    python scripts/trace_report.py \\
        --junit-xml /tmp/results.xml \\
        --docs-path /path/to/novel-it-docs \\
        [--date YYYY-MM-DD] \\
        [--dry-run]

Design notes
------------
- Tests with no "[TRACE_ID]" suffix in their reported name are silently
  skipped. This is expected, not an error -- it's exactly the pre-existing
  tests (novels/tests.py, planning/tests.py, the *_factories.py smoke
  tests) that were never part of the requirements-driven traceability
  system to begin with (see issues #136/#137 for the two that arguably
  should be, eventually).

- xfail results are recorded as FAIL, not a separate status -- the
  test-results YAML schema only supports PASS/FAIL, and a known, tracked
  bug is still a bug; xfail just means CI doesn't hard-fail on it. The
  issue number and comment are parsed from the xfail reason string, which
  must follow the convention already used in test_word_count_cascade.py:
  "<comment> -- issue #<N>". Reasons that don't follow this convention are
  recorded with the issue field left blank and a warning printed -- worth
  fixing the xfail's reason string to match the convention rather than
  silently losing the issue reference.

- A plain @pytest.mark.skip (not xfail) doesn't fit PASS/FAIL at all.
  There are none in the suite today; if one shows up, this script raises
  rather than guessing how to represent it.

- Never edits past executions -- only appends. If a test_id has never been
  recorded in its source_file's YAML before, a brand-new top-level entry is
  created for it (appended at the end of the file -- not inserted in
  requirement order, since finding the "right" spot isn't worth the risk of
  disturbing existing entries). If the source_file's YAML doesn't exist at
  all yet (World Building's situation as of today -- it's never had a
  recorded run), the file is created fresh with the standard header.

- Uses ruamel.yaml in round-trip mode specifically to preserve the existing
  files' hand-written header comments and per-entry example comments. A
  plain PyYAML load/dump would silently destroy both.

- --dry-run prints the full resulting YAML for every file that would
  change, to stdout, and touches nothing on disk. Worth using on the first
  run against any new dataset before trusting it for real.
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


TRACE_ID_RE = re.compile(r'\[([^\]]+)\]$')
XFAIL_ISSUE_RE = re.compile(r'^(.*?)\s*--\s*issue\s*#(\d+)\s*$', re.IGNORECASE)

NEW_FILE_HEADER = """# Test execution records for {title}
# Format:
#
# - test_id: T-FUNC-0101.01.01
#   requirement_id: R-FUNC-0101.01
#   executions:
#     - date: YYYY-MM-DD
#       result: PASS
#       issue:
#       comment: Brief description
#     - date: YYYY-MM-DD
#       result: FAIL
#       issue: 23
#       comment: "Retest after issue #23 closed \u2014 description"
#
# Notes:
#   - result must be exactly PASS or FAIL (uppercase)
#   - issue is the GitHub issue number only (no # prefix)
#   - Any comment containing # must be wrapped in double quotes
#   - Always append new executions \u2014 never edit past entries

"""

yaml = YAML()
yaml.preserve_quotes = True
# A wide width means every multi-line comment collapses to one line the
# first time this script touches its entry -- after that, it stays a
# single line on every future run (nothing left to re-wrap), rather than
# ruamel silently re-flowing wrap points differently on every run. Text
# and intent are unchanged either way; only where the line breaks falls
# changes, which doesn't count as "editing" a past entry.
yaml.width = 4096


def load_requirement_map(docs_path: Path) -> dict:
    """test_id -> {'req_id': ..., 'source_file': ...}, flattened from
    data/requirements/phase-1.yaml's per-requirement test_ids lists."""
    req_file = docs_path / 'data' / 'requirements' / 'phase-1.yaml'
    data = yaml.load(req_file.read_text())
    mapping = {}
    for entry in data:
        for test_id in entry['test_ids']:
            mapping[test_id] = {
                'req_id': entry['req_id'],
                'source_file': entry['source_file'],
            }
    return mapping


def parse_junit_xml(xml_path: Path) -> list:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    results = []

    for testcase in root.iter('testcase'):
        name = testcase.get('name', '')
        match = TRACE_ID_RE.search(name)
        if not match:
            continue  # no trace marker -- not part of the traceability system
        trace_id = match.group(1)

        failure = testcase.find('failure')
        error = testcase.find('error')
        skipped = testcase.find('skipped')

        if skipped is not None and skipped.get('type') == 'pytest.xfail':
            result = 'FAIL'
            message = skipped.get('message', '')
            issue_match = XFAIL_ISSUE_RE.match(message)
            if issue_match:
                comment = issue_match.group(1).strip()
                issue = int(issue_match.group(2))
            else:
                comment = message.strip()
                issue = None
                print(f"WARNING: xfail reason for {trace_id} doesn't follow "
                      f"the '<comment> -- issue #<N>' convention: {message!r}",
                      file=sys.stderr)
        elif failure is not None or error is not None:
            result = 'FAIL'
            node = failure if failure is not None else error
            comment = (node.get('message') or '').strip()
            issue = None
        elif skipped is not None:
            raise ValueError(
                f"{trace_id} was skipped (not xfail) -- the test-results "
                f"schema only supports PASS/FAIL. Handle this one manually "
                f"rather than guessing how to represent a plain skip."
            )
        else:
            result = 'PASS'
            comment = 'Automated test passed.'
            issue = None

        results.append({
            'trace_id': trace_id,
            'result': result,
            'comment': comment,
            'issue': issue,
        })

    return results


def build_execution_entry(execution_date, result, issue, comment):
    entry = CommentedMap()
    entry['date'] = execution_date
    entry['result'] = result
    entry['issue'] = issue  # None renders as blank, matching existing style
    entry['comment'] = comment
    return entry


def split_header(raw_text: str) -> tuple:
    """
    Split a file's raw text into (header, body), where header is every
    leading comment/blank line before the first real YAML content line.

    This exists because a file's leading preamble isn't really YAML data --
    it's text before any node ruamel.yaml's round-trip loader can attach a
    comment to -- so relying on ruamel to preserve it is unreliable. Byte-
    for-byte text preservation, kept entirely outside the YAML load/dump
    cycle, is deterministic regardless of library quirks.
    """
    lines = raw_text.splitlines(keepends=True)
    idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '' or stripped.startswith('#'):
            idx = i + 1
        else:
            break
    return ''.join(lines[:idx]), ''.join(lines[idx:])


def apply_to_yaml_file(docs_path, source_file, entries, execution_date, dry_run):
    yaml_path = docs_path / 'data' / 'test-results' / f'{source_file}.yaml'
    file_exists = yaml_path.exists()

    if file_exists:
        header, body = split_header(yaml_path.read_text())
        data = yaml.load(body)
    else:
        title = source_file.split('-', 1)[1].replace('-', ' ').title()
        title = f"{source_file.split('-')[0]} {title}"
        header = NEW_FILE_HEADER.format(title=title)
        data = None
    if data is None:
        data = CommentedSeq()

    by_test_id = {item['test_id']: item for item in data if isinstance(item, dict)}

    new_entries, appended = [], []
    for entry in entries:
        test_id = entry['trace_id']
        execution = build_execution_entry(
            execution_date, entry['result'], entry['issue'], entry['comment'])

        if test_id in by_test_id:
            by_test_id[test_id]['executions'].append(execution)
            appended.append(test_id)
        else:
            new_item = CommentedMap()
            new_item['test_id'] = test_id
            new_item['requirement_id'] = entry['req_id']
            new_item['executions'] = CommentedSeq([execution])
            data.append(new_item)
            new_entries.append(test_id)

    print(f"{source_file}: {len(appended)} execution(s) appended to existing "
          f"entries, {len(new_entries)} new test_id entr"
          f"{'y' if len(new_entries) == 1 else 'ies'} created"
          f"{' (new file)' if not file_exists else ''}")

    if dry_run:
        print(f"--- {yaml_path} (dry run, not written) ---")
        sys.stdout.write(header)
        yaml.dump(data, sys.stdout)
        print()
        return

    with open(yaml_path, 'w') as f:
        f.write(header)
        yaml.dump(data, f)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--junit-xml', required=True, type=Path)
    parser.add_argument('--docs-path', required=True, type=Path,
                         help='Path to the novel-it-docs repo checkout')
    parser.add_argument('--date', default=date.today().isoformat())
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    req_map = load_requirement_map(args.docs_path)
    results = parse_junit_xml(args.junit_xml)

    by_source_file = {}
    unmapped = []
    for r in results:
        info = req_map.get(r['trace_id'])
        if info is None:
            unmapped.append(r['trace_id'])
            continue
        by_source_file.setdefault(info['source_file'], []).append(
            {**r, 'req_id': info['req_id']})

    if unmapped:
        print(f"WARNING: {len(unmapped)} trace ID(s) have a marker but aren't "
              f"in phase-1.yaml, skipped: {unmapped}", file=sys.stderr)

    if not by_source_file:
        print("No trace-tagged test results found in the JUnit XML -- nothing to do.")
        return

    for source_file, entries in sorted(by_source_file.items()):
        apply_to_yaml_file(args.docs_path, source_file, entries, args.date, args.dry_run)


if __name__ == '__main__':
    main()
