from __future__ import annotations

import contextlib
import functools
import typing
from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.utils import translation
from django.utils.text import capfirst
from wagtail.admin.compare import ChildRelationComparison, M2MFieldComparison, diff_text
from wagtail.admin.panels import FieldPanel, InlinePanel, PanelGroup

import sentry_sdk
from loguru import logger

from actions.models.action import Action
from admin_site.wagtail import AdminOnlyPanel

if typing.TYPE_CHECKING:
    from collections.abc import Iterator

    from django.db.models import Model
    from django_stubs_ext import StrOrPromise
    from wagtail.admin.compare import FieldComparison
    from wagtail.admin.panels.base import Panel

    from actions.attributes import AttributeFieldPanel, AttributeType as AttributeTypeWrapper, AttributeValue
    from actions.models.attributes import Attribute
    from actions.models.category import CategoryType
    from users.models import User

logger = logger.bind(name='actions.revision_compare')

CATEGORY_FIELD_PREFIX = 'categories_'

# Child model fields that carry ordering or bookkeeping data and should not be compared.
CHILD_RELATION_EXCLUDED_FIELDS = frozenset({'sort_order', 'order'})


def _text_vals_match(text_vals: dict[str, str], attribute: Attribute) -> bool:
    """
    Check draft text values against the corresponding fields of a database attribute.

    Only the languages tracked in the draft are compared, so languages that were not part of
    the form that produced the draft do not cause false positives.
    """
    return all((value or '') == (getattr(attribute, field_name, None) or '') for field_name, value in text_vals.items())


def _draft_value_matches_attribute(value: AttributeValue, attribute: Attribute) -> bool | None:
    """
    Check whether a serialized draft value is equal to a database attribute.

    The comparison uses the underlying values (choice PKs, raw rich text HTML, category PKs)
    rather than the display strings, so changes that are invisible in the display rendering
    (e.g. formatting-only rich text edits) are still detected.

    Returns None for unknown attribute value types, in which case the caller should fall back
    to comparing display strings.
    """
    from actions.attributes import (
        CategoryChoiceAttributeValue,
        GenericTextAttributeAttributeValue,
        NumericAttributeValue,
        OptionalChoiceWithTextAttributeValue,
        OrderedChoiceAttributeValue,
    )

    if isinstance(value, OrderedChoiceAttributeValue):
        return (value.option.pk if value.option else None) == attribute.choice_id  # type: ignore[attr-defined]
    if isinstance(value, CategoryChoiceAttributeValue):
        return sorted(c.pk for c in value.categories) == sorted(c.pk for c in attribute.categories.all())  # type: ignore[attr-defined]
    if isinstance(value, OptionalChoiceWithTextAttributeValue):
        if (value.option.pk if value.option else None) != attribute.choice_id:  # type: ignore[attr-defined]
            return False
        return _text_vals_match(value.text_vals, attribute)
    if isinstance(value, GenericTextAttributeAttributeValue):
        return _text_vals_match(value.text_vals, attribute)
    if isinstance(value, NumericAttributeValue):
        return value.value == attribute.value  # type: ignore[attr-defined]
    return None


class AttributeComparison:
    """
    Comparison of the value of a single dynamic attribute between two versions of an action.

    Follows the interface of `wagtail.admin.compare.FieldComparison` so that instances can be
    rendered with Wagtail's revision comparison template.
    """

    is_field = True
    is_child_relation = False

    def __init__(
        self,
        attribute_type: AttributeTypeWrapper,
        language: str,
        obj_a: Action,
        obj_b: Action,
    ):
        self.attribute_type = attribute_type
        self.language = language
        self._side_a = self._effective_value(obj_a)
        self._side_b = self._effective_value(obj_b)
        self.val_a = self._display_value(*self._side_a)
        self.val_b = self._display_value(*self._side_b)

    def _effective_value(self, obj: Action) -> tuple[AttributeValue | None, Attribute | None, Action]:
        """
        Resolve the value of this attribute for one version of the action.

        Returns (draft_value, db_attribute, obj); exactly one of the first two is meaningful.
        A revision that does not track this attribute type at all (e.g. because it was not
        editable in the form that produced the revision) falls back to the published database
        value instead of being treated as deleted.
        """
        draft_attributes = getattr(obj, 'draft_attributes', None)
        if draft_attributes is not None:
            try:
                value = draft_attributes.get_value_for_attribute_type(self.attribute_type)
            except KeyError:
                pass
            else:
                if not value.should_exist_in_database():
                    # An explicitly cleared value.
                    return (None, None, obj)
                return (value, None, obj)
        attribute = self.attribute_type.get_attributes(obj).first()
        return (None, attribute, obj)

    def _display_value(self, draft_value: AttributeValue | None, attribute: Attribute | None, obj: Action) -> str:
        language_context = translation.override(self.language) if self.language else contextlib.nullcontext()
        with language_context:
            if draft_value is not None:
                return str(draft_value.instantiate_attribute(self.attribute_type, obj))
            if attribute is not None:
                return str(attribute)
            return ''

    def field_label(self) -> str:
        label = str(self.attribute_type.instance)
        if self.language:
            label += f' ({self.language})'
        return label

    def htmldiff(self):
        return diff_text(self.val_a, self.val_b).to_html()

    def has_changed(self) -> bool:
        draft_a, attr_a, _ = self._side_a
        draft_b, attr_b, _ = self._side_b

        if draft_a is None and draft_b is None:
            # Both sides resolve to the database state of the same action, which is identical
            # by definition; this also covers revisions that do not track the attribute.
            if attr_a is None or attr_b is None:
                return (attr_a is None) != (attr_b is None)
            return attr_a.pk != attr_b.pk

        if draft_a is not None and draft_b is not None:
            return draft_a.serialize() != draft_b.serialize()

        # One side is a draft value, the other the database state; compare underlying values
        # so that changes invisible in the display rendering are still detected.
        draft_value = draft_a if draft_a is not None else draft_b
        attribute = attr_b if draft_a is not None else attr_a
        assert draft_value is not None
        if attribute is None:
            return True
        matches = _draft_value_matches_attribute(draft_value, attribute)
        if matches is None:
            return self.val_a != self.val_b
        return not matches


