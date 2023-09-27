import dataclasses
import logging
from typing import List
from typing import Protocol
from typing import Type

from core.bp_metadata_utils.customer_blueprint_repo import CustomerBlueprintRepo
from core.commands.get_classes_of_blueprint_suite import execute_get_classes_of_blueprint_suite
from core.commands.get_resource_infrastructure_from_oak9 import execute_get_resource_infrastructure_from_oak9
from core.commands.run_blueprints import BlueprintRunResult
from core.commands.run_blueprints import execute_run_blueprints
from core.types import Blueprint
from core.types import PropertiesNamesMixin
from models.shared.shared_pb2 import RunnerInput

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PreviewCommandArguments(PropertiesNamesMixin):
    blueprints_suite_absolute_path: str

    # Used to build app arch. Should be removed in the future.
    oak9_api_url: str
    oak9_org_id: str
    oak9_project_id: str
    oak9_environment_id: str
    oak9_api_key: str
    oak9_validation_request_id: str


@dataclasses.dataclass
class PreviewCommandResult:
    blueprint_classes: List[Type[Blueprint]] = dataclasses.field(default_factory=list)
    blueprints_results: List[BlueprintRunResult] = dataclasses.field(default_factory=list)
    runner_inputs: List[RunnerInput] = dataclasses.field(default_factory=list)


def execute_preview(arguments: PreviewCommandArguments) -> PreviewCommandResult:
    """ execute a blueprint suite """
    response = PreviewCommandResult()

    blueprint_repo = CustomerBlueprintRepo(arguments.blueprints_suite_absolute_path)
    response.blueprint_classes = execute_get_classes_of_blueprint_suite(blueprint_repo.blueprint_file_paths)

    if not any(response.blueprint_classes):
        return response

    response.runner_inputs = execute_get_resource_infrastructure_from_oak9(
        org_id=arguments.oak9_org_id,
        project_id=arguments.oak9_project_id,
        env_id=arguments.oak9_environment_id,
        api_key=arguments.oak9_api_key,
        validation_request_id=arguments.oak9_validation_request_id,
        api_url=arguments.oak9_api_url
    )

    if not any(response.runner_inputs):
        logger.debug("Empty resource infrastructure")

    response.blueprints_results = execute_run_blueprints(response.runner_inputs, response.blueprint_classes)

    return response


