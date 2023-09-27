import dataclasses
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, ClassVar, List, Type, TypeVar, Union

from core.proxyobjs import PathTrackerProxy
from core.sdk.resource_map import grpc_type_map
from models.shared.shared_pb2 import Context as Ctx
from models.shared.shared_pb2 import Finding, Graph, ResourceMetadata
from models.shared.shared_pb2 import ValidationMetaInfo as Vmi

ValidationFunction = Callable[[any], any]
T = TypeVar("T", bound=dataclasses.dataclass)


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Csp(Enum):
    Aws = 1
    Azure = 2
    GoogleCloud = 3


class DataSensitivity(OrderedEnum):
    BusinessSensitive = 2
    Public = 1


class BusinessImpact(OrderedEnum):
    High = 3
    Medium = 2
    Low = 1


class DeploymentModel(OrderedEnum):
    Private = 3
    Hybrid = 2
    Public = 1


class ComplianceFramework(Enum):
    AWS_FTR = "AWS.FTR"
    Azure_Benchmarks = "Azure_Benchmarks"
    CSA_CCM = "CSA.CCM"
    Cis_Controls_v8 = "Cis_Controls_v8"
    EU_GDPR = "EU.GDPR"
    FCA = "FCA"
    HIPAA = "HIPAA"
    HITRUST_BUID = "HITRUST.BUID"
    HITRUST_v8_0 = "HITRUST.v8_0"
    HITRUST_v9_4 = "HITRUST.v9_4"
    ISO27001 = "ISO27001"
    Mitre_attack = "Mitre_att&ck"
    NIST_800_53_R4 = "NIST.800-53.R4"
    NIST_800_53_R5 = "NIST.800-53.R5"
    NIST_CSF = "NIST.CSF"
    NRS603A = "NRS603A"
    NYCRR = "23NYCRR"
    PCI_DSS = "PCI.DSS"
    SCIDSA = "SCIDSA"
    SOC2 = "Soc_2"
    TAC = "1TAC"
    CMR17 = "201CMR17"


class Severity(OrderedEnum):
    Critical = 4
    High = 3
    Moderate = 2
    Low = 1


class SecurityLevel(OrderedEnum):
    Best = 3
    Better = 2
    Good = 1


