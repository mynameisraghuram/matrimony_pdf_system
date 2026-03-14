from django.urls import path
from profiles import views

app_name = "profiles"

urlpatterns = [
    path("", views.profile_list, name="profile_list"),
    path("sync/", views.sync_sheet, name="sync_sheet"),
    path("bulk-generate/", views.bulk_generate_pdf, name="bulk_generate_pdf"),
    path("export/", views.export_excel, name="export_excel"),
    path("activity-log/", views.activity_log, name="activity_log"),
    path("add/", views.add_profile, name="add_profile"),
    path("<int:pk>/", views.profile_detail, name="profile_detail"),
    path("<int:pk>/edit/", views.edit_profile, name="edit_profile"),
    path("<int:pk>/delete/", views.delete_profile, name="delete_profile"),
    path("<int:pk>/upload-photo/", views.upload_photo, name="upload_photo"),
    path("<int:pk>/delete-photo/", views.delete_photo, name="delete_photo"),
    path("<int:pk>/generate-pdf/<str:tier>/", views.generate_pdf, name="generate_pdf"),
    path("<int:pk>/pdf/<int:pdf_id>/preview/", views.preview_pdf, name="preview_pdf"),
    path("<int:pk>/pdf/<int:pdf_id>/download/", views.download_pdf, name="download_pdf"),
    path("<int:pk>/pdf/<int:pdf_id>/email/", views.email_pdf, name="email_pdf"),
    path("<int:pk>/add-note/", views.add_note, name="add_note"),
    path("<int:pk>/note/<int:note_id>/delete/", views.delete_note, name="delete_note"),
]