class CategoryTypeComparison(M2MFieldComparison):
    """Comparison of the categories of a single category type between two versions of an action."""

    def __init__(self, category_type: CategoryType, obj_a: Action, obj_b: Action):
        self.category_type = category_type
        # Skip FieldComparison.__init__ on purpose; we get the values from the `categories`
        # relation instead of a plain model field.
        self.field = Action._meta.get_field('categories')
        self.val_a = self._get_categories(obj_a)
        self.val_b = self._get_categories(obj_b)

    def _get_categories(self, obj: Action) -> list:
        cats = [cat for cat in obj.categories.all() if cat.type_id == self.category_type.pk]
        return sorted(cats, key=str)

    def get_items(self) -> tuple[list, list]:
        return self.val_a, self.val_b

    def field_label(self) -> str:
        return capfirst(str(self.category_type.name))


class ComparisonContext:
    """State shared by a single walk over an action edit handler."""

    def __init__(self, obj_a: Action, obj_b: Action, user: User):
        self.obj_a = obj_a
        self.obj_b = obj_b
        self.user = user
        plan = obj_a.plan
        self.category_types_by_identifier = {ct.identifier: ct for ct in plan.category_types.filter(editable_for_actions=True)}
        self.seen_attributes: set[tuple[int, str]] = set()
        self.seen_relations: set[str] = set()
        self.seen_fields: set[str] = set()


def _compare_attribute_panel(panel: AttributeFieldPanel, ctx: ComparisonContext) -> AttributeComparison | None:
    key = (panel.attribute_type.instance.pk, panel.language)
    if key in ctx.seen_attributes:
        # Some attribute types (e.g. choice with text) produce multiple form fields for the same
        # attribute; show only one comparison row per attribute and language.
        return None
    ctx.seen_attributes.add(key)
    return AttributeComparison(panel.attribute_type, panel.language, ctx.obj_a, ctx.obj_b)


def _compare_field_panel(panel: FieldPanel, ctx: ComparisonContext) -> FieldComparison | CategoryTypeComparison | None:
    field_name = panel.field_name
    if field_name.startswith(CATEGORY_FIELD_PREFIX):
        category_type = ctx.category_types_by_identifier.get(field_name[len(CATEGORY_FIELD_PREFIX) :])
        if category_type is None:
            return None
        return CategoryTypeComparison(category_type, ctx.obj_a, ctx.obj_b)

    if field_name in ctx.seen_fields:
        return None
    try:
        # get_comparison_class is missing from the FieldPanel type stub
        comparator_class = panel.get_comparison_class()  # type: ignore[attr-defined]
        db_field = panel.db_field
    except FieldDoesNotExist:
        # The panel refers to a form-only field that does not exist on the model; there is
        # nothing to compare it against in the revision content.
        return None
    ctx.seen_fields.add(field_name)
    return comparator_class(db_field, ctx.obj_a, ctx.obj_b)


def _get_inline_panel_field_comparisons(panel: InlinePanel) -> list:
    comparisons = []
    for child in panel.child_edit_handler.children:
        if not isinstance(child, FieldPanel):
            continue
        try:
            # get_comparison_class is missing from the FieldPanel type stub
            comparator_class = child.get_comparison_class()  # type: ignore[attr-defined]
            db_field = child.db_field
        except FieldDoesNotExist:
            continue
        comparisons.append(functools.partial(comparator_class, db_field))
    return comparisons


def _compare_inline_panel(panel: InlinePanel, ctx: ComparisonContext) -> ChildRelationComparison | None:
    db_field = panel.db_field
    relation_name = db_field.related_name
    if relation_name is None or relation_name in ctx.seen_relations:
        # Role-filtered inline panels (e.g. contact persons per role) all map to the same
        # underlying relation; compare the whole relation only once.
        return None
    ctx.seen_relations.add(relation_name)
    heading: StrOrPromise = panel.heading or relation_name.replace('_', ' ')
    return ChildRelationComparison(
        db_field,
        _get_inline_panel_field_comparisons(panel),
        ctx.obj_a,
        ctx.obj_b,
        label=capfirst(str(heading)),
    )


