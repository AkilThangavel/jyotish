from django.conf.urls import include
from django.urls import path
from match import views

#

urlpatterns = [
    path('', views.HomePageView.as_view()),

    path('admin_panel', views.AdminPanelView.as_view()),
    path('admin_settings', views.AdminSettingsView.as_view()),
    path('index', views.HomePageView.as_view()),
    path('login', views.SignInView.as_view()),
    path('logout', views.logout_view),

    #path('data_input1', views.DataInputView.as_view()),
    #path('data_input2', views.DataInputDetailedView.as_view()),
    #path('data_input3', views.DataInput3View.as_view()),

    #path('match_engine1', views.DataInputMatchView.as_view()),
    #path('match_engine2', views.DataInputDetailedMatchView.as_view()),
    #path('match_engine3', views.DataInput3MatchView.as_view()),
    path('persons_list', views.PersonsListView.as_view()),
    path('map_sessions', views.MapSessionsView.as_view()),
    path('videos', views.VideosPDFView.as_view()),

    path('load50', views.Load50.as_view()),

    path('relocation_map_input', views.RelocationMap3dInputView.as_view()),
    path('relocation_map3d', views.RelocationMap3dView.as_view()),

    path('ajax/validate_person_name/', views.ajax_validate_person_name),
    path('ajax/validate_person_name_admin/', views.ajax_validate_person_name_admin),
    path('ajax/add_person/', views.ajax_add_person),
    path('ajax/save_labels/', views.ajax_save_labels),
    path('ajax/save_session/', views.ajax_save_session),
    path('ajax/delete_session/', views.ajax_delete_session),
    path('ajax/delete_user/', views.ajax_delete_user),
    path('ajax/delete_user_video_link/', views.delete_user_video_link),
    path('ajax/add_user_video_link/', views.add_user_video_link),
    path('ajax/add_user_video_link/', views.add_user_video_link),
    path('ajax/save_video_link/', views.save_video_link),
    path('ajax/edit_video_links/', views.edit_video_links),
    path('ajax/get_degrees/', views.get_degrees)
]
