import random

from django import template

from posts.models import Rumor

register = template.Library()


@register.inclusion_tag("player/partials/_rumor_banner.html")
def random_rumor(run):
    if not run:
        return {"rumor": None}
    post_ids = (
        Rumor.objects.filter(post__run=run, post__is_published=True)
        .values_list("post_id", flat=True)
        .distinct()
    )
    if not post_ids:
        return {"rumor": None}
    chosen_post_id = random.choice(list(post_ids))
    rumor = (
        Rumor.objects.filter(post_id=chosen_post_id)
        .select_related("post__casting")
        .order_by("?")
        .first()
    )
    return {"rumor": rumor, "run": run}
