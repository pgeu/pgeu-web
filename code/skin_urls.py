from django.conf.urls import url

import postgresqleu.static.views
import postgresqleu.membership.views

PRELOAD_URLS=[
    url(r'^(events/services)/$', postgresqleu.static.views.static_fallback),
    url(r'^community/members/$', postgresqleu.membership.views.userlist),
]

