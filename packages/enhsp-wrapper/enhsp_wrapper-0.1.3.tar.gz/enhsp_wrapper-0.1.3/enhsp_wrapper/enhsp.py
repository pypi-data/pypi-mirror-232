from dataclasses import dataclass
from enum import Enum, auto
import importlib.resources
import os
import subprocess
import tempfile
import time
from typing import List, Optional
import warnings


class PlanningStatus(Enum):
    SUCCESS = auto()
    UNSOLVABLE = auto()
    TIMEOUT = auto()
    MEMEOUT = auto()
    ERROR = auto()
    UNKNOWN = auto()


@dataclass
class PlanningResult:
    status: PlanningStatus
    plan: Optional[List[str]]
    time: float
    stdout: str
    stderr: str


class ENHSP:
    def __init__(self, params: str):
        """Initialize ENHSP.

        Args:
            params (str): the parameters to pass to ENHSP
        """
        self.params = params
        with importlib.resources.path("enhsp_wrapper.lib", "jpddlplus.jar") as path:
            self.path = path

        if "-timeout" not in self.params.split():
            warnings.warn(
                "No timeout specified. ENHSP will run forever if the "
                "problem is unsolvable.",
                RuntimeWarning,
            )

    def plan(self, domain_path: str, problem_path: str) -> PlanningResult:
        """Plan with ENHSP.

        Args:
            domain_path (str): path to domain file
            problem_path (str): path to problem file

        Returns:
            PlanningResult: the planning result
        """
        cmd = [
            "java",
            "-jar",
            str(self.path),
            "-o",
            domain_path,
            "-f",
            problem_path,
            *self.params.split(),
        ]
        # We respect ENHSP's timeout, so we don't need to set a timeout here.
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start

        status = PlanningStatus.UNKNOWN
        plan = None

        for i, line in enumerate(result.stdout.split("\n")):
            if line == "Problem Detected as Unsolvable":
                status = PlanningStatus.UNSOLVABLE
                break

            if line == "Found Plan:":
                status = PlanningStatus.SUCCESS
                plan = []

                for line in result.stdout.split("\n")[i + 1 :]:
                    if line == "":
                        break
                    plan.append(line.split(": ")[1])
        
        if "Timeout" in result.stderr:
            status = PlanningStatus.TIMEOUT
        elif "Memory" in result.stderr:
            status = PlanningStatus.MEMEOUT  # not tested
        elif result.returncode != 0 and status == PlanningStatus.UNKNOWN:
            status = PlanningStatus.ERROR

        return PlanningResult(status, plan, duration, result.stdout,
                              result.stderr)

    def plan_from_string(self, domain_text: str, problem_text: str) -> PlanningResult:
        """Plan with ENHSP.

        Args:
            domain_text (str): the text of the domain (PDDL)
            problem_text (str): the text of the problem (PDDL)

        Returns:
            PlanningResult: the planning result
        """
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".pddl", dir=os.getcwd()
        ) as domain_file, tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".pddl", dir=os.getcwd()
        ) as problem_file:
            domain_file.write(domain_text)
            problem_file.write(problem_text)
            domain_file.flush()
            problem_file.flush()
            result = self.plan(domain_file.name, problem_file.name)

        os.remove(domain_file.name)
        os.remove(problem_file.name)
        return result
