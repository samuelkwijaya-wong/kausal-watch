"""
Tests for Plan.get_view_url without wildcard (*) hostname patterns.

These tests verify that the non-wildcard get_view_url behavior is preserved
when wildcard hostname support is added.
"""

from types import SimpleNamespace

import pytest

from actions.tests.factories import PlanDomainFactory, PlanFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def plan():
    return PlanFactory.create(
        site_url='https://myplan.example.com',
        primary_language='en',
        other_languages=['fi'],
    )


@pytest.fixture(params=['settings', 'request', 'both'], ids=['via_settings', 'via_request', 'via_both'])
def wildcard_domain(request, settings):
    retval = {}
    settings.HOSTNAME_PLAN_DOMAINS = []
    if request.param in ('settings', 'both'):
        settings.HOSTNAME_PLAN_DOMAINS = ['dummy.io']
    if request.param in ('request', 'both'):
        retval.update({'request': SimpleNamespace(wildcard_domains=['dummy.io'])})
    return retval


@pytest.fixture
def no_wildcard_domains(settings):
    settings.HOSTNAME_PLAN_DOMAINS = []


class TestGetViewUrlNoClientUrl:
    def test_returns_site_url(self, plan):
        assert plan.get_view_url() == 'https://myplan.example.com'

    def test_returns_site_url_with_trailing_slash_stripped(self):
        plan = PlanFactory.create(site_url='https://myplan.example.com/')
        assert plan.get_view_url() == 'https://myplan.example.com'

    def test_adds_locale_prefix_for_non_primary_language(self, plan):
        url = plan.get_view_url(active_locale='fi')
        assert url == 'https://myplan.example.com/fi'

    def test_no_locale_prefix_for_primary_language(self, plan):
        url = plan.get_view_url(active_locale='en')
        assert url == 'https://myplan.example.com'

    def test_no_locale_prefix_for_unknown_language(self, plan):
        url = plan.get_view_url(active_locale='sv')
        assert url == 'https://myplan.example.com'

    def test_site_url_without_scheme_gets_https(self):
        plan = PlanFactory.create(site_url='myplan.example.com')
        assert plan.get_view_url() == 'https://myplan.example.com'


class TestGetViewUrlWithWildcardDomain:
    """Test get_view_url when client_url matches a HOSTNAME_PLAN_DOMAINS entry (non-* pattern)."""

    def test_returns_url_with_plan_identifier(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='https://anything.dummy.io', **wildcard_domain)
        assert url == f'https://{plan.identifier}.dummy.io'

    def test_preserves_http_scheme(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='http://anything.dummy.io', **wildcard_domain)
        assert url == f'http://{plan.identifier}.dummy.io'

    def test_preserves_custom_port(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='https://anything.dummy.io:8080', **wildcard_domain)
        assert url == f'https://{plan.identifier}.dummy.io:8080'

    def test_strips_default_https_port(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='https://anything.dummy.io:443', **wildcard_domain)
        assert url == f'https://{plan.identifier}.dummy.io'

    def test_strips_default_http_port(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='http://anything.dummy.io:80', **wildcard_domain)
        assert url == f'http://{plan.identifier}.dummy.io'

    def test_adds_locale_prefix(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='https://anything.dummy.io', active_locale='fi', **wildcard_domain)
        assert url == f'https://{plan.identifier}.dummy.io/fi'

    def test_no_locale_prefix_for_primary_language(self, plan, wildcard_domain):
        url = plan.get_view_url(client_url='https://anything.dummy.io', active_locale='en', **wildcard_domain)
        assert url == f'https://{plan.identifier}.dummy.io'


class TestGetViewUrlWithPlanDomain:
    """Test get_view_url when client_url matches a PlanDomain."""

    def test_returns_url_with_matching_domain(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='climate.city.gov')
        url = plan.get_view_url(client_url='https://climate.city.gov')
        assert url == 'https://climate.city.gov'

    def test_includes_base_path(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='city.gov', base_path='/climate')
        url = plan.get_view_url(client_url='https://city.gov')
        assert url == 'https://city.gov/climate'

    def test_base_path_trailing_slash_stripped(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='city.gov', base_path='/climate/')
        url = plan.get_view_url(client_url='https://city.gov')
        assert url == 'https://city.gov/climate'

    def test_preserves_custom_port(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='climate.city.gov')
        url = plan.get_view_url(client_url='https://climate.city.gov:8443')
        assert url == 'https://climate.city.gov:8443'

    def test_adds_locale_prefix(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='climate.city.gov')
        url = plan.get_view_url(client_url='https://climate.city.gov', active_locale='fi')
        assert url == 'https://climate.city.gov/fi'

    def test_locale_prefix_after_base_path(self, plan):
        PlanDomainFactory.create(plan=plan, hostname='city.gov', base_path='/climate')
        url = plan.get_view_url(client_url='https://city.gov', active_locale='fi')
        assert url == 'https://city.gov/climate/fi'


class TestGetViewUrlFallback:
    """Test get_view_url falls back to site_url when client_url doesn't match anything."""

    def test_falls_back_when_hostname_not_in_wildcard_or_domains(self, plan, no_wildcard_domains):
        url = plan.get_view_url(client_url='https://unknown.example.org')
        assert url == 'https://myplan.example.com'

    def test_falls_back_with_locale_prefix(self, plan, no_wildcard_domains):
        url = plan.get_view_url(client_url='https://unknown.example.org', active_locale='fi')
        assert url == 'https://myplan.example.com/fi'
