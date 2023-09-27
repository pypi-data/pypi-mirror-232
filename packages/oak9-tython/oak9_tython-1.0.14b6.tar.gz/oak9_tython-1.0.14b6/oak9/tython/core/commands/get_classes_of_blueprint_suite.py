from typing import Iterable

from core.bp_metadata_utils.python_source_file_utils import get_blueprint_classes


def execute_get_classes_of_blueprint_suite(suite_absolute_paths: Iterable[str]):
    """ returns a flat list of blueprint classes found in the specified suites """
    return [bp[1] for path in suite_absolute_paths for bp in get_blueprint_classes(path)]
