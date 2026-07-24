from .models import SiteProfile


def site_context(request):
    profile = SiteProfile.objects.prefetch_related("social_links").first()
    return {"site_profile": profile, "site_social_links": profile.social_links.filter(is_active=True) if profile else []}
