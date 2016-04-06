from django.conf.urls import url

from . import views

USERNAME_REGEX = '[a-zA-Z0-9._]+'

app_name = 'game'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    # Exchanges page
    url(r'^exchanges$', views.exchanges, name='exchanges'),
    url(r'^exchanges/0/(?P<state>[WARC]+)', views.exchanges, name='filter_exchanges'),
    url(r'^exchanges/0/', views.exchanges, name='filter_exchanges_without_opts'),
    # Modify an exchange
    url(r'^exchanges/(?P<exchange_pk>[0-9]+)', views.update_exchange, name='update_exchange'),
    # Exchanges with a user page
    url(r'^exchanges/(?P<offeree>'+USERNAME_REGEX+')/$', views.new_exchange, name='exchange'),
    url(r'^exchanges/(?P<offeree>'+USERNAME_REGEX+')/0/(?P<state>[WARC]+)$', views.new_exchange, name='filter_exchanges_offer'),
    url(r'^exchanges/(?P<offeree>'+USERNAME_REGEX+')/0/$', views.new_exchange, name='filter_exchanges_offer_without_opts'),
    # Bonds page
    url(r'^bonds$', views.bonds, name='bonds'),
    url(r'^bonds/0/(?P<state>[WPF]+)', views.bonds, name='filter_bonds'),
    url(r'^bonds/0/', views.bonds, name='filter_bonds_without_opts'),
    # Modify a Bond
    url(r'^bonds/(?P<bond_pk>[0-9]+)', views.update_bond, name='update_bond'),
    # Exchanges with a user page
    url(r'^bonds/(?P<username>'+USERNAME_REGEX+')/$', views.bond_by_user, name='bond'),
    url(r'^bonds/(?P<username>.+)/0/(?P<state>[WPF]+)', views.bond_by_user, name='filter_bonds_offer'),
    url(r'^bonds/(?P<username>.+)/0/$', views.bond_by_user, name='filter_bonds_offer_without_opts'),
    # Login/Logout
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
]

