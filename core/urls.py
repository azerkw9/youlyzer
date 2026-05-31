from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('analyze/', views.analyze, name='analyze'),
    path('results/video/', views.video_results, name='video_results'),
    path('results/channel/', views.channel_results, name='channel_results'),
    path('compare/', views.compare, name='compare'),

    # Download endpoints
    path('download/thumbnail/', views.download_thumbnail, name='download_thumbnail'),

    # Static pages
    path('privacy/', views.privacy, name='privacy'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Custom admin dashboard
    path('lucius-dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('lucius-dashboard/ads/', admin_views.ads_list, name='admin_ads_list'),
    path('lucius-dashboard/ads/create/', admin_views.ad_create, name='admin_ad_create'),
    path('lucius-dashboard/ads/<int:pk>/edit/', admin_views.ad_edit, name='admin_ad_edit'),
    path('lucius-dashboard/ads/<int:pk>/delete/', admin_views.ad_delete, name='admin_ad_delete'),
    path('lucius-dashboard/messages/', admin_views.messages_list, name='admin_messages_list'),
    path('lucius-dashboard/messages/<int:pk>/', admin_views.message_detail, name='admin_message_detail'),
    path('lucius-dashboard/messages/<int:pk>/toggle-read/', admin_views.message_toggle_read, name='admin_message_toggle_read'),
    path('lucius-dashboard/messages/<int:pk>/delete/', admin_views.message_delete, name='admin_message_delete'),
]
