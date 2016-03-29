from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('game.urls')),
]

admin.site.site_header = 'Iron & Blood administration'
admin.site.site_title = 'Iron & Blood administration'
