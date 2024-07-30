import re
from typing import Optional, Any

from django.views.generic.base import RedirectView
from django.urls import reverse


class RootRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        request = self.request
        if request.user.is_authenticated:
            url = reverse('wagtailadmin_home')
        else:
            url = reverse('graphql')
        return url


class WadminRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        new_path = re.sub('^/wadmin', '/admin', self.request.get_full_path())
        return new_path
