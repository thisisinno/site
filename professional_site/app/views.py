from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ContactForm
from .models import *


def home(request):
    return render(request, "app/home.html", {
        "expertise": Expertise.objects.filter(is_active=True)[:8],
        "metrics": ImpactMetric.objects.filter(is_active=True).exclude(value="")[:4],
        "publications": Publication.objects.filter(is_published=True, featured=True)[:3],
        "experience": ProfessionalExperience.objects.filter(is_active=True, featured=True)[:3],
        "projects": Project.objects.filter(is_published=True, featured=True)[:3],
        "articles": Article.objects.filter(is_published=True)[:4],
        "testimonials": Testimonial.objects.filter(is_published=True, featured=True)[:3],
    })


def about(request):
    return render(request, "app/about.html", {
        "milestones": CareerMilestone.objects.filter(is_active=True),
        "expertise": Expertise.objects.filter(is_active=True),
        "awards": Award.objects.filter(is_published=True),
        "memberships": ProfessionalMembership.objects.filter(is_published=True),
    })


def cv(request):
    return render(request, "app/cv.html", {
        "education": Education.objects.filter(is_published=True),
        "experience": ProfessionalExperience.objects.filter(is_active=True),
        "skills": Skill.objects.filter(is_active=True),
        "certifications": Certification.objects.filter(is_published=True),
        "awards": Award.objects.filter(is_published=True),
        "memberships": ProfessionalMembership.objects.filter(is_published=True),
        "publications": Publication.objects.filter(is_published=True)[:6],
    })


def articles(request):
    qs = Article.objects.filter(is_published=True)
    category = request.GET.get("category", "")
    if category: qs = qs.filter(category=category)
    return render(request, "app/articles/list.html", {
        "page_obj": Paginator(qs, 9).get_page(request.GET.get("page")),
        "featured_article": qs.filter(featured=True).first(),
        "categories": Article.objects.filter(is_published=True).values_list("category", flat=True).distinct(),
        "selected_category": category,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    related = Article.objects.filter(is_published=True, category=article.category).exclude(pk=article.pk)[:3]
    return render(request, "app/articles/detail.html", {"article": article, "related_articles": related})

def article_preview(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "app/articles/_preview.html", {"article": article})


def publications(request):
    qs = Publication.objects.filter(is_published=True)
    publication_type, year = request.GET.get("type", ""), request.GET.get("year", "")
    if publication_type: qs = qs.filter(publication_type=publication_type)
    if year.isdigit(): qs = qs.filter(publication_year=int(year))
    return render(request, "app/publications/list.html", {
        "publications": qs, "interests": ResearchInterest.objects.filter(is_active=True),
        "types": Publication.TYPES, "years": Publication.objects.filter(is_published=True).values_list("publication_year", flat=True).distinct().order_by("-publication_year"),
        "selected_type": publication_type, "selected_year": year,
    })

def publication_detail(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_published=True)
    related = Publication.objects.filter(
        is_published=True, publication_type=publication.publication_type
    ).exclude(pk=publication.pk)[:3]
    return render(request, "app/publications/detail.html", {
        "publication": publication, "related_publications": related,
    })

def publication_preview(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_published=True)
    return render(request, "app/publications/_preview.html", {"publication": publication})


def experience(request): return render(request, "app/experience.html", {"experience": ProfessionalExperience.objects.filter(is_active=True)})
def projects(request): return render(request, "app/projects/list.html", {"projects": Project.objects.filter(is_published=True)})
def project_detail(request, slug): return render(request, "app/projects/detail.html", {"project": get_object_or_404(Project, slug=slug, is_published=True)})


def gallery(request):
    items = GalleryItem.objects.filter(is_published=True).select_related("category")
    category = request.GET.get("category", "")
    if category: items = items.filter(category__slug=category)
    return render(request, "app/gallery.html", {"items": items, "categories": GalleryCategory.objects.all(), "selected_category": category})


def testimonials(request): return render(request, "app/testimonials.html", {"testimonials": Testimonial.objects.filter(is_published=True)})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        recent = request.session.get("last_contact_submission")
        if form.is_valid():
            if recent and timezone.now().timestamp() - recent < 30:
                messages.info(request, "Your message has already been received.")
            else:
                form.save()
                request.session["last_contact_submission"] = timezone.now().timestamp()
                messages.success(request, "Thank you. Your message has been received.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "app/contact.html", {"form": form})


def custom_404(request, exception): return render(request, "app/404.html", status=404)
