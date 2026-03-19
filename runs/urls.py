from django.urls import path

from runs.views import PlayerRunListView

app_name = "runs"

urlpatterns = [
    path("", PlayerRunListView.as_view(), name="run_list"),
]
