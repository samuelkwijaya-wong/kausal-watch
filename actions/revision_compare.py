from __future__ import annotations

import functools
import typing
from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.utils import translation
from django.utils.text import capfirst
from wagtail.admin.compare import ChildRelationComparison, M2MFieldComparison, diff_text
from wagtail.admin.panels import FieldPanel, InlinePanel, PanelGroup

from loguru import logger

from actions.models.action import Action
from admin_site.wagtail import AdminOnlyPanel

if typing.TYPE_CHECKING:
    from collections.abc import Iterator

    from django_stubs_ext import StrOrPromise
    from wagtail.admin.compare import FieldComparison
    from wagtail.admin.panels.base import Panel

    from actions.attributes import AttributeFieldPanel, AttributeType as AttributeTypeWrapper
    from actions.models.category import CategoryType
    from users.models import User

logger = logger.bind(name='actions.revision_compare')

CATEGORY_FIELD_PREFIX = 'categories_'


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
        self.val_a = self._display_value(obj_a)
        self.val_b = self._display_value(obj_b)

    def _display_value(self, obj: Action) -> str:
        draft_attributes = getattr(obj, 'draft_attributes', None)
        if draft_attributes is not None:
            # The object comes from a revision; read the value from the serialized draft attributes.
            try:
                attribute_value = draft_attributes.get_value_for_attribute_type(self.attribute_type)
            except KeyError:
                return ''
            if not attribute_value.should_exist_in_database():
                return ''
            attribute = attribute_value.instantiate_attribute(self.attribute_type, obj)
            if not self.language:
                return str(attribute)
            with translation.override(self.language):
                return str(attribute)

        # The object is the live version; read the values from the database.
        def get_value() -> str:
            return ' '.join(str(x) for x in self.attribute_type.get_attributes(obj))

        if not self.language:
            return get_value()
        with translation.override(self.language):
            return get_value()

    def field_label(self) -> str:
        label = str(self.attribute_type.instance)
        if self.language:
            label += f' ({self.language})'
        return label

    def htmldiff(self):
        return diff_text(self.val_a, self.val_b).to_html()

    def has_changed(self) -> bool:
        return self.val_a != self.val_b


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


def _compare_single_panel(panel: Panel, ctx: ComparisonContext) -> Any | None:
    from actions.attributes import AttributeFieldPanel

    if isinstance(panel, AttributeFieldPanel):
        return _compare_attribute_panel(panel, ctx)
    if isinstance(panel, FieldPanel):
        return _compare_field_panel(panel, ctx)
    if isinstance(panel, InlinePanel):
        return _compare_inline_panel(panel, ctx)
    return None


def _walk_panel(panel: Panel, ctx: ComparisonContext) -> Iterator[Any]:
    from actions.attributes import AttributeFieldPanel

    if isinstance(panel, AdminOnlyPanel) and not ctx.user.is_general_admin_for_plan(ctx.obj_a.plan):
        return

    if isinstance(panel, (AttributeFieldPanel, FieldPanel, InlinePanel)):
        try:
            comparison = _compare_single_panel(panel, ctx)
        except Exception:
            # A single field that cannot be compared should not break the whole comparison view.
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
        except Exception:
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