class Context:
    def __init__(self, context: Ctx = None, meta_info: Vmi = None):
        """
        Business context of the architecture being secured

        Args:
            context (context_pb2): The proto context object is passed in and converted into a python object
        """
        required_lower = "required"

        self._compliance_objectives = []

        if meta_info and meta_info.compliance_objectives:
            for objective in meta_info.compliance_objectives:
                try:
                    self._compliance_objectives.append(ComplianceFramework(objective))
                except ValueError:
                    continue

        self._business_impact: BusinessImpact = BusinessImpact.High
        if (
            context
            and context.susceptibility
            and context.susceptibility.business_impact
        ):
            business_impact_str = context.susceptibility.business_impact.lower()
            if business_impact_str == "low":
                self._business_impact: BusinessImpact = BusinessImpact.Low
            elif business_impact_str == "medium":
                self._business_impact: BusinessImpact = BusinessImpact.Medium
            elif business_impact_str == "high":
                self._business_impact: BusinessImpact = BusinessImpact.High
            else:
                self._business_impact: BusinessImpact = BusinessImpact.High

        if (
            context
            and context.susceptibility
            and context.susceptibility.data_sensitivity
        ):
            data_sensitivity_str = context.susceptibility.data_sensitivity.lower()
            if data_sensitivity_str == "public":
                self.data_sensitivity: DataSensitivity = DataSensitivity.Public
            elif data_sensitivity_str == "businesssensitive":
                self.data_sensitivity: DataSensitivity = (
                    DataSensitivity.BusinessSensitive
                )
            else:
                self.data_sensitivity: DataSensitivity = (
                    DataSensitivity.BusinessSensitive
                )
        else:
            self.data_sensitivity: DataSensitivity = DataSensitivity.BusinessSensitive

        if (
            context
            and context.app_architecture
            and context.app_architecture.deployment_model
        ):
            deployment_model_str = context.app_architecture.deployment_model.lower()
            if deployment_model_str == "private":
                self.deployment_model = DeploymentModel.Private
            elif deployment_model_str == "hybrid":
                self.deployment_model = DeploymentModel.Hybrid
            elif deployment_model_str == "public":
                self.deployment_model = DeploymentModel.Public
            else:
                self.deployment_model = DeploymentModel.Public
        else:
            self.deployment_model = DeploymentModel.Public

        if (
            context
            and context.security_architecture
            and context.security_architecture.security_level
        ):
            security_level_str = context.security_architecture.security_level.lower()
            if security_level_str == "best":
                self.security_level = SecurityLevel.Best
            elif security_level_str == "better":
                self.security_level = SecurityLevel.Better
            elif security_level_str == "good":
                self.security_level = SecurityLevel.Good
            else:
                self.security_level = SecurityLevel.Better
        else:
            self.security_level = SecurityLevel.Better

        if (
            context
            and context.accessibility
            and context.accessibility.access_type
            and context.accessibility.access_type.internal_access
            and context.accessibility.access_type.internal_access.lower()
            == required_lower
        ):
            self.internal_access = True
        else:
            self.internal_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.access_type
            and context.accessibility.access_type.external_access
            and context.accessibility.access_type.external_access.lower()
            == required_lower
        ):
            self.external_access = True
        else:
            self.external_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.access_type
            and context.accessibility.access_type.remote_access
            and context.accessibility.access_type.remote_access.lower()
            == required_lower
        ):
            self.remote_access = True
        else:
            self.remote_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.access_type
            and context.accessibility.access_type.outbound_access
            and context.accessibility.access_type.outbound_access.lower()
            == required_lower
        ):
            self.outbound_access = True
        else:
            self.outbound_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.end_users
            and context.accessibility.end_users.workforce
            and context.accessibility.end_users.workforce.lower() == required_lower
        ):
            self.workforce = True
        else:
            self.workforce = False

        if (
            context
            and context.accessibility
            and context.accessibility.end_users
            and context.accessibility.end_users.consumers
            and context.accessibility.end_users.consumers.lower() == required_lower
        ):
            self.consumers = True
        else:
            self.consumers = False

        if (
            context
            and context.accessibility
            and context.accessibility.end_users
            and context.accessibility.end_users.business_partners
            and context.accessibility.end_users.business_partners.lower()
            == required_lower
        ):
            self.business_partners = True
        else:
            self.business_partners = False

        if (
            context
            and context.accessibility
            and context.accessibility.level_of_access
            and context.accessibility.level_of_access.physical
            and context.accessibility.level_of_access.physical.lower() == required_lower
        ):
            self.physical_access = True
        else:
            self.physical_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.level_of_access
            and context.accessibility.level_of_access.open
            and context.accessibility.level_of_access.open.lower() == required_lower
        ):
            self.open_access = True
        else:
            self.open_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.level_of_access
            and context.accessibility.level_of_access.limited_sensitive_data
            and context.accessibility.level_of_access.limited_sensitive_data.lower()
            == required_lower
        ):
            self.limited_sensitive_data_access = True
        else:
            self.limited_sensitive_data_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.level_of_access
            and context.accessibility.level_of_access.broad_sensitive_data
            and context.accessibility.level_of_access.broad_sensitive_data.lower()
            == required_lower
        ):
            self.broad_sensitive_data_access = True
        else:
            self.broad_sensitive_data_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.level_of_access
            and context.accessibility.level_of_access.security_privileged
            and context.accessibility.level_of_access.security_privileged.lower()
            == required_lower
        ):
            self.security_privileged_access = True
        else:
            self.security_privileged_access = False

        if (
            context
            and context.accessibility
            and context.accessibility.applicable_component_slices
            and context.accessibility.applicable_component_slices.component_core
            and context.accessibility.applicable_component_slices.component_core.lower()
            == required_lower
        ):
            self.component_core = True
        else:
            self.component_core = False

        if (
            context
            and context.accessibility
            and context.accessibility.applicable_component_slices
            and context.accessibility.applicable_component_slices.user_interface
            and context.accessibility.applicable_component_slices.user_interface.lower()
            == required_lower
        ):
            self.user_interface = True
        else:
            self.user_interface = False

        if (
            context
            and context.accessibility
            and context.accessibility.applicable_component_slices
            and context.accessibility.applicable_component_slices.management_interface
            and context.accessibility.applicable_component_slices.management_interface.lower()
            == required_lower
        ):
            self.management_interface = True
        else:
            self.management_interface = False

    def is_externally_accessible(self) -> bool:
        if self.external_access and not self.internal_access:
            return True

        return False

    def is_data_sensitive(self) -> bool:
        if self.data_sensitivity == DataSensitivity.BusinessSensitive:
            return True
        return False

    def is_high_impact(self) -> bool:
        if self._business_impact == BusinessImpact.High:
            return True

        return False

    def is_moderate_impact(self) -> bool:
        if self._business_impact == BusinessImpact.Medium:
            return True

        return False

    def is_low_impact(self) -> bool:
        if self._business_impact == BusinessImpact.Low:
            return True

        return False

    def is_business_critical(self) -> bool:
        if (
            self._business_impact == BusinessImpact.High
            and self.data_sensitivity == DataSensitivity.BusinessSensitive
        ):
            return True
        else:
            return False

    def is_high_impact_or_sensitive_data(self) -> bool:
        if (
            self._business_impact == BusinessImpact.High
            or self.data_sensitivity == DataSensitivity.BusinessSensitive
        ):
            return True
        else:
            return False

    def is_sensitive_data(self) -> bool:
        if self.data_sensitivity == DataSensitivity.BusinessSensitive:
            return True
        else:
            return False

    def is_sensitive_and_external(self) -> bool:
        if (
            self.data_sensitivity == DataSensitivity.BusinessSensitive
            and self.external_access
        ):
            return True
        else:
            return False

    def is_sensitive_and_internal(self) -> bool:
        if (
            self.data_sensitivity == DataSensitivity.BusinessSensitive
            and self.internal_access
        ):
            return True
        else:
            return False

    def determine_severity(self) -> Severity:
        if self._business_impact == BusinessImpact.High:
            config_violation_severity = Severity.High

        elif self._business_impact == BusinessImpact.Medium:
            config_violation_severity = Severity.Moderate

        else:
            config_violation_severity = Severity.Low

        return config_violation_severity

    def requires_compliance(self, framework_to_check: ComplianceFramework) -> bool:
        for framework in self._compliance_objectives:
            if framework == framework_to_check:
                return True
        return False

    @property
    def compliance_objectives(self):
        return self._compliance_objectives


