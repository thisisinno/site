from io import BytesIO
from datetime import date
from tempfile import TemporaryDirectory
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Article, ContactMessage, Education, Expertise, ProfessionalExperience,
    GalleryCategory, GalleryItem, Project, Publication, SiteProfile, Testimonial,
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
        cls.publication = Publication.objects.create(
            title="Published research", slug="published-research",
            publication_type="Research Report", authors="Sample Author",
            publication_year=2026, abstract="A substantial published abstract.",
            is_published=True,
        )
        cls.draft_publication = Publication.objects.create(
            title="Draft research", slug="draft-research",
            publication_type="Working Paper", authors="Sample Author",
            publication_year=2026, abstract="A draft abstract.", is_published=False,
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

    def test_published_article_preview_returns_content(self):
        response = self.client.get(reverse("article_preview", args=[self.article.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.body)

    def test_unpublished_article_preview_is_not_public(self):
        self.assertEqual(self.client.get(reverse("article_preview", args=[self.draft_article.slug])).status_code, 404)

    def test_published_publication_detail_and_preview(self):
        detail = self.client.get(self.publication.get_absolute_url())
        preview = self.client.get(reverse("publication_preview", args=[self.publication.slug]))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, self.publication.title)
        self.assertContains(preview, self.publication.abstract)

    def test_unpublished_publication_is_not_public(self):
        self.assertEqual(self.client.get(self.draft_publication.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(reverse("publication_preview", args=[self.draft_publication.slug])).status_code, 404)

    def test_key_routes_reverse(self):
        self.assertEqual(reverse("articles"), "/articles/")
        self.assertEqual(reverse("publication_detail", args=["record"]), "/research-publications/record/")
        self.assertEqual(reverse("publication_preview", args=["record"]), "/research-publications/record/preview/")

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

    def test_csrf_middleware_protects_contact_post(self):
        csrf_client = Client(enforce_csrf_checks=True)
        data = {
            "name": "Community Partner", "email": "partner@example.org",
            "subject": "Protected request", "message": "A valid message.",
        }
        self.assertEqual(csrf_client.post(reverse("contact"), data).status_code, 403)
        response = csrf_client.get(reverse("contact"))
        data["csrfmiddlewaretoken"] = response.cookies["csrftoken"].value
        self.assertEqual(csrf_client.post(reverse("contact"), data).status_code, 302)


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

    def test_portrait_crop_boundaries_validate(self):
        for kwargs in (
            {"portrait_focus_x": -1},
            {"portrait_focus_x": 101},
            {"portrait_focus_y": 101},
            {"portrait_zoom": 1.31},
            {"portrait_zoom": .99},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValidationError):
                    SiteProfile(**kwargs).full_clean()


class GalleryBulkUploadAdminTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_directory = TemporaryDirectory()
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media_override.disable()
        cls.media_directory.cleanup()

    @classmethod
    def setUpTestData(cls):
        cls.category = GalleryCategory.objects.create(name="Community", slug="community")
        cls.superuser = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="test-password"
        )
        cls.staff_without_permission = get_user_model().objects.create_user(
            username="staff", password="test-password", is_staff=True
        )

    @staticmethod
    def image_file(name, color="green"):
        output = BytesIO()
        Image.new("RGB", (3, 3), color).save(output, format="PNG")
        return SimpleUploadedFile(name, output.getvalue(), content_type="image/png")

    def test_bulk_url_requires_authenticated_staff(self):
        url = reverse("admin:app_galleryitem_bulk_upload")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_without_add_permission_cannot_upload(self):
        self.client.force_login(self.staff_without_permission)
        self.assertEqual(
            self.client.get(reverse("admin:app_galleryitem_bulk_upload")).status_code,
            403,
        )

    def test_three_images_create_three_ordered_published_items(self):
        GalleryItem.objects.create(
            category=self.category, title="Existing", display_order=7
        )
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("admin:app_galleryitem_bulk_upload"), {
            "category": self.category.pk,
            "title_prefix": "Workshop",
            "publish_immediately": "on",
            "images": [
                self.image_file("community-workshop-2026.png"),
                self.image_file("family-support.png", "blue"),
                self.image_file("IMG_20260726_152344.png", "red"),
            ],
        })
        self.assertRedirects(response, reverse("admin:app_galleryitem_changelist"))
        created = list(GalleryItem.objects.exclude(title="Existing").order_by("display_order"))
        self.assertEqual(len(created), 3)
        self.assertEqual([item.display_order for item in created], [8, 9, 10])
        self.assertTrue(all(item.category == self.category for item in created))
        self.assertTrue(all(item.is_published for item in created))
        self.assertTrue(all(item.title and item.alt_text for item in created))

    def test_zero_images_and_invalid_file_show_useful_errors(self):
        self.client.force_login(self.superuser)
        url = reverse("admin:app_galleryitem_bulk_upload")
        response = self.client.post(url, {"category": self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at least one image")
        response = self.client.post(url, {
            "category": self.category.pk,
            "images": SimpleUploadedFile("not-image.txt", b"not an image", "text/plain"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not-image.txt")
        self.assertEqual(GalleryItem.objects.count(), 0)

    def test_single_gallery_item_workflow_remains_available(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("admin:app_galleryitem_add"), {
            "category": self.category.pk,
            "title": "Single image",
            "alt_text": "A single accessible image",
            "display_order": 1,
        })
        self.assertRedirects(response, reverse("admin:app_galleryitem_changelist"))
        self.assertTrue(GalleryItem.objects.filter(title="Single image").exists())


class SeedCommandTests(TestCase):
    def test_demo_seed_is_idempotent(self):
        call_command("seed_portfolio", "--demo", verbosity=0)
        first = (Article.objects.count(), Publication.objects.count(), Project.objects.count())
        call_command("seed_portfolio", "--demo", verbosity=0)
        self.assertEqual(first, (Article.objects.count(), Publication.objects.count(), Project.objects.count()))
        self.assertGreaterEqual(first[0], 6)
        self.assertGreaterEqual(first[1], 4)
