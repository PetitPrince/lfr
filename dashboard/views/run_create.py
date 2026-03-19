from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from dashboard.forms.run import RunCreateForm
from runs.models import CustomAttributeDefinition, Run


def _is_organizer(user):
    return user.role in ("organizer", "admin")


@login_required(login_url="/organize/login/")
@user_passes_test(_is_organizer, login_url="/organize/login/")
def run_create_view(request):
    """Create a new run, optionally from a template."""
    templates = Run.objects.filter(is_template=True).order_by("name")

    if request.method == "POST":
        form = RunCreateForm(request.POST)
        if form.is_valid():
            run = form.save()

            template_id = request.POST.get("template")
            if template_id:
                try:
                    template = Run.objects.get(pk=template_id, is_template=True)
                    _copy_template_data(template, run)
                except Run.DoesNotExist:
                    pass

            return redirect("dashboard:run_detail", slug=run.slug)
    else:
        form = RunCreateForm()

    return render(request, "dashboard/run_create.html", {
        "form": form,
        "templates": templates,
    })


def _copy_template_data(template, run):
    """Copy vocabulary M2M relations and custom attributes from template to run."""
    for field_name in ["houses", "paths", "years", "clubs", "teaching_subjects", "blood_statuses"]:
        source = getattr(template, field_name).all()
        getattr(run, field_name).set(source)

    for attr_def in template.custom_attributes.all():
        CustomAttributeDefinition.objects.create(
            run=run,
            name=attr_def.name,
            attr_type=attr_def.attr_type,
            choices=attr_def.choices,
            applies_to=attr_def.applies_to,
            is_filterable=attr_def.is_filterable,
            sort_order=attr_def.sort_order,
        )
