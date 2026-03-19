from django.urls import path

from casting.views import keyword_autocomplete, looking_for_autocomplete

app_name = "casting"

urlpatterns = [
    path("autocomplete/keywords/", keyword_autocomplete, name="keyword_autocomplete"),
    path("autocomplete/looking-for/", looking_for_autocomplete, name="looking_for_autocomplete"),
]