class BlueprintType(Enum):
    Component = 1
    Reference = 2
    Solution = 3
    Resource = 4
    Customer = 5


@dataclass
class Resource:
    id: str
    name: str
    csp: Csp
    resource_type: ClassVar[str]
    id: str
    name: str
    blueprint_id: str


class ImpactRating(OrderedEnum):
    Stellar = 5
    Exceptional = 4
    Excellent = 3
    Good = 2
    Ok = 1


class RelatedConfig:
    """
    Related Configs allows the Violation to bundle additional configurations that don't need a separate violation
    and should be remediated together
    """

    config_id: str = ""
    config_value: Union[List, int, str] = ""
    preferred_value: Union[List, int, str] = ""
    comment: str = ""


class Violation:
    """
    Defines a violation object.
    This object is DEPRECATED and is only there for backwards compatibility
    Note that there are required and optional fields
    """

    def __init__(
        self,
        severity: Severity = Severity.Low,
        adjusted_severity: Severity = None,
        config_id: str = "",
        config_value: str = "",
        config_gap: str = "",
        config_impact: str = "",
        config_fix: str = "",
        preferred_value: Union[List, str, int] = "",
        additional_guidance: str = "",
        documentation: str = "",
        related_configs: List[RelatedConfig] = None,
        capability_id: str = "",
        capability_name: str = "",
        resource_id: str = "",
        resource_type: str = "",
        resource_name: str = "",
        priority: int = 0,
    ):
        # Severity of the violation.  Default to low. Severity should be determined based on the business context
        self._severity = severity

        # Adjusted severity of the violation. This field is used to adjust the severity for a mitigating design
        self._adjusted_severity = adjusted_severity

        # the unique id (full path) of the configuration that has the issue
        self.config_id = config_id

        # currently configured value of this configuration
        if type(config_value) != str:
            self.config_value = str(config_value)

        else:
            self.config_value = config_value

        # Description of the gap
        self.config_gap = config_gap

        # Impact of not fixing this violation
        self.config_impact = config_impact

        # Guidance on how to fix the issue
        self.config_fix = config_fix

        # The preferred value
        # Preferred values can be strings, integers, bools, lists, dictionaries
        if type(preferred_value) == list:
            self.preferred_value = ", ".join(preferred_value)

        elif type(preferred_value) != str:
            self.preferred_value = str(preferred_value)

        else:
            self.preferred_value = preferred_value

        # Additional guidance
        self.additional_guidance = additional_guidance

        # Related configurations that should be remediated together
        self.related_configs: List[RelatedConfig] = related_configs

        # oak9 security capability capability id
        self._capability_id = capability_id

        # oak9 detailed capability name
        self._capability_name = capability_name

        # documentation link
        self._documentation = documentation

        # Unique id of the resource
        self._resource_id = resource_id

        # Type of resource
        self._resource_type = resource_type

        # resource name
        self._resource_name = resource_name

        # Priority of finding (1-100)
        # This helps relatively prioritize across qualitative ratings
        self._priority = priority

    def __json__(self):
        return {
            "severity": self.severity.name,
            "configGap": self.config_gap,
            "capabilityId": self.capability_id,
            "configId": self.config_id,
            "configValue": self.config_value,
            "oak9Guidance": self.additional_guidance,
            "prefferedValue": self.preferred_value,
            "capabilityName": self.capability_name,
            "configFix": self.config_fix,
            "configImpact": self.config_impact,
            "resourceId": self.resource_id,
            "resourceType": self.resource_type,
            "resourceName": self.resource_name,
        }

    @property
    def severity(self) -> Severity:
        return self._severity

    @severity.setter
    def severity(self, value):
        if self._adjusted_severity:
            self._severity = self._adjusted_severity
        else:
            self._severity = value

    @property
    def adjusted_severity(self):
        return self._adjusted_severity

    @adjusted_severity.setter
    def adjusted_severity(self, value):
        self._adjusted_severity = value

    @property
    def documentation(self):
        return self._documentation

    @property
    def capability_id(self):
        return self._capability_id

    @capability_id.setter
    def capability_id(self, value):
        self._capability_id = value

    @property
    def capability_name(self):
        return self._capability_name

    @capability_name.setter
    def capability_name(self, value):
        self._capability_name = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if isinstance(value, int) and 101 > value > 0:
            self._priority = value

    @property
    def resource_id(self):
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value):
        self._resource_id = value

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value):
        self._resource_type = value

    @property
    def resource_name(self):
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value):
        self._resource_name = value


