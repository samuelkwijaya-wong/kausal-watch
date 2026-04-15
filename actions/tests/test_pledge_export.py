from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING

from django.db.models import Count

import pytest

from actions.models import Pledge, PledgeCommitment, PledgeUser
from actions.pledge_admin import PledgeIndexView, PledgeViewSet
from actions.tests.factories import PlanFactory, PledgeFactory

if TYPE_CHECKING:
    from django.test import RequestFactory

    from users.models import User

pytestmark = pytest.mark.django_db


def _get_view_and_queryset(rf: RequestFactory, user: User, plan, extra_params: dict | None = None):
    """Set up a PledgeIndexView and build the queryset for the given plan."""
    view_set = PledgeViewSet()
    view = PledgeIndexView(
        **view_set.get_common_view_kwargs(),
        **view_set.get_index_view_kwargs(),
    )
    params = {'export': 'csv'}
    if extra_params:
        params.update(extra_params)
    request = rf.get('/admin/', params)
    request.user = user
    view.setup(request)
    view.filterset_class = None  # type: ignore[assignment]
    queryset = Pledge.objects.filter(plan=plan).annotate(commitment_count=Count('commitments'))
    return view, queryset


def _parse_csv_rows(view: PledgeIndexView, queryset) -> list[dict[str, str]]:
    """Stream pledges CSV from the view and parse into a list of row dicts."""
    raw = b''.join(view.stream_csv(queryset))
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8')))
    return list(reader)


def _parse_commitments_csv_rows(view: PledgeIndexView, queryset) -> list[dict[str, str]]:
    """Stream commitments CSV from the view and parse into a list of row dicts."""
    response = view.write_commitments_csv_response(queryset)
    raw = b''.join(response.streaming_content)  # type: ignore[arg-type]
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8')))
    return list(reader)


class TestPledgeExportCSV:
    @pytest.fixture(autouse=True)
    def setup(self, plan_admin_user):
        self.user = plan_admin_user
        self.plan = self.user.get_active_admin_plan()
        self.plan.features.enable_community_engagement = True
        self.plan.features.save()

    def test_basic_export_columns(self, rf):
        """Pledge export should contain base columns; user_data columns should not appear."""
        PledgeFactory.create(plan=self.plan)

        view, qs = _get_view_and_queryset(rf, self.user, self.plan)
        rows = _parse_csv_rows(view, qs)

        assert len(rows) == 1
        row = rows[0]
        assert set(row.keys()) >= {'ID', 'Name', 'Slug', 'Number of commitments'}
        assert not any(k in row for k in ('zip_code', 'city'))

    def test_commitment_count(self, rf):
        """Pledge export should reflect the correct number of commitments per pledge."""
        pledge = PledgeFactory.create(plan=self.plan)
        for _ in range(3):
            PledgeCommitment.objects.create(
                pledge=pledge,
                pledge_user=PledgeUser.objects.create(),
            )

        view, qs = _get_view_and_queryset(rf, self.user, self.plan)
        rows = _parse_csv_rows(view, qs)

        assert rows[0]['Number of commitments'] == '3'

    def test_user_data_columns_absent_from_pledge_export(self, rf):
        """User data keys from commitments should NOT appear as columns in the pledge export."""
        pledge = PledgeFactory.create(plan=self.plan)
        PledgeCommitment.objects.create(
            pledge=pledge,
            pledge_user=PledgeUser.objects.create(user_data={'zip_code': '00100', 'city': 'Helsinki'}),
        )

        view, qs = _get_view_and_queryset(rf, self.user, self.plan)
        rows = _parse_csv_rows(view, qs)

        row = rows[0]
        assert 'zip_code' not in row
        assert 'city' not in row

    def test_multiple_pledges(self, rf):
        """Pledge export should include one row per pledge."""
        PledgeFactory.create(plan=self.plan, name='First Pledge')
        PledgeFactory.create(plan=self.plan, name='Second Pledge')

        view, qs = _get_view_and_queryset(rf, self.user, self.plan)
        rows = _parse_csv_rows(view, qs)

        names = {row['Name'] for row in rows}
        assert names == {'First Pledge', 'Second Pledge'}

    def test_only_own_plan_pledges(self, rf):
        """Pledge export should only include pledges from the user's active plan."""
        PledgeFactory.create(plan=self.plan, name='My Pledge')

        other_plan = PlanFactory.create()
        other_plan.features.enable_community_engagement = True
        other_plan.features.save()
        PledgeFactory.create(plan=other_plan, name='Other Pledge')

        view, qs = _get_view_and_queryset(rf, self.user, self.plan)
        rows = _parse_csv_rows(view, qs)

        names = {row['Name'] for row in rows}
        assert 'My Pledge' in names
        assert 'Other Pledge' not in names


