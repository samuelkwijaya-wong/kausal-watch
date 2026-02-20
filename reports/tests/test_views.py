from __future__ import annotations

import pytest


def test_mark_action_as_complete_view_accepts_as_view_kwargs():
    """
    as_view() must accept all kwargs that are passed when the view is used.

    Django's View.as_view() checks hasattr(cls, key) for each kwarg.
    Type annotations without default values do NOT create class attributes,
    so they will cause TypeError if passed as kwargs to as_view().

    This test ensures that MarkActionAsCompleteView has action_pk and report_pk
    as class attributes (with default values) so they can be passed to as_view().
    """
    from reports.views import MarkActionAsCompleteView

    # Verify the class attributes exist
    assert hasattr(MarkActionAsCompleteView, 'action_pk'), \
        'MarkActionAsCompleteView must have action_pk as a class attribute'
    assert hasattr(MarkActionAsCompleteView, 'report_pk'), \
        'MarkActionAsCompleteView must have report_pk as a class attribute'
    assert hasattr(MarkActionAsCompleteView, 'complete'), \
        'MarkActionAsCompleteView must have complete as a class attribute'

    # Verify as_view() accepts the kwargs (these are passed in actions/action_admin.py)
    try:
        MarkActionAsCompleteView.as_view(
            model_admin=None,
            action_pk='1',
            report_pk='1',
            complete=True,
        )
    except TypeError as e:
        if 'invalid keyword' in str(e):
            pytest.fail(f'as_view() rejected a keyword argument: {e}')
        raise


def test_mark_report_as_complete_view_accepts_as_view_kwargs():
    """
    as_view() must accept all kwargs that are passed when the view is used.

    This test ensures that MarkReportAsCompleteView has report_pk and complete
    as class attributes (with default values) so they can be passed to as_view().
    """
    from reports.views import MarkReportAsCompleteView

    # Verify the class attributes exist
    assert hasattr(MarkReportAsCompleteView, 'report_pk'), \
        'MarkReportAsCompleteView must have report_pk as a class attribute'
    assert hasattr(MarkReportAsCompleteView, 'complete'), \
        'MarkReportAsCompleteView must have complete as a class attribute'

    # Verify as_view() accepts the kwargs (these are passed in reports/wagtail_admin.py)
    try:
        MarkReportAsCompleteView.as_view(
            model_admin=None,
            report_pk='1',
            complete=True,
        )
    except TypeError as e:
        if 'invalid keyword' in str(e):
            pytest.fail(f'as_view() rejected a keyword argument: {e}')
        raise
