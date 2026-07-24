from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Article, ContactMessage, Education, Expertise, ProfessionalExperience,
    Project, Publication, SiteProfile, Testimonial,
)


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profile = SiteProfile.objects.create(full_name="Test Professional")
        cls.article = Article.objects.create(
            title="Published reflection", slug="published-reflection",
            excerpt="A careful reflection.", body="Article body.",
            category="Practice", published_at=timezone.now(), is_published=True,
        )
        cls.draft_article = Article.objects.create(
            title="Draft reflection", slug="draft-reflection", excerpt="Draft",
            body="Draft body", category="Practice", is_published=False,
        )
        cls.project = Project.objects.create(
            title="Published project", slug="published-project",
            category="Community Development", summary="A community project.",
            status="Completed", is_published=True,
        )
        cls.draft_project = Project.objects.create(
            title="Draft project", slug="draft-project", category="Research",
            summary="Draft.", status="Planned", is_published=False,
        )

    def assert_page_ok(self, name):
        self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_home_returns_200(self): self.assert_page_ok("home")
    def test_about_returns_200(self): self.assert_page_ok("about")
    def test_cv_returns_200(self): self.assert_page_ok("cv")
    def test_articles_returns_200(self): self.assert_page_ok("articles")
    def test_publications_returns_200(self): self.assert_page_ok("publications")
    def test_experience_returns_200(self): self.assert_page_ok("experience")
    def test_projects_returns_200(self): self.assert_page_ok("projects")
    def test_gallery_returns_200(self): self.assert_page_ok("gallery")
    def test_testimonials_returns_200(self): self.assert_page_ok("testimonials")
    def test_contact_get_returns_200(self): self.assert_page_ok("contact")

    def test_published_article_detail_returns_200(self):
        self.assertEqual(self.client.get(self.article.get_absolute_url()).status_code, 200)

    def test_unpublished_article_is_not_public(self):
        self.assertEqual(self.client.get(self.draft_article.get_absolute_url()).status_code, 404)

    def test_published_project_detail_returns_200(self):
        self.assertEqual(self.client.get(self.project.get_absolute_url()).status_code, 200)

    def test_unpublished_project_is_not_public(self):
        self.assertEqual(self.client.get(self.draft_project.get_absolute_url()).status_code, 404)

    def test_optional_images_and_files_are_not_required(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Upload a professional portrait in Admin")
        self.assertNotContains(response, "cv_file.url")


class ContactTests(TestCase):
    def setUp(self):
        SiteProfile.objects.create()

    def test_valid_post_creates_message_and_redirects(self):
        response = self.client.post(reverse("contact"), {
            "name": "Community Partner", "email": "partner@example.org",
            "subject": "Research partnership", "message": "I would like to discuss a project.",
        })
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_invalid_post_shows_errors(self):
        response = self.client.post(reverse("contact"), {"name": "", "email": "not-an-email"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_duplicate_submission_is_suppressed(self):
        data = {"name": "A", "email": "a@example.org", "subject": "Hello", "message": "A meaningful message"}
        self.client.post(reverse("contact"), data)
        self.client.post(reverse("contact"), data)
        self.assertEqual(ContactMessage.objects.count(), 1)


class ModelTests(TestCase):
    def test_string_representations(self):
        profile = SiteProfile.objects.create(full_name="Professional Name")
        expertise = Expertise.objects.create(title="Community Practice", short_description="Description")
        publication = Publication.objects.create(
            title="Research title", slug="research-title", publication_type="Research Report",
            authors="Author", publication_year=2025,
        )
        education = Education.objects.create(qualification="Editable qualification", institution="Editable institution")
        self.assertEqual(str(profile), "Professional Name")
        self.assertEqual(str(expertise), "Community Practice")
        self.assertEqual(str(publication), "Research title (2025)")
        self.assertIn("Editable institution", str(education))

    def test_site_profile_is_singleton(self):
        SiteProfile.objects.create()
        with self.assertRaises(ValidationError):
            SiteProfile.objects.create()

    def test_experience_dates_validate(self):
        item = ProfessionalExperience(
            job_title="Role", organization="Organization",
            start_date=date(2025, 1, 1), end_date=date(2024, 1, 1), summary="Summary",
        )
        with self.assertRaises(ValidationError):
            item.full_clean()
