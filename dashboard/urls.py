from django.urls import path

from dashboard.views.auth import DashboardLoginView, DashboardLogoutView
from dashboard.views.casting import (
    CastingCreateView,
    CastingDeleteView,
    CastingEditView,
    CastingListView,
    CSVUploadConfirmView,
    CSVUploadPreviewView,
    CSVUploadView,
)
from dashboard.views.invites import InviteGenerateView, InviteListView
from dashboard.views.run_create import run_create_view
from dashboard.views.run_detail import (
    CustomAttributeDeleteView,
    CustomAttributeListView,
    RunDetailView,
    RunSettingsView,
    VocabularyAddView,
    VocabularyEditView,
)
from dashboard.views.run_list import RunListView

app_name = "dashboard"

urlpatterns = [
    # Auth
    path("login/", DashboardLoginView.as_view(), name="login"),
    path("logout/", DashboardLogoutView.as_view(), name="logout"),
    # Run list & create
    path("", RunListView.as_view(), name="run_list"),
    path("create/", run_create_view, name="run_create"),
    # Run detail & settings
    path("<slug:slug>/", RunDetailView.as_view(), name="run_detail"),
    path("<slug:slug>/settings/", RunSettingsView.as_view(), name="run_settings"),
    # Vocabulary
    path("<slug:slug>/vocabulary/<str:vocab_type>/", VocabularyEditView.as_view(), name="vocabulary_edit"),
    path("<slug:slug>/vocabulary/<str:vocab_type>/add/", VocabularyAddView.as_view(), name="vocabulary_add"),
    # Custom attributes
    path("<slug:slug>/custom-attributes/", CustomAttributeListView.as_view(), name="custom_attrs"),
    path("<slug:slug>/custom-attributes/<int:attr_id>/delete/", CustomAttributeDeleteView.as_view(), name="custom_attr_delete"),
    # Castings
    path("<slug:slug>/castings/", CastingListView.as_view(), name="casting_list"),
    path("<slug:slug>/castings/create/", CastingCreateView.as_view(), name="casting_create"),
    path("<slug:slug>/castings/<int:casting_id>/edit/", CastingEditView.as_view(), name="casting_edit"),
    path("<slug:slug>/castings/<int:casting_id>/delete/", CastingDeleteView.as_view(), name="casting_delete"),
    path("<slug:slug>/castings/upload/", CSVUploadView.as_view(), name="csv_upload"),
    path("<slug:slug>/castings/upload/preview/", CSVUploadPreviewView.as_view(), name="csv_upload_preview"),
    path("<slug:slug>/castings/upload/confirm/", CSVUploadConfirmView.as_view(), name="csv_upload_confirm"),
    # Invites
    path("<slug:slug>/invites/", InviteListView.as_view(), name="invite_list"),
    path("<slug:slug>/invites/generate/", InviteGenerateView.as_view(), name="invite_generate"),
]
