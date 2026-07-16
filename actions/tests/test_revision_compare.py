from __future__ import annotations

import datetime
import typing

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from wagtail.admin.panels import FieldPanel, ObjectList

import pytest
from pytest_django.asserts import assertContains

from actions.attributes import (
    AttributeFieldPanel,
    AttributeType as AttributeTypeWrapper,
    DraftAttributes,
    GenericTextAttributeAttributeValue,
)
from actions.models.action import Action, ActionContactPerson, ActionTask
from actions.models.attributes import AttributeType
from actions.revision_compare import get_action_comparisons, get_changed_field_labels
from actions.tests.factories import AttributeTypeFactory
from admin_site.tests.factories import ClientPlanFactory
from admin_site.wagtail import CondensedInlinePanel

if typing.TYPE_CHECKING:
    from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def moderated_action(plan_with_single_task_moderation) -> Action:
    plan = plan_with_single_task_moderation
    # The fixture only sets the moderation workflow on the in-memory features object.
    plan.features.save()
    return plan.actions.get()


@pytest.fixture
def moderator_user(moderated_action, action_contact_factory) -> User:
    acp = action_contact_factory(action=moderated_action, role=ActionContactPerson.Role.MODERATOR)
    return acp.person.user


@pytest.fixture
def editor_user(moderated_action, action_contact_factory) -> User:
    acp = action_contact_factory(action=moderated_action, role=ActionContactPerson.Role.EDITOR)
    return acp.person.user


def _make_draft(action: Action, **changes):
    for field, value in changes.items():
        setattr(action, field, value)
    return action.save_revision()


def _simple_edit_handler(*field_names: str):
    return ObjectList([FieldPanel(field_name) for field_name in field_names]).bind_to_model(Action)


def test_changed_field_labels_reports_modified_fields(moderated_action, moderator_user):
    live = Action.objects.get(pk=moderated_action.pk)
    _make_draft(moderated_action, name='A completely new name', lead_paragraph='New lead paragraph')
    draft = moderated_action.latest_revision.as_object()

    edit_handler = _simple_edit_handler('name', 'lead_paragraph', 'official_name')
    labels = get_changed_field_labels(edit_handler, live, draft, moderator_user)
    assert labels == ['Name', 'Lead paragraph']


def test_field_comparison_shows_old_and_new_value(moderated_action, moderator_user):
    live = Action.objects.get(pk=moderated_action.pk)
    old_name = live.name
    _make_draft(moderated_action, name='A completely new name')
    draft = moderated_action.latest_revision.as_object()

    edit_handler = _simple_edit_handler('name')
    comparisons = get_action_comparisons(edit_handler, live, draft, moderator_user)
    assert len(comparisons) == 1
    diff = comparisons[0].htmldiff()
    assert 'A completely new name' in diff
    assert old_name.split(' ')[-1] in diff


def test_child_relation_comparison_detects_added_task(moderated_action, moderator_user):
    live = Action.objects.get(pk=moderated_action.pk)
    moderated_action.tasks.add(ActionTask(name='Do the thing', state=ActionTask.NOT_STARTED, due_at=datetime.date(2030, 1, 1)))
    moderated_action.save_revision()
    draft = moderated_action.latest_revision.as_object()

    edit_handler = ObjectList([
        CondensedInlinePanel('tasks', panels=[FieldPanel('name'), FieldPanel('state')]),
    ]).bind_to_model(Action)
    comparisons = get_action_comparisons(edit_handler, live, draft, moderator_user)
    assert len(comparisons) == 1
    comparison = comparisons[0]
    assert comparison.is_child_relation
    child_comparisons = comparison.get_child_comparisons()
    assert len(child_comparisons) == 1
    assert child_comparisons[0].is_addition()


def test_attribute_comparison_detects_changed_attribute(plan_with_single_task_moderation, moderated_action, moderator_user):
    plan = plan_with_single_task_moderation
    action_ct = ContentType.objects.get(app_label='actions', model='action')
    plan_ct = ContentType.objects.get(app_label='actions', model='plan')
    attribute_type_model = AttributeTypeFactory.create(
        object_content_type=action_ct,
        scope_content_type=plan_ct,
        scope_id=plan.id,
        name='Extra information',
        format=AttributeType.AttributeFormat.TEXT,
    )
    wrapper: AttributeTypeWrapper[typing.Any] = AttributeTypeWrapper.from_model_instance(attribute_type_model)

    live = Action.objects.get(pk=moderated_action.pk)
    draft_attributes = DraftAttributes()
    draft_attributes.update(wrapper, GenericTextAttributeAttributeValue(text_vals={'text': 'Some new information'}))
    moderated_action.draft_attributes = draft_attributes
    moderated_action.save_revision()
    draft = moderated_action.latest_revision.as_object()

    edit_handler = ObjectList([
        AttributeFieldPanel('name', attribute_type=wrapper, language=''),
    ]).bind_to_model(Action)
    comparisons = get_action_comparisons(edit_handler, live, draft, moderator_user)
    assert len(comparisons) == 1
    comparison = comparisons[0]
    assert comparison.field_label() == 'Extra information'
    assert 'Some new information' in comparison.htmldiff()


def test_compare_view_shows_changes_to_moderator(client, moderated_action, moderator_user):
    ClientPlanFactory(plan=moderated_action.plan)
    old_name = moderated_action.name
    _make_draft(moderated_action, name='A completely new name')

    url = reverse(
        'actions_action_modeladmin_compare',
        kwargs=dict(pk=moderated_action.pk, revision_id_a='live', revision_id_b='latest'),
    )
    client.force_login(moderator_user)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'A completely new name')
    assertContains(response, old_name.split(' ')[-1])
    # The diff markup highlights additions and deletions
    assertContains(response, 'addition')
    assertContains(response, 'deletion')


def test_compare_view_forbidden_for_unrelated_user(client, moderated_action, user_factory):
    ClientPlanFactory(plan=moderated_action.plan)
    _make_draft(moderated_action, name='A completely new name')
    unrelated_user = user_factory()

    url = reverse(
        'actions_action_modeladmin_compare',
        kwargs=dict(pk=moderated_action.pk, revision_id_a='live', revision_id_b='latest'),
    )
    client.force_login(unrelated_user)
    response = client.get(url)
    assert response.status_code in (302, 403)


def test_edit_view_shows_changed_fields_summary(client, moderated_action, moderator_user):
    ClientPlanFactory(plan=moderated_action.plan)
    _make_draft(moderated_action, name='A completely new name')

    url = reverse('actions_action_modeladmin_edit', kwargs=dict(instance_pk=moderated_action.pk))
    client.force_login(moderator_user)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'unpublished changes')
    assertContains(response, 'View changes')


def test_edit_view_shows_no_summary_without_draft_changes(client, moderated_action, moderator_user):
    ClientPlanFactory(plan=moderated_action.plan)

    url = reverse('actions_action_modeladmin_edit', kwargs=dict(instance_pk=moderated_action.pk))
    client.force_login(moderator_user)
    response = client.get(url)
    assert response.status_code == 200
    assert 'unpublished changes' not in response.content.decode('utf-8')
