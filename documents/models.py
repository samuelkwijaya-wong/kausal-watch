from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.documents.models import AbstractDocument, Document as WagtailDocument
from wagtail.search.queryset import SearchableQuerySetMixin

from kausal_common.models.types import ModelManager


class AplansDocumentQuerySet(SearchableQuerySetMixin, models.QuerySet['AplansDocument']):
    pass


if TYPE_CHECKING:
    class AplansDocumentManager(ModelManager['AplansDocument', AplansDocumentQuerySet]): ...
else:
    AplansDocumentManager = ModelManager.from_queryset(AplansDocumentQuerySet)


class AplansDocument(AbstractDocument):
    admin_form_fields = WagtailDocument.admin_form_fields

    objects = AplansDocumentManager()

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')

    @property
    def url(self):
        return reverse('wagtaildocs_serve', args=[self.id, self.filename])
