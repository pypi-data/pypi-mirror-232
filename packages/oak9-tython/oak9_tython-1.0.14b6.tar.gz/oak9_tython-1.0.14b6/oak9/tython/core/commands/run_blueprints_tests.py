import unittest

from models.shared.shared_pb2 import Finding
from run_blueprints import BlueprintRunResult


class BlueprintRunResult_GetFlattenedFindings_TestCase(unittest.TestCase):
    def test_empty_findings_is_handled_gracefully(self):
        findings = BlueprintRunResult.get_flattened_findings([])
        self.assertTrue(len(findings) == 0)

    def test_results_with_empty_findings_are_handled_gracefully(self):
        results = [
            BlueprintRunResult(findings=[]),
            BlueprintRunResult(findings=[]),
        ]

        findings = BlueprintRunResult.get_flattened_findings(results)
        self.assertTrue(len(findings) == 0)

    def test_findings_are_flattened(self):
        results = [
            BlueprintRunResult(findings=[Finding()]),
            BlueprintRunResult(findings=[Finding()]),
        ]

        findings = BlueprintRunResult.get_flattened_findings(results)
        self.assertTrue(len(findings) == 2)
