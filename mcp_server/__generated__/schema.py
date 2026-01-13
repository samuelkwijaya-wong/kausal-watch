from typing import Optional, Annotated, Literal, Union, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class ActionContactPersonRole(str, Enum):
    """An enumeration."""
    EDITOR = 'EDITOR'
    'Editor'
    MODERATOR = 'MODERATOR'
    'Moderator'

class ActionDateFormat(str, Enum):
    """An enumeration."""
    FULL = 'FULL'
    'Day, month and year (31.12.2020)'
    MONTH_YEAR = 'MONTH_YEAR'
    'Month and year (12.2020)'
    YEAR = 'YEAR'
    'Year (2020)'

class ActionIndicatorEffectType(str, Enum):
    """An enumeration."""
    INCREASES = 'INCREASES'
    'increases'
    DECREASES = 'DECREASES'
    'decreases'

class ActionResponsiblePartyRole(str, Enum):
    """An enumeration."""
    NONE = 'NONE'
    'Unspecified'
    PRIMARY = 'PRIMARY'
    'Primary responsible party'
    COLLABORATOR = 'COLLABORATOR'
    'Collaborator'

class ActionStatusSummaryIdentifier(str, Enum):
    """An enumeration."""
    COMPLETED = 'COMPLETED'
    ON_TIME = 'ON_TIME'
    IN_PROGRESS = 'IN_PROGRESS'
    NOT_STARTED = 'NOT_STARTED'
    LATE = 'LATE'
    CANCELLED = 'CANCELLED'
    OUT_OF_SCOPE = 'OUT_OF_SCOPE'
    MERGED = 'MERGED'
    POSTPONED = 'POSTPONED'
    UNDEFINED = 'UNDEFINED'

class ActionTaskState(str, Enum):
    """An enumeration."""
    NOT_STARTED = 'NOT_STARTED'
    'not started'
    IN_PROGRESS = 'IN_PROGRESS'
    'in progress'
    COMPLETED = 'COMPLETED'
    'completed'
    CANCELLED = 'CANCELLED'
    'cancelled'

class ActionTimelinessIdentifier(str, Enum):
    """An enumeration."""
    OPTIMAL = 'OPTIMAL'
    ACCEPTABLE = 'ACCEPTABLE'
    LATE = 'LATE'
    STALE = 'STALE'

class ActionVisibility(str, Enum):
    """An enumeration."""
    INTERNAL = 'INTERNAL'
    'Internal'
    PUBLIC = 'PUBLIC'
    'Public'

class AttributeTypeFormat(str, Enum):
    """An enumeration."""
    ORDERED_CHOICE = 'ORDERED_CHOICE'
    'Ordered choice'
    OPTIONAL_CHOICE = 'OPTIONAL_CHOICE'
    'Optional choice with optional text'
    UNORDERED_CHOICE = 'UNORDERED_CHOICE'
    'Choice'
    TEXT = 'TEXT'
    'Text'
    RICH_TEXT = 'RICH_TEXT'
    'Rich text'
    NUMERIC = 'NUMERIC'
    'Numeric'
    CATEGORY_CHOICE = 'CATEGORY_CHOICE'
    'Category'

class Comparison(str, Enum):
    """An enumeration."""
    LTE = 'LTE'
    GT = 'GT'

class PlanFeaturesContactPersonsPublicData(str, Enum):
    """An enumeration."""
    NONE = 'NONE'
    'Do not show contact persons publicly'
    NAME = 'NAME'
    'Show only name, role and affiliation'
    ALL = 'ALL'
    'Show all information'
    ALL_FOR_AUTHENTICATED = 'ALL_FOR_AUTHENTICATED'
    'Show all information but only for authenticated users'

class Sentiment(str, Enum):
    """An enumeration."""
    POSITIVE = 'POSITIVE'
    NEGATIVE = 'NEGATIVE'
    NEUTRAL = 'NEUTRAL'

class MCPUserDetailsMe(BaseModel):
    """No documentation"""
    typename: Literal['User'] = Field(alias='__typename', default='User')
    id: str
    uuid: str
    email: str
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    is_superuser: bool = Field(alias='isSuperuser')

class MCPUserDetails(BaseModel):
    """No documentation found for this operation."""
    me: Optional[MCPUserDetailsMe] = Field(default=None)
    'The current user'

    class Arguments(BaseModel):
        """Arguments for MCPUserDetails """
        model_config = ConfigDict(populate_by_name=None)

    class Meta:
        """Meta class for MCPUserDetails """
        document = 'query MCPUserDetails {\n  me {\n    id\n    uuid\n    email\n    firstName\n    lastName\n    isSuperuser\n    __typename\n  }\n}'

