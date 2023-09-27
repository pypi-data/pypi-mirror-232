import dataclasses
from typing import List
from typing import Type

from core.commands.preview import PreviewCommandArguments
from core.commands.preview import PreviewCommandResult
from core.commands.preview import execute_preview
from core.commands.run_blueprints import BlueprintRunResult
from core.services.tython_api_service import TythonApiService
from core.types import Blueprint
from core.types import Configuration
from core.types import PropertiesNamesMixin
from models.shared.shared_pb2 import RunnerInput


@dataclasses.dataclass
class ApplyCommandArguments(PropertiesNamesMixin):
    blueprints_suite_absolute_path: str

    # Used to build app arch. Should be removed in the future.
    oak9_api_url: str
    oak9_org_id: str
    oak9_project_id: str
    oak9_environment_id: str
    oak9_api_key: str


@dataclasses.dataclass
class ApplyCommandResult(PreviewCommandResult):
    request_id: str = ""

    blueprint_classes: List[Type[Blueprint]] = dataclasses.field(default_factory=list)
    blueprints_results: List[BlueprintRunResult] = dataclasses.field(default_factory=list)
    runner_inputs: List[RunnerInput] = dataclasses.field(default_factory=list)


def execute_apply(arguments: ApplyCommandArguments) -> ApplyCommandResult:
    tython_api_service = TythonApiService(Configuration(
        api_key=arguments.oak9_api_key,
        org_id=arguments.oak9_org_id,
        project_id=arguments.oak9_project_id,
        env_id=arguments.oak9_environment_id,
        data_endpoint=arguments.oak9_api_url,

        # not needed for TythonApiService
        blueprint_package_path='',
        mode=None,
    ))

    # we get a validation request id, but the validation hasn't actually been triggered on oak9 yet
    validation_request_id = tython_api_service.build_app()

    preview_command_args = PreviewCommandArguments(
        oak9_validation_request_id=validation_request_id,
        blueprints_suite_absolute_path=arguments.blueprints_suite_absolute_path,
        oak9_api_key=arguments.oak9_api_key,
        oak9_api_url=arguments.oak9_api_url,
        oak9_org_id=arguments.oak9_org_id,
        oak9_project_id=arguments.oak9_project_id,
        oak9_environment_id=arguments.oak9_environment_id,
    )

    preview_result = execute_preview(preview_command_args)

    # submit our local findings to oak9, and trigger a validation on oak9
    findings = BlueprintRunResult.get_flattened_findings(preview_result.blueprints_results)
    tython_api_service.apply_findings(findings, validation_request_id)

    return ApplyCommandResult(
        blueprint_classes=preview_result.blueprint_classes,
        blueprints_results=preview_result.blueprints_results,
        runner_inputs=preview_result.runner_inputs,
        request_id=validation_request_id
    )

