import traceback

from google.protobuf.json_format import MessageToDict
import dataclasses
from typing import Iterable
from typing import List
from typing import Type

from oak9.tython.core.types import Blueprint

from models.shared.shared_pb2 import Finding


@dataclasses.dataclass
class BlueprintRunResult:
    blueprint_class: Type[Blueprint] = None
    findings: List[Finding] = dataclasses.field(default_factory=list)
    exceptions: List[Exception] = dataclasses.field(default_factory=list)

    @staticmethod
    def get_flattened_findings(results: Iterable['BlueprintRunResult']) -> List[Finding]:
        return [finding for result in results for finding in result.findings]

    @staticmethod
    def get_flattened_exceptions(results: Iterable['BlueprintRunResult']) -> List[Exception]:
        return [exc for result in results for exc in result.exceptions]

    @staticmethod
    def to_json(result: 'BlueprintRunResult'):
        return {
            'blueprint_class': result.blueprint_class.__name__,
            'findings': [MessageToDict(f) for f in result.findings],
            'exceptions': [_exception_to_json(e) for e in result.exceptions]
        }


def execute_run_blueprints(runner_input, blueprint_classes: Iterable[Type[Blueprint]]) -> List[BlueprintRunResult]:
    results: List[BlueprintRunResult] = []

    for blueprint_class in blueprint_classes:
        blueprint_instance = blueprint_class(graph=runner_input)
        blueprint_result = BlueprintRunResult(blueprint_class=blueprint_class)

        try:
            run_result = blueprint_instance.validate()
        except Exception as e:
            blueprint_result.exceptions.append(e)
            continue

        for i in run_result:
            if isinstance(i, Finding):
                blueprint_result.findings.append(i)
            elif isinstance(i, Exception):
                blueprint_result.exceptions.append(i)

        results.append(blueprint_result)

    return results


def _exception_to_json(exception: Exception):
    return {
        'name': exception.__class__.__name__,
        'message': str(exception),
        'traceback': ''.join(traceback.format_exception(type(exception), value=exception, tb=exception.__traceback__))
    }