class TestCommitmentsExportCSV:
    @pytest.fixture(autouse=True)
    def setup(self, plan_admin_user):
        self.user = plan_admin_user
        self.plan = self.user.get_active_admin_plan()
        self.plan.features.enable_community_engagement = True
        self.plan.features.save()

    def test_commitments_export_columns(self, rf):
        """Commitments export should contain the expected base column headers."""
        pledge = PledgeFactory.create(plan=self.plan)
        PledgeCommitment.objects.create(pledge=pledge, pledge_user=PledgeUser.objects.create())

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        assert len(rows) == 1
        assert set(rows[0].keys()) >= {'Pledge ID', 'Pledge name', 'Commitment date', 'User ID'}

    def test_commitments_one_row_per_commitment(self, rf):
        """Commitments export should yield one row per commitment, not per pledge."""
        pledge = PledgeFactory.create(plan=self.plan)
        for _ in range(3):
            PledgeCommitment.objects.create(
                pledge=pledge,
                pledge_user=PledgeUser.objects.create(),
            )

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        assert len(rows) == 3

    def test_commitments_user_data_in_own_cells(self, rf):
        """Each commitment's user_data values should appear in their own cells, not comma-joined."""
        pledge = PledgeFactory.create(plan=self.plan)
        PledgeCommitment.objects.create(
            pledge=pledge,
            pledge_user=PledgeUser.objects.create(user_data={'zip_code': '00100', 'city': 'Helsinki'}),
        )
        PledgeCommitment.objects.create(
            pledge=pledge,
            pledge_user=PledgeUser.objects.create(user_data={'zip_code': '00200'}),
        )

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        assert len(rows) == 2
        zip_codes = {row['zip_code'] for row in rows}
        assert zip_codes == {'00100', '00200'}
        # Each cell contains a single value, not a comma-joined list
        for row in rows:
            assert ',' not in row['zip_code']

    def test_commitments_includes_timestamp_and_user_id(self, rf):
        """Each commitment row should include a timestamp and the pledge user's UUID."""
        pledge = PledgeFactory.create(plan=self.plan)
        pu = PledgeUser.objects.create()
        PledgeCommitment.objects.create(pledge=pledge, pledge_user=pu)

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        assert len(rows) == 1
        row = rows[0]
        assert row['User ID'] == str(pu.uuid)
        # Timestamp should be an ISO 8601 string
        assert 'T' in row['Commitment date'] or '-' in row['Commitment date']

    def test_commitments_only_own_plan(self, rf):
        """Commitments export should only include commitments from the user's active plan."""
        pledge = PledgeFactory.create(plan=self.plan, name='My Pledge')
        PledgeCommitment.objects.create(pledge=pledge, pledge_user=PledgeUser.objects.create())

        other_plan = PlanFactory.create()
        other_plan.features.enable_community_engagement = True
        other_plan.features.save()
        other_pledge = PledgeFactory.create(plan=other_plan, name='Other Pledge')
        PledgeCommitment.objects.create(pledge=other_pledge, pledge_user=PledgeUser.objects.create())

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        pledge_names = {row['Pledge name'] for row in rows}
        assert 'My Pledge' in pledge_names
        assert 'Other Pledge' not in pledge_names

    def test_commitments_comma_in_user_data_value(self, rf):
        """User data values containing commas should be properly handled in the commitments CSV."""
        pledge = PledgeFactory.create(plan=self.plan)
        PledgeCommitment.objects.create(
            pledge=pledge,
            pledge_user=PledgeUser.objects.create(user_data={'location': 'City, State'}),
        )

        view, qs = _get_view_and_queryset(rf, self.user, self.plan, {'export_type': 'commitments'})
        rows = _parse_commitments_csv_rows(view, qs)

        assert rows[0]['location'] == 'City, State'
