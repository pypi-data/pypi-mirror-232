from core.services.tython_api_service import TythonApiService
from core.types import Configuration


def execute_get_resource_infrastructure_from_oak9(
        org_id: str,
        project_id: str,
        env_id: str,
        api_key: str,
        validation_request_id: str = None,
        api_url: str = None
):
    tython_api_service = TythonApiService(Configuration(
        api_key=api_key,
        org_id=org_id,
        project_id=project_id,
        env_id=env_id,
        data_endpoint=api_url,

        # not needed for TythonApiService
        blueprint_package_path='',
        mode=None
    ))

    if not validation_request_id:
        request_id = tython_api_service.build_app()
    else:
        request_id = validation_request_id

    graph_data = tython_api_service.fetch_graph_data(request_id)

    return graph_data
