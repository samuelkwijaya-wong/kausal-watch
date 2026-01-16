from django.urls import reverse

import pytest
from pytest_factoryboy import register

from .factories import IndicatorFactory, UnitFactory

register(IndicatorFactory)
register(UnitFactory)


@pytest.fixture
def indicator_list_url(plan):
    return reverse('indicator-list', args=(plan.pk,))


@pytest.fixture
def indicator_detail_url(plan, indicator):
    return reverse('indicator-detail', kwargs={'plan_pk': plan.pk, 'pk': indicator.pk})
