from django.utils.translation import gettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from . import DEFAULT_APP_NAMESPACE


class PeopleApp(CMSApp):
    name = _('People')
    app_name = DEFAULT_APP_NAMESPACE
    urls = ['aldryn_people.urls']  # COMPAT: CMS3.2

    def get_urls(self, *args, **kwargs):
        return self.urls


apphook_pool.register(PeopleApp)