class MCPListPlansPlans(BaseModel):
    """The Action Plan under monitoring.

Most information in this service is linked to a Plan."""
    typename: Literal['Plan'] = Field(alias='__typename', default='Plan')
    id: str
    identifier: str
    'A unique identifier for the plan used internally to distinguish between plans. This becomes part of the test site URL: https://[identifier].watch-test.kausal.tech. Use lowercase letters and dashes.'
    name: str
    'The official plan name in full form'
    short_name: Optional[str] = Field(default=None, alias='shortName')
    'A shorter version of the plan name'
    version_name: str = Field(alias='versionName')
    'If this plan has multiple versions, name of this version'
    primary_language: str = Field(alias='primaryLanguage')
    other_languages: List[str] = Field(alias='otherLanguages')
    published_at: Optional[datetime] = Field(default=None, alias='publishedAt')
    view_url: Optional[str] = Field(default=None, alias='viewUrl')

class MCPListPlans(BaseModel):
    """No documentation found for this operation."""
    plans: Optional[List[MCPListPlansPlans]] = Field(default=None)

    class Arguments(BaseModel):
        """Arguments for MCPListPlans """
        model_config = ConfigDict(populate_by_name=None)

    class Meta:
        """Meta class for MCPListPlans """
        document = 'query MCPListPlans {\n  plans {\n    id\n    identifier\n    name\n    shortName\n    versionName\n    primaryLanguage\n    otherLanguages\n    publishedAt\n    viewUrl\n    __typename\n  }\n}'

class MCPListActionsPlanactionsStatus(BaseModel):
    """The current status for the action ("on time", "late", "completed", etc.)."""
    typename: Literal['ActionStatus'] = Field(alias='__typename', default='ActionStatus')
    id: str
    identifier: str
    name: str
    is_completed: bool = Field(alias='isCompleted')

class MCPListActionsPlanactionsImplementationphase(BaseModel):
    """No documentation"""
    typename: Literal['ActionImplementationPhase'] = Field(alias='__typename', default='ActionImplementationPhase')
    id: str
    identifier: str
    name: str

class MCPListActionsPlanactionsStatussummary(BaseModel):
    """No documentation"""
    typename: Literal['ActionStatusSummary'] = Field(alias='__typename', default='ActionStatusSummary')
    identifier: ActionStatusSummaryIdentifier
    label: str
    sentiment: Sentiment
    is_active: bool = Field(alias='isActive')
    is_completed: bool = Field(alias='isCompleted')

class MCPListActionsPlanactionsResponsiblepartiesOrganization(BaseModel):
    """No documentation"""
    typename: Literal['Organization'] = Field(alias='__typename', default='Organization')
    id: str
    name: str
    'Full name of the organization'
    abbreviation: Optional[str] = Field(default=None)
    'Short version or abbreviation of the organization name to be displayed when it is not necessary to show the full name'

class MCPListActionsPlanactionsResponsibleparties(BaseModel):
    """No documentation"""
    typename: Literal['ActionResponsibleParty'] = Field(alias='__typename', default='ActionResponsibleParty')
    id: str
    organization: MCPListActionsPlanactionsResponsiblepartiesOrganization

class MCPListActionsPlanactionsPrimaryorg(BaseModel):
    """No documentation"""
    typename: Literal['Organization'] = Field(alias='__typename', default='Organization')
    id: str
    name: str
    'Full name of the organization'
    abbreviation: Optional[str] = Field(default=None)
    'Short version or abbreviation of the organization name to be displayed when it is not necessary to show the full name'

class MCPListActionsPlanactionsCategoriesType(BaseModel):
    """Type of the categories.

Is used to group categories together. One action plan can have several
category types."""
    typename: Literal['CategoryType'] = Field(alias='__typename', default='CategoryType')
    id: str
    identifier: str
    name: str

class MCPListActionsPlanactionsCategories(BaseModel):
    """A category for actions and indicators."""
    typename: Literal['Category'] = Field(alias='__typename', default='Category')
    id: str
    identifier: str
    name: str
    type: MCPListActionsPlanactionsCategoriesType

