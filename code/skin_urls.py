from django.urls import re_path

import postgresqleu.static.views
import postgresqleu.membership.views

PRELOAD_URLS = [
    re_path(r'^(events/services)/$', postgresqleu.static.views.static_fallback),
    re_path(r'^community/members/$', postgresqleu.membership.views.userlist),
]
