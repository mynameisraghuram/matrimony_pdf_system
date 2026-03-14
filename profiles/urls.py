from django.urls import path
from profiles import views

app_name = "profiles"

urlpatterns = [
    path("", views.profile_list, name="profile_list"),
    path("sync/", views.sync_sheet, name="sync_sheet"),
    path("<int:pk>/", views.profile_detail, name="profile_detail"),
    path("<int:pk>/generate-pdf/<str:tier>/", views.generate_pdf, name="generate_pdf"),
    path("<int:pk>/pdf/<int:pdf_id>/download/", views.download_pdf, name="download_pdf"),
]
