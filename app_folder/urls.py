from django.urls import path
from . import views

app_name = 'app_folder'
urlpatterns = [
    path('', views.TopView.as_view(), name='top_page'),
    path('top_page/', views.TopView.as_view(), name='top_page'),
    
    # app1 CRUD処理アプリ　ポケポケDB
    path('app1_index/', views.App1View.as_view(), name='app1_index'),

    # app2 APIと非同期通信
    path('app2_top/', views.App2View.as_view(), name='app2_top'),

]

"""
#    path('app1_form/<int:id>', views.App1View.as_view(), name='app1_edit'),
#    path('app1_form/', views.App1View.as_view(), name='app1_create'),

"""