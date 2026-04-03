from django.http import JsonResponse

from runs.models import GlobalKeyword, GlobalLookingForLabel


def keyword_autocomplete(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    q = request.GET.get("q", "")
    labels = GlobalKeyword.objects.filter(label__icontains=q).values_list("label", flat=True)[:20]
    return JsonResponse(list(labels), safe=False)


def looking_for_autocomplete(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    q = request.GET.get("q", "")
    labels = GlobalLookingForLabel.objects.filter(label__icontains=q).values_list("label", flat=True)[:20]
    return JsonResponse(list(labels), safe=False)
