import os
import re
from collections import defaultdict, namedtuple
from enum import StrEnum
from time import time
from typing import Dict, List, Optional, Set, Tuple, Union
from warnings import warn

import pytest
from coverage import CoverageData


def pytest_addoption(parser):
    group = parser.getgroup("coverage runtime minimisation")
    group.addoption(
        "--maxcov",
        action="store_true",
        default=False,
        help=(
            "Run the subset of tests provides maximum coverage with the minimum"
            "execution time. Requires a previous pytest run using --maxcov-record"
        ),
    )
    group.addoption(
        "--maxcov-record",
        action="store_true",
        default=False,
        help="Record coverage and timing data for the --maxcov option",
    )
    group.addoption(
        "--maxcov-threshold",
        type=float,
        default=100.0,
        metavar="PERCENT",
        help="Set the threshold for computing maximum coverage. Default: 100.0",
    )


def pytest_configure(config):
    config.pluginmanager.register(MaxCovPlugin(config), "maxcov-plugin")


Subset = namedtuple("Subset", ["set", "cost", "context"])


class CacheType(StrEnum):
    COST = "$"
    COVERAGE = "?"


class TestDuration:
    def __init__(self):
        self.start = None
        self.end = None

    @property
    def delta(self) -> time:
        return self.end - self.start


class MaxCovPlugin:
    def __init__(self, config: pytest.Config):
        self.config = config
        self.durations = defaultdict(TestDuration)
        if not 0.0 < config.option.maxcov_threshold <= 100.0:
            raise pytest.UsageError("--maxcov-threshold must be >0.0 and <=100.0")

    def pytest_collection(self, session: pytest.Session) -> None:
        if not self.config.pluginmanager.has_plugin("pytest_cov"):
            raise pytest.UsageError("pytest-maxcov uses pytest-cov which is not enabled")
        if self.config.option.no_cov:
            raise pytest.UsageError("pytest-maxcov uses coverage which is disabled with --no-cov")
        if self.config.option.maxcov_record and not self.config.option.cov_context:
            raise pytest.UsageError("pytest-maxcov requires --cov_context=test")

    def pytest_collection_modifyitems(
        self, session: pytest.Session, config: pytest.Config, items: List[pytest.Item]
    ) -> None:
        if not config.option.maxcov:
            return

        (costs, coverage) = self.read_cache()
        if len(coverage) == 0:
            warn(pytest.PytestWarning("No coverage data available: --maxcov aborted"))
            return

        collected_nodeids = set([x.nodeid for x in items])
        cached_nodeids = set(costs.keys())
        if not collected_nodeids.issubset(cached_nodeids):
            missing_nodeids = ", ".join(collected_nodeids - cached_nodeids)
            raise pytest.UsageError(f"no recorded durations for nodes: {missing_nodeids}")

        universe = set()
        subsets = []
        for context, hits in coverage.items():
            subset = set(hits.split("|"))
            universe |= subset
            subsets.append(Subset(set=subset, cost=costs[context], context=context))

        cover_subsets = set_cover(universe, subsets)
        maxcov_contexts = [x.context for x in cover_subsets]

        skip_maxcov = pytest.mark.skip(reason="excluded by --maxcov")
        maxcov_subsets = set_cover(universe, subsets, config.option.maxcov_threshold / 100)
        maxcov_contexts = [x.context for x in maxcov_subsets]

        for item in items:
            if item.nodeid not in maxcov_contexts:
                item.add_marker(skip_maxcov)

    def pytest_runtest_logstart(
        self, nodeid: str, location: Tuple[str, Optional[int], str]
    ) -> None:
        if self.config.option.maxcov_record:
            self.durations[nodeid].start = time()

    def pytest_runtest_logfinish(self, nodeid, location: Tuple[str, Optional[int], str]) -> None:
        if self.config.option.maxcov_record:
            self.durations[nodeid].end = time()

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if self.config.option.maxcov_record:
            self.write_cache()

    def read_cache(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        costs = {}
        coverage = {}
        lineno = 1
        try:
            fh = open(".maxcov", "r")
        except FileNotFoundError as e:
            raise pytest.UsageError(str(e)) from e

        for line in fh.readlines():
            if line.startswith(f"{CacheType.COST}:"):
                line_type = CacheType.COST
            elif line.startswith(f"{CacheType.COVERAGE}:"):
                line_type = CacheType.COVERAGE
            else:
                raise pytest.UsageError(f".maxcov is corrupted at line {lineno}")

            try:
                (context, data) = line[2:].split("=")
            except ValueError as e:
                raise pytest.UsageError(f".maxcov is corrupted at line {lineno}") from e

            if line_type == CacheType.COST:
                costs[context] = float(data)
            else:
                coverage[context] = data
            lineno += 1

        return costs, coverage

    def write_cache(self) -> None:
        coverage = coverage_data()
        try:
            fh = open(".maxcov", "w")
        except (FileNotFoundError, PermissionError) as e:
            raise pytest.UsageError(str(e)) from e

        for nodeid, duration in self.durations.items():
            print(f"{CacheType.COST}:{nodeid}={duration.delta}", file=fh)
        for context, hits in coverage.items():
            print(f"{CacheType.COVERAGE}:{context}={hits}", file=fh)


def coverage_data() -> Dict[str, str]:
    """Read coverage data from disk and return a list of lines/arcs hit per coverage context"""
    if os.environ.get("COVERAGE_FILE"):
        data = CoverageData(os.environ.get("COVERAGE_FILE"))
    else:
        data = CoverageData(".coverage")

    data.read()
    root_dir = os.path.dirname(data.base_filename()) + "/"
    coverage_data = {}
    for context in data.measured_contexts():
        if not context:
            continue
        data.set_query_context(context)
        if data.has_arcs():
            arcs = [
                [f"{filename.replace(root_dir,'')}:{arc}" for arc in data.arcs(filename)]
                for filename in data.measured_files()
            ]
            hits = set(e for s in arcs for e in s)
        else:
            lines = [
                [f"{filename.replace(root_dir,'')}:{line}" for line in data.lines(filename)]
                for filename in data.measured_files()
            ]
            hits = set(e for s in lines for e in s)
        context = re.sub(r"\|.*", "", context)
        coverage_data[context] = "|".join(hits)
    return coverage_data


def set_cover(
    universe: Set, subsets: List[Subset], confidence: Union[None, float] = None
) -> List[list]:
    all_elements = set(e for s in subsets for e in s.set)
    if universe != all_elements:
        raise RuntimeError("union of all sets doesn't match universe")

    if confidence is not None and (confidence <= 0.0 or confidence > 1.0):
        raise RuntimeError("subset match confidence must be >0.0 and <=1.0")

    covered = set()
    cover_subsets = []
    while True:
        best_subset = max(subsets, key=lambda x: len(x.set - covered) / x.cost)
        cover_subsets.append(best_subset)
        covered |= best_subset.set

        if confidence is None:
            if len(covered) == len(universe):
                break
        else:
            if len(covered) >= len(universe) * confidence:
                break

    return cover_subsets