class MCPListActionsPlanactions(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str
    official_name: Optional[str] = Field(default=None, alias='officialName')
    'The name as approved by an official party'
    completion: Optional[int] = Field(default=None)
    'The completion percentage for this action'
    schedule_continuous: bool = Field(alias='scheduleContinuous')
    'Set if the action does not have a start or an end date'
    start_date: Optional[str] = Field(default=None, alias='startDate')
    'The date when implementation of this action starts'
    end_date: Optional[str] = Field(default=None, alias='endDate')
    'The date when implementation of this action ends'
    updated_at: datetime = Field(alias='updatedAt')
    status: Optional[MCPListActionsPlanactionsStatus] = Field(default=None)
    implementation_phase: Optional[MCPListActionsPlanactionsImplementationphase] = Field(default=None, alias='implementationPhase')
    status_summary: MCPListActionsPlanactionsStatussummary = Field(alias='statusSummary')
    responsible_parties: List[MCPListActionsPlanactionsResponsibleparties] = Field(alias='responsibleParties')
    primary_org: Optional[MCPListActionsPlanactionsPrimaryorg] = Field(default=None, alias='primaryOrg')
    categories: List[MCPListActionsPlanactionsCategories]

class MCPListActions(BaseModel):
    """No documentation found for this operation."""
    plan_actions: Optional[List[MCPListActionsPlanactions]] = Field(default=None, alias='planActions')

    class Arguments(BaseModel):
        """Arguments for MCPListActions """
        plan: str
        category: Optional[str] = Field(default=None)
        first: Optional[int] = Field(default=None)
        order_by: Optional[str] = Field(alias='orderBy', default=None)
        model_config = ConfigDict(populate_by_name=None)

    class Meta:
        """Meta class for MCPListActions """
        document = 'query MCPListActions($plan: ID!, $category: ID, $first: Int, $orderBy: String) @context(input: {identifier: $plan}) {\n  planActions(plan: $plan, category: $category, first: $first, orderBy: $orderBy) {\n    id\n    identifier\n    name\n    officialName\n    completion\n    scheduleContinuous\n    startDate\n    endDate\n    updatedAt\n    status {\n      id\n      identifier\n      name\n      isCompleted\n      __typename\n    }\n    implementationPhase {\n      id\n      identifier\n      name\n      __typename\n    }\n    statusSummary {\n      identifier\n      label\n      sentiment\n      isActive\n      isCompleted\n      __typename\n    }\n    responsibleParties {\n      id\n      organization {\n        id\n        name\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    primaryOrg {\n      id\n      name\n      abbreviation\n      __typename\n    }\n    categories {\n      id\n      identifier\n      name\n      type {\n        id\n        identifier\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}'

class MCPGetPlanPlanFeatures(BaseModel):
    """No documentation"""
    typename: Literal['PlanFeatures'] = Field(alias='__typename', default='PlanFeatures')
    public_contact_persons: bool = Field(alias='publicContactPersons')
    has_action_identifiers: bool = Field(alias='hasActionIdentifiers')
    'Set if the plan uses meaningful action identifiers'
    has_action_official_name: bool = Field(alias='hasActionOfficialName')
    'Set if the plan uses the official name field'
    has_action_lead_paragraph: bool = Field(alias='hasActionLeadParagraph')
    'Set if the plan uses the lead paragraph field'
    has_action_primary_orgs: bool = Field(alias='hasActionPrimaryOrgs')
    'Set if actions have a clear primary organization (such as multi-city plans)'
    enable_search: bool = Field(alias='enableSearch')
    'Enable site-wide search functionality'
    enable_indicator_comparison: bool = Field(alias='enableIndicatorComparison')
    'Set to enable comparing indicators between organizations'
    minimal_statuses: bool = Field(alias='minimalStatuses')
    "Set to prevent showing status-specific graphs and other elements if statuses aren't systematically used in this action plan"
    contact_persons_public_data: PlanFeaturesContactPersonsPublicData = Field(alias='contactPersonsPublicData')
    'Choose which information about contact persons is visible in the public UI'

class MCPGetPlanPlanCategorytypes(BaseModel):
    """Type of the categories.

Is used to group categories together. One action plan can have several
category types."""
    typename: Literal['CategoryType'] = Field(alias='__typename', default='CategoryType')
    id: str
    identifier: str
    name: str
    usable_for_actions: bool = Field(alias='usableForActions')
    usable_for_indicators: bool = Field(alias='usableForIndicators')

class MCPGetPlanPlanActionstatussummaries(BaseModel):
    """No documentation"""
    typename: Literal['ActionStatusSummary'] = Field(alias='__typename', default='ActionStatusSummary')
    identifier: ActionStatusSummaryIdentifier
    label: str
    is_active: bool = Field(alias='isActive')
    is_completed: bool = Field(alias='isCompleted')
    sentiment: Sentiment

class MCPGetPlanPlanActionattributetypesUnit(BaseModel):
    """No documentation"""
    typename: Literal['Unit'] = Field(alias='__typename', default='Unit')
    id: str
    short_name: Optional[str] = Field(default=None, alias='shortName')

class MCPGetPlanPlanActionattributetypesChoiceoptions(BaseModel):
    """No documentation"""
    typename: Literal['AttributeTypeChoiceOption'] = Field(alias='__typename', default='AttributeTypeChoiceOption')
    id: str
    identifier: str
    name: str

class MCPGetPlanPlanActionattributetypes(BaseModel):
    """No documentation"""
    typename: Literal['AttributeType'] = Field(alias='__typename', default='AttributeType')
    id: str
    identifier: str
    name: str
    format: AttributeTypeFormat
    unit: Optional[MCPGetPlanPlanActionattributetypesUnit] = Field(default=None)
    choice_options: List[MCPGetPlanPlanActionattributetypesChoiceoptions] = Field(alias='choiceOptions')

class MCPGetPlanPlan(BaseModel):
    """The Action Plan under monitoring.

Most information in this service is linked to a Plan."""
    typename: Literal['Plan'] = Field(alias='__typename', default='Plan')
    id: str
    identifier: str
    'A unique identifier for the plan used internally to distinguish between plans. This becomes part of the test site URL: https://[identifier].watch-test.kausal.tech. Use lowercase letters and dashes.'
    name: str
    'The official plan name in full form'
    short_name: Optional[str] = Field(default=None, alias='shortName')
    'A shorter version of the plan name'
    version_name: str = Field(alias='versionName')
    'If this plan has multiple versions, name of this version'
    primary_language: str = Field(alias='primaryLanguage')
    other_languages: List[str] = Field(alias='otherLanguages')
    published_at: Optional[datetime] = Field(default=None, alias='publishedAt')
    view_url: Optional[str] = Field(default=None, alias='viewUrl')
    accessibility_statement_url: Optional[str] = Field(default=None, alias='accessibilityStatementUrl')
    external_feedback_url: Optional[str] = Field(default=None, alias='externalFeedbackUrl')
    "If not empty, the system's built-in user feedback feature will be replaced by a link to an external feedback form available at this web address."
    features: MCPGetPlanPlanFeatures
    category_types: List[MCPGetPlanPlanCategorytypes] = Field(alias='categoryTypes')
    action_status_summaries: List[MCPGetPlanPlanActionstatussummaries] = Field(alias='actionStatusSummaries')
    action_attribute_types: List[MCPGetPlanPlanActionattributetypes] = Field(alias='actionAttributeTypes')

class MCPGetPlan(BaseModel):
    """No documentation found for this operation."""
    plan: Optional[MCPGetPlanPlan] = Field(default=None)

    class Arguments(BaseModel):
        """Arguments for MCPGetPlan """
        identifier: str
        model_config = ConfigDict(populate_by_name=None)

    class Meta:
        """Meta class for MCPGetPlan """
        document = 'query MCPGetPlan($identifier: ID!) @context(input: {identifier: $identifier}) {\n  plan(id: $identifier) {\n    id\n    identifier\n    name\n    shortName\n    versionName\n    primaryLanguage\n    otherLanguages\n    publishedAt\n    viewUrl\n    accessibilityStatementUrl\n    externalFeedbackUrl\n    features {\n      publicContactPersons\n      hasActionIdentifiers\n      hasActionOfficialName\n      hasActionLeadParagraph\n      hasActionPrimaryOrgs\n      enableSearch\n      enableIndicatorComparison\n      minimalStatuses\n      contactPersonsPublicData\n      __typename\n    }\n    categoryTypes {\n      id\n      identifier\n      name\n      usableForActions\n      usableForIndicators\n      __typename\n    }\n    actionStatusSummaries {\n      identifier\n      label\n      isActive\n      isCompleted\n      sentiment\n      __typename\n    }\n    actionAttributeTypes {\n      id\n      identifier\n      name\n      format\n      unit {\n        id\n        shortName\n        __typename\n      }\n      choiceOptions {\n        id\n        identifier\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}'

class MCPGetActionActionStatus(BaseModel):
    """The current status for the action ("on time", "late", "completed", etc.)."""
    typename: Literal['ActionStatus'] = Field(alias='__typename', default='ActionStatus')
    id: str
    identifier: str
    name: str
    is_completed: bool = Field(alias='isCompleted')

class MCPGetActionActionImplementationphase(BaseModel):
    """No documentation"""
    typename: Literal['ActionImplementationPhase'] = Field(alias='__typename', default='ActionImplementationPhase')
    id: str
    identifier: str
    name: str

class MCPGetActionActionStatussummary(BaseModel):
    """No documentation"""
    typename: Literal['ActionStatusSummary'] = Field(alias='__typename', default='ActionStatusSummary')
    identifier: ActionStatusSummaryIdentifier
    label: str
    sentiment: Sentiment
    is_active: bool = Field(alias='isActive')
    is_completed: bool = Field(alias='isCompleted')

class MCPGetActionActionTimeliness(BaseModel):
    """No documentation"""
    typename: Literal['ActionTimeliness'] = Field(alias='__typename', default='ActionTimeliness')
    identifier: ActionTimelinessIdentifier
    comparison: Comparison
    days: int

class MCPGetActionActionImpact(BaseModel):
    """An impact classification for an action in an action plan."""
    typename: Literal['ActionImpact'] = Field(alias='__typename', default='ActionImpact')
    id: str
    identifier: str
    name: str

class MCPGetActionActionPrimaryorg(BaseModel):
    """No documentation"""
    typename: Literal['Organization'] = Field(alias='__typename', default='Organization')
    id: str
    name: str
    'Full name of the organization'
    abbreviation: Optional[str] = Field(default=None)
    'Short version or abbreviation of the organization name to be displayed when it is not necessary to show the full name'

class MCPGetActionActionResponsiblepartiesOrganization(BaseModel):
    """No documentation"""
    typename: Literal['Organization'] = Field(alias='__typename', default='Organization')
    id: str
    name: str
    'Full name of the organization'
    abbreviation: Optional[str] = Field(default=None)
    'Short version or abbreviation of the organization name to be displayed when it is not necessary to show the full name'

class MCPGetActionActionResponsibleparties(BaseModel):
    """No documentation"""
    typename: Literal['ActionResponsibleParty'] = Field(alias='__typename', default='ActionResponsibleParty')
    id: str
    role: Optional[ActionResponsiblePartyRole] = Field(default=None)
    specifier: str
    'The responsibility domain for the organization'
    organization: MCPGetActionActionResponsiblepartiesOrganization

class MCPGetActionActionCategoriesType(BaseModel):
    """Type of the categories.

Is used to group categories together. One action plan can have several
category types."""
    typename: Literal['CategoryType'] = Field(alias='__typename', default='CategoryType')
    id: str
    identifier: str
    name: str

class MCPGetActionActionCategories(BaseModel):
    """A category for actions and indicators."""
    typename: Literal['Category'] = Field(alias='__typename', default='Category')
    id: str
    identifier: str
    name: str
    type: MCPGetActionActionCategoriesType

class MCPGetActionActionContactpersonsPersonOrganization(BaseModel):
    """No documentation"""
    typename: Literal['Organization'] = Field(alias='__typename', default='Organization')
    id: str
    name: str
    'Full name of the organization'
    abbreviation: Optional[str] = Field(default=None)
    'Short version or abbreviation of the organization name to be displayed when it is not necessary to show the full name'

class MCPGetActionActionContactpersonsPerson(BaseModel):
    """No documentation"""
    typename: Literal['Person'] = Field(alias='__typename', default='Person')
    id: str
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    title: Optional[str] = Field(default=None)
    'Job title or role of this person'
    email: str
    organization: MCPGetActionActionContactpersonsPersonOrganization

class MCPGetActionActionContactpersons(BaseModel):
    """A Person acting as a contact for an action."""
    typename: Literal['ActionContactPerson'] = Field(alias='__typename', default='ActionContactPerson')
    id: str
    role: ActionContactPersonRole
    primary_contact: bool = Field(alias='primaryContact')
    'Is this person the primary contact person for the action?'
    person: MCPGetActionActionContactpersonsPerson

class MCPGetActionActionTasks(BaseModel):
    """A task that should be completed during the execution of an action.

The task will have at least a name and an estimate of the due date."""
    typename: Literal['ActionTask'] = Field(alias='__typename', default='ActionTask')
    id: str
    name: str
    state: ActionTaskState
    due_at: str = Field(alias='dueAt')
    'The date by which the task should be completed (deadline)'
    completed_at: Optional[str] = Field(default=None, alias='completedAt')
    'The date when the task was completed'
    comment: Optional[str] = Field(default=None)

class MCPGetActionActionRelatedindicatorsIndicatorUnit(BaseModel):
    """No documentation"""
    typename: Literal['Unit'] = Field(alias='__typename', default='Unit')
    id: str
    name: str
    short_name: Optional[str] = Field(default=None, alias='shortName')

class MCPGetActionActionRelatedindicatorsIndicatorLatestvalue(BaseModel):
    """One measurement of an indicator for a certain date/month/year."""
    typename: Literal['IndicatorValue'] = Field(alias='__typename', default='IndicatorValue')
    id: str
    date: Optional[str] = Field(default=None)
    value: float

class MCPGetActionActionRelatedindicatorsIndicator(BaseModel):
    """An indicator with which to measure actions and progress towards strategic goals."""
    typename: Literal['Indicator'] = Field(alias='__typename', default='Indicator')
    id: str
    identifier: Optional[str] = Field(default=None)
    name: str
    unit: MCPGetActionActionRelatedindicatorsIndicatorUnit
    latest_value: Optional[MCPGetActionActionRelatedindicatorsIndicatorLatestvalue] = Field(default=None, alias='latestValue')

class MCPGetActionActionRelatedindicators(BaseModel):
    """Link between an action and an indicator."""
    typename: Literal['ActionIndicator'] = Field(alias='__typename', default='ActionIndicator')
    id: str
    effect_type: ActionIndicatorEffectType = Field(alias='effectType')
    'What type of effect should the action cause?'
    indicates_action_progress: bool = Field(alias='indicatesActionProgress')
    'Set if the indicator should be used to determine action progress'
    indicator: MCPGetActionActionRelatedindicatorsIndicator

class MCPGetActionActionLinks(BaseModel):
    """A link related to an action."""
    typename: Literal['ActionLink'] = Field(alias='__typename', default='ActionLink')
    id: str
    url: str
    title: str

class MCPGetActionActionStatusupdatesAuthor(BaseModel):
    """No documentation"""
    typename: Literal['Person'] = Field(alias='__typename', default='Person')
    id: str
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')

class MCPGetActionActionStatusupdates(BaseModel):
    """No documentation"""
    typename: Literal['ActionStatusUpdate'] = Field(alias='__typename', default='ActionStatusUpdate')
    id: str
    title: str
    date: str
    content: str
    author: Optional[MCPGetActionActionStatusupdatesAuthor] = Field(default=None)

class MCPGetActionActionRelatedactions(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionMergedwith(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionMergedactions(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionSupersededby(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionSupersededactions(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionAlldependencyrelationshipsPreceding(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionAlldependencyrelationshipsDependent(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str

class MCPGetActionActionAlldependencyrelationships(BaseModel):
    """No documentation"""
    typename: Literal['ActionDependencyRelationship'] = Field(alias='__typename', default='ActionDependencyRelationship')
    preceding: MCPGetActionActionAlldependencyrelationshipsPreceding
    dependent: MCPGetActionActionAlldependencyrelationshipsDependent

class MCPGetActionActionImpactgroupsGroup(BaseModel):
    """No documentation"""
    typename: Literal['ImpactGroup'] = Field(alias='__typename', default='ImpactGroup')
    id: str
    identifier: str
    name: str

class MCPGetActionActionImpactgroupsImpact(BaseModel):
    """An impact classification for an action in an action plan."""
    typename: Literal['ActionImpact'] = Field(alias='__typename', default='ActionImpact')
    id: str
    identifier: str

class MCPGetActionActionImpactgroups(BaseModel):
    """No documentation"""
    typename: Literal['ImpactGroupAction'] = Field(alias='__typename', default='ImpactGroupAction')
    id: str
    group: MCPGetActionActionImpactgroupsGroup
    impact: MCPGetActionActionImpactgroupsImpact

class MCPGetActionActionAttributesTypeUnit(BaseModel):
    """No documentation"""
    typename: Literal['Unit'] = Field(alias='__typename', default='Unit')
    short_name: Optional[str] = Field(default=None, alias='shortName')

class MCPGetActionActionAttributesType(BaseModel):
    """No documentation"""
    typename: Literal['AttributeType'] = Field(alias='__typename', default='AttributeType')
    identifier: str
    name: str
    unit: Optional[MCPGetActionActionAttributesTypeUnit] = Field(default=None)

class MCPGetActionActionAttributesCategoriesType(BaseModel):
    """Type of the categories.

Is used to group categories together. One action plan can have several
category types."""
    typename: Literal['CategoryType'] = Field(alias='__typename', default='CategoryType')
    identifier: str

class MCPGetActionActionAttributesCategories(BaseModel):
    """A category for actions and indicators."""
    typename: Literal['Category'] = Field(alias='__typename', default='Category')
    identifier: str
    type: MCPGetActionActionAttributesCategoriesType

class MCPGetActionActionAttributesChoice(BaseModel):
    """No documentation"""
    typename: Literal['AttributeTypeChoiceOption'] = Field(alias='__typename', default='AttributeTypeChoiceOption')
    identifier: str

class MCPGetActionActionAttributesBase(BaseModel):
    """No documentation"""
    type: MCPGetActionActionAttributesType
    key_identifier: str = Field(alias='keyIdentifier')

class MCPGetActionActionAttributesBaseAttributeCategoryChoice(MCPGetActionActionAttributesBase, BaseModel):
    """No documentation"""
    typename: Literal['AttributeCategoryChoice'] = Field(alias='__typename', default='AttributeCategoryChoice')
    categories: List[MCPGetActionActionAttributesCategories]

class MCPGetActionActionAttributesBaseAttributeChoice(MCPGetActionActionAttributesBase, BaseModel):
    """No documentation"""
    typename: Literal['AttributeChoice'] = Field(alias='__typename', default='AttributeChoice')
    choice: Optional[MCPGetActionActionAttributesChoice] = Field(default=None)

class MCPGetActionActionAttributesBaseAttributeNumericValue(MCPGetActionActionAttributesBase, BaseModel):
    """No documentation"""
    typename: Literal['AttributeNumericValue'] = Field(alias='__typename', default='AttributeNumericValue')
    numeric_value: float = Field(alias='numericValue')

class MCPGetActionActionAttributesBaseAttributeRichText(MCPGetActionActionAttributesBase, BaseModel):
    """No documentation"""
    typename: Literal['AttributeRichText'] = Field(alias='__typename', default='AttributeRichText')
    rich_text_value: str = Field(alias='richTextValue')

class MCPGetActionActionAttributesBaseAttributeText(MCPGetActionActionAttributesBase, BaseModel):
    """No documentation"""
    typename: Literal['AttributeText'] = Field(alias='__typename', default='AttributeText')
    text_value: str = Field(alias='textValue')

class MCPGetActionActionAttributesBaseCatchAll(MCPGetActionActionAttributesBase, BaseModel):
    """Catch all class for MCPGetActionActionAttributesBase"""
    typename: str = Field(alias='__typename')

class MCPGetActionAction(BaseModel):
    """One action/measure tracked in an action plan."""
    typename: Literal['Action'] = Field(alias='__typename', default='Action')
    id: str
    uuid: str
    identifier: str
    'The identifier for this action (e.g. number)'
    name: str
    official_name: Optional[str] = Field(default=None, alias='officialName')
    'The name as approved by an official party'
    lead_paragraph: str = Field(alias='leadParagraph')
    description: Optional[str] = Field(default=None)
    'What does this action involve in more detail?'
    start_date: Optional[str] = Field(default=None, alias='startDate')
    'The date when implementation of this action starts'
    end_date: Optional[str] = Field(default=None, alias='endDate')
    'The date when implementation of this action ends'
    schedule_continuous: bool = Field(alias='scheduleContinuous')
    'Set if the action does not have a start or an end date'
    date_format: Optional[ActionDateFormat] = Field(default=None, alias='dateFormat')
    'Format of action start and end dates shown in the public UI.             The default for all actions can be specified on the actions page.'
    updated_at: datetime = Field(alias='updatedAt')
    completion: Optional[int] = Field(default=None)
    'The completion percentage for this action'
    manual_status_reason: Optional[str] = Field(default=None, alias='manualStatusReason')
    'Describe the reason why this action has this status'
    status: Optional[MCPGetActionActionStatus] = Field(default=None)
    implementation_phase: Optional[MCPGetActionActionImplementationphase] = Field(default=None, alias='implementationPhase')
    status_summary: MCPGetActionActionStatussummary = Field(alias='statusSummary')
    timeliness: MCPGetActionActionTimeliness
    color: Optional[str] = Field(default=None)
    impact: Optional[MCPGetActionActionImpact] = Field(default=None)
    'The impact of this action'
    primary_org: Optional[MCPGetActionActionPrimaryorg] = Field(default=None, alias='primaryOrg')
    responsible_parties: List[MCPGetActionActionResponsibleparties] = Field(alias='responsibleParties')
    categories: List[MCPGetActionActionCategories]
    contact_persons: List[MCPGetActionActionContactpersons] = Field(alias='contactPersons')
    tasks: List[MCPGetActionActionTasks]
    related_indicators: List[MCPGetActionActionRelatedindicators] = Field(alias='relatedIndicators')
    links: List[MCPGetActionActionLinks]
    status_updates: List[MCPGetActionActionStatusupdates] = Field(alias='statusUpdates')
    related_actions: List[MCPGetActionActionRelatedactions] = Field(alias='relatedActions')
    merged_with: Optional[MCPGetActionActionMergedwith] = Field(default=None, alias='mergedWith')
    'Set if this action is merged with another action'
    merged_actions: List[MCPGetActionActionMergedactions] = Field(alias='mergedActions')
    'Set if this action is merged with another action'
    superseded_by: Optional[MCPGetActionActionSupersededby] = Field(default=None, alias='supersededBy')
    'Set if this action is superseded by another action'
    superseded_actions: List[MCPGetActionActionSupersededactions] = Field(alias='supersededActions')
    'Set if this action is superseded by another action'
    all_dependency_relationships: List[MCPGetActionActionAlldependencyrelationships] = Field(alias='allDependencyRelationships')
    impact_groups: List[MCPGetActionActionImpactgroups] = Field(alias='impactGroups')
    attributes: List[Union[Annotated[Union[MCPGetActionActionAttributesBaseAttributeCategoryChoice, MCPGetActionActionAttributesBaseAttributeChoice, MCPGetActionActionAttributesBaseAttributeNumericValue, MCPGetActionActionAttributesBaseAttributeRichText, MCPGetActionActionAttributesBaseAttributeText], Field(discriminator='typename')], MCPGetActionActionAttributesBaseCatchAll]]
    visibility: ActionVisibility
    order: int
    view_url: str = Field(alias='viewUrl')

class MCPGetAction(BaseModel):
    """No documentation found for this operation."""
    action: Optional[MCPGetActionAction] = Field(default=None)

    class Arguments(BaseModel):
        """Arguments for MCPGetAction """
        plan: str
        identifier: str
        model_config = ConfigDict(populate_by_name=None)

    class Meta:
        """Meta class for MCPGetAction """
        document = 'query MCPGetAction($plan: ID!, $identifier: ID!) @context(input: {identifier: $plan}) {\n  action(plan: $plan, identifier: $identifier) {\n    id\n    uuid\n    identifier\n    name\n    officialName\n    leadParagraph\n    description\n    startDate\n    endDate\n    scheduleContinuous\n    dateFormat\n    updatedAt\n    completion\n    manualStatusReason\n    status {\n      id\n      identifier\n      name\n      isCompleted\n      __typename\n    }\n    implementationPhase {\n      id\n      identifier\n      name\n      __typename\n    }\n    statusSummary {\n      identifier\n      label\n      sentiment\n      isActive\n      isCompleted\n      __typename\n    }\n    timeliness {\n      identifier\n      comparison\n      days\n      __typename\n    }\n    color\n    impact {\n      id\n      identifier\n      name\n      __typename\n    }\n    primaryOrg {\n      id\n      name\n      abbreviation\n      __typename\n    }\n    responsibleParties {\n      id\n      role\n      specifier\n      organization {\n        id\n        name\n        abbreviation\n        __typename\n      }\n      __typename\n    }\n    categories {\n      id\n      identifier\n      name\n      type {\n        id\n        identifier\n        name\n        __typename\n      }\n      __typename\n    }\n    contactPersons {\n      id\n      role\n      primaryContact\n      person {\n        id\n        firstName\n        lastName\n        title\n        email\n        organization {\n          id\n          name\n          abbreviation\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    tasks {\n      id\n      name\n      state\n      dueAt\n      completedAt\n      comment\n      __typename\n    }\n    relatedIndicators {\n      id\n      effectType\n      indicatesActionProgress\n      indicator {\n        id\n        identifier\n        name\n        unit {\n          id\n          name\n          shortName\n          __typename\n        }\n        latestValue {\n          id\n          date\n          value\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    links {\n      id\n      url\n      title\n      __typename\n    }\n    statusUpdates {\n      id\n      title\n      date\n      content\n      author {\n        id\n        firstName\n        lastName\n        __typename\n      }\n      __typename\n    }\n    relatedActions {\n      id\n      identifier\n      name\n      __typename\n    }\n    mergedWith {\n      id\n      identifier\n      name\n      __typename\n    }\n    mergedActions {\n      id\n      identifier\n      name\n      __typename\n    }\n    supersededBy {\n      id\n      identifier\n      name\n      __typename\n    }\n    supersededActions {\n      id\n      identifier\n      name\n      __typename\n    }\n    allDependencyRelationships {\n      preceding {\n        id\n        identifier\n        name\n        __typename\n      }\n      dependent {\n        id\n        identifier\n        name\n        __typename\n      }\n      __typename\n    }\n    impactGroups {\n      id\n      group {\n        id\n        identifier\n        name\n        __typename\n      }\n      impact {\n        id\n        identifier\n        __typename\n      }\n      __typename\n    }\n    attributes {\n      __typename\n      type {\n        identifier\n        name\n        unit {\n          shortName\n          __typename\n        }\n        __typename\n      }\n      keyIdentifier\n      ... on AttributeText {\n        textValue: value\n      }\n      ... on AttributeRichText {\n        richTextValue: value\n      }\n      ... on AttributeCategoryChoice {\n        categories {\n          identifier\n          type {\n            identifier\n          }\n        }\n      }\n      ... on AttributeNumericValue {\n        numericValue: value\n      }\n      ... on AttributeChoice {\n        choice {\n          identifier\n        }\n      }\n    }\n    visibility\n    order\n    viewUrl\n    __typename\n  }\n}'