@dataclass
class ValidationMetaInfo:
    caller: str
    request_id: str
    resource_type: str
    blueprint_id: str
    resource_name: str
    resource_id: str
    compliance_frameworks: List[str]


class DesignPref:
    pass


class Blueprint:
    """
    Base class for Tython Blueprints
    """

    display_name: ClassVar[str] = None
    blueprint_type: ClassVar[BlueprintType] = BlueprintType.Customer
    id: ClassVar[str] = None
    parent_blueprint_id: ClassVar[str] = None
    version: ClassVar[str] = None

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    @property
    def context(self) -> Context:
        if (
            self._graph
            and self._graph[0]
            and self._graph[0].project_context
            and self._graph[0].meta_info
        ):
            blueprint_context = Context(
                self._graph[0].project_context, self._graph[0].meta_info
            )
            return blueprint_context
        else:
            return Context()

    @property
    def meta_info(self):
        return self._meta_info

    @property
    def graph(self):
        return self._graph

    def validate(self) -> List[Finding]:
        pass

    def find_by_resource(self, resource_type):
        """
        Filters the graph for the given resource_type
        """
        resources = []

        for input in self._graph:
            for root_node in input.graph.root_nodes:
                mapped = grpc_type_map.get(root_node.node.resource.data.type_url)
                if mapped == resource_type:
                    resource = resource_type()
                    root_node.node.resource.data.Unpack(resource)

                    resource_metadata = ResourceMetadata(
                        resource_id=input.meta_info.resource_id,
                        resource_name=input.meta_info.resource_name,
                        resource_type=input.meta_info.resource_type,
                    )
                    resource = PathTrackerProxy.create(resource)

                    resources.append((resource, resource_metadata))

        if not resources:
            logging.debug(
                f"No resources found for the given resource type {resource_type}"
            )

        return resources


@dataclass
class Configuration:
    api_key: str = None
    org_id: str = None
    project_id: str = None
    env_id: str = None
    blueprint_package_path: str = None
    data_endpoint: str = None
    mode: str = None

    def __init__(
        self,
        api_key: str,
        org_id: str,
        project_id: str,
        blueprint_package_path: str,
        env_id: str = None,
        data_endpoint: str = None,
        mode: str = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.org_id = org_id
        self.project_id = project_id
        self.env_id = env_id
        self.blueprint_package_path = blueprint_package_path
        self.data_endpoint = (
            "https://api.oak9.io/console/" if not data_endpoint else data_endpoint
        )
        self.mode = "test" if not mode else mode
        for key, value in kwargs.items():
            setattr(self, key, value)


class PropertiesNamesMixin:
    """
    Used on dataclasses to set the properties' values with the names of those properties.

    This is a trick to avoid having to use magic strings during the CLI argument setup
    for a somewhat more strongly-typed approach.
    """

    @classmethod
    def for_property_names(cls: Type[T]) -> T:
        fields_names = dataclasses.fields(cls)
        constructor_args = {field.name: field.name for field in fields_names}
        return cls(**constructor_args)
