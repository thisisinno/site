from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("curriculum-vitae/", views.cv, name="cv"),
    path("articles/", views.articles, name="articles"),
    path("articles/<slug:slug>/", views.article_detail, name="article_detail"),
    path("articles/<slug:slug>/preview/", views.article_preview, name="article_preview"),
    path("research-publications/", views.publications, name="publications"),
    path("research-publications/<slug:slug>/", views.publication_detail, name="publication_detail"),
    path("research-publications/<slug:slug>/preview/", views.publication_preview, name="publication_preview"),
    path("professional-experience/", views.experience, name="experience"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("contact/", views.contact, name="contact"),
]