def _get_model_field_comparisons(model: type[Model]) -> list:
    """Build comparators for a child model's editable fields, excluding the parent link."""
    comparisons = []
    for field in model._meta.concrete_fields:
        if not field.editable or field.primary_key or field.name in CHILD_RELATION_EXCLUDED_FIELDS:
            continue
        if field.is_relation and field.related_model is Action:
            continue
        bound_panel = FieldPanel(field.name).bind_to_model(model)
        # get_comparison_class is missing from the FieldPanel type stub
        comparator_class = bound_panel.get_comparison_class()  # type: ignore[attr-defined]
        comparisons.append(functools.partial(comparator_class, field))
    return comparisons


def _compare_relation_panel(panel: Panel, ctx: ComparisonContext) -> ChildRelationComparison | None:
    """
    Compare a child relation exposed by a panel that is not a regular InlinePanel.

    Read-only panels for contact persons and responsible parties (and their role-grouping
    container) only declare a `relation_name`; without this, changes to those relations would
    be invisible to reviewers who lack edit rights on them.
    """
    relation_name = getattr(panel, 'relation_name', None)
    if not relation_name or relation_name in ctx.seen_relations:
        return None
    manager = getattr(Action, relation_name, None)
    rel = getattr(manager, 'rel', None)
    if rel is None or rel.related_name != relation_name:
        return None
    ctx.seen_relations.add(relation_name)
    heading: StrOrPromise = panel.heading or relation_name.replace('_', ' ')
    return ChildRelationComparison(
        rel,
        _get_model_field_comparisons(rel.related_model),
        ctx.obj_a,
        ctx.obj_b,
        label=capfirst(str(heading)),
    )


def _compare_single_panel(panel: Panel, ctx: ComparisonContext) -> Any | None:
    from actions.attributes import AttributeFieldPanel

    if isinstance(panel, AttributeFieldPanel):
        return _compare_attribute_panel(panel, ctx)
    if isinstance(panel, FieldPanel):
        return _compare_field_panel(panel, ctx)
    if isinstance(panel, InlinePanel):
        return _compare_inline_panel(panel, ctx)
    if getattr(panel, 'relation_name', None):
        return _compare_relation_panel(panel, ctx)
    return None


def _panel_produces_comparison(panel: Panel) -> bool:
    from actions.attributes import AttributeFieldPanel

    if isinstance(panel, (AttributeFieldPanel, FieldPanel, InlinePanel)):
        return True
    # Panels that only declare a relation name (e.g. read-only contact person panels and their
    # role-grouping container) are compared through the underlying relation.
    return bool(getattr(panel, 'relation_name', None))


def _walk_panel(panel: Panel, ctx: ComparisonContext) -> Iterator[Any]:
    if isinstance(panel, AdminOnlyPanel) and not ctx.user.is_general_admin_for_plan(ctx.obj_a.plan):
        return

    if _panel_produces_comparison(panel):
        try:
            comparison = _compare_single_panel(panel, ctx)
        except Exception as e:
            # A single field that cannot be compared should not break the whole comparison view.
            sentry_sdk.capture_exception(e)
            logger.exception(f'Failed to compare panel {panel!r} of action {ctx.obj_a.pk}')
            return
        if comparison is not None:
            yield comparison
        return

    if isinstance(panel, PanelGroup):
        for child in panel.children:
            yield from _walk_panel(child, ctx)


def get_action_comparisons(
    edit_handler: Panel,
    obj_a: Action,
    obj_b: Action,
    user: User,
    only_changed: bool = True,
) -> list[Any]:
    """
    Compare two versions of an action, panel by panel.

    `edit_handler` must be an edit handler that has been bound to the `Action` model. `obj_a` and
    `obj_b` are two versions of the same action: typically the live database instance and a
    revision restored with `Revision.as_object()`, in chronological order.

    Returns a list of Wagtail comparison objects (see `wagtail.admin.compare`) in the order the
    respective panels appear in the edit form. When `only_changed` is set, only fields whose values
    differ between the two versions are included.
    """
    ctx = ComparisonContext(obj_a, obj_b, user)
    comparisons = []
    for comparison in _walk_panel(edit_handler, ctx):
        try:
            changed = comparison.has_changed()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.exception(f'Failed to compare field {type(comparison).__name__} of action {obj_a.pk}')
            continue
        if only_changed and not changed:
            continue
        comparisons.append(comparison)
    return comparisons


def get_changed_field_labels(
    edit_handler: Panel,
    obj_a: Action,
    obj_b: Action,
    user: User,
) -> list[str]:
    """Return the labels of the fields whose values differ between two versions of an action."""
    return [str(comparison.field_label()) for comparison in get_action_comparisons(edit_handler, obj_a, obj_b, user)]
