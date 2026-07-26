import re
from pathlib import Path

from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import GalleryBulkUploadForm
from .models import *

admin.site.site_header = "Jesca Social Work Administration"
admin.site.site_title = "Jesca Social Work Admin"
admin.site.index_title = "Content Management"


def thumbnail(obj, field_name):
    image = getattr(obj, field_name, None)
    return format_html('<img src="{}" alt="" style="width:68px;height:68px;object-fit:cover;border-radius:6px">', image.url) if image else "—"


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    fields = ("platform", "label", "url", "icon_class", "display_order", "is_active")


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    inlines = (SocialLinkInline,)
    readonly_fields = ("profile_preview", "created_at", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "credentials", "professional_title", "professional_subtitle", "website_name")}),
        ("Hero & Introduction", {"fields": ("welcome_eyebrow", "welcome_heading", "hero_intro", "about_short")}),
        ("Mission & Biography", {"fields": ("mission_statement", "professional_philosophy", "about_full", "populations_of_interest", "key_competencies", "professional_values")}),
        ("Contact Information", {"fields": ("email", "secondary_email", "phone", "location")}),
        ("Professional Portrait", {"fields": (
            "profile_photo", "profile_preview", "profile_photo_alt",
            "portrait_focus_x", "portrait_focus_y", "portrait_zoom",
        )}),
        ("Other Files & Images", {"fields": ("secondary_photo", "cv_file")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Footer", {"fields": ("footer_statement", "copyright_name")}),
        ("Record information", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    def has_add_permission(self, request): return not SiteProfile.objects.exists()
    @admin.display(description="Portrait")
    def profile_preview(self, obj): return thumbnail(obj, "profile_photo")


class PublishableAdmin(admin.ModelAdmin):
    actions = ("publish", "unpublish", "feature", "unfeature")
    @admin.action(description="Publish selected")
    def publish(self, request, queryset): queryset.update(is_published=True)
    @admin.action(description="Unpublish selected")
    def unpublish(self, request, queryset): queryset.update(is_published=False)
    @admin.action(description="Mark selected as featured")
    def feature(self, request, queryset): queryset.update(featured=True)
    @admin.action(description="Remove featured status")
    def unfeature(self, request, queryset): queryset.update(featured=False)


class OrderedActiveAdmin(admin.ModelAdmin):
    list_display = ("__str__", "display_order", "is_active", "updated_at")
    list_editable = ("display_order", "is_active")
    ordering = ("display_order",)


admin.site.register(Expertise, OrderedActiveAdmin)
admin.site.register(ImpactMetric, OrderedActiveAdmin)
admin.site.register(CareerMilestone, OrderedActiveAdmin)
admin.site.register(ResearchInterest, OrderedActiveAdmin)
admin.site.register(Skill, OrderedActiveAdmin)


class CVRecordAdmin(admin.ModelAdmin):
    list_display = ("__str__", "display_order", "is_published", "updated_at")
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published",)
    ordering = ("display_order",)


@admin.register(Education)
class EducationAdmin(CVRecordAdmin):
    search_fields = ("qualification", "field_of_study", "institution")
    list_display = ("qualification", "institution", "end_year", "display_order", "is_published")

@admin.register(Certification)
class CertificationAdmin(CVRecordAdmin):
    search_fields = ("title", "issuing_organization", "description")


@admin.register(Award)
class AwardAdmin(CVRecordAdmin):
    search_fields = ("title", "organization", "description")


@admin.register(ProfessionalMembership)
class MembershipAdmin(CVRecordAdmin):
    search_fields = ("organization", "membership_title", "description")


@admin.register(Article)
class ArticleAdmin(PublishableAdmin):
    list_display = ("image_preview", "title", "category", "published_at", "is_published", "featured")
    list_filter = ("is_published", "featured", "category", "published_at")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("title", "slug", "category", "author_name")}),
        ("Article", {"fields": ("excerpt", "body")}),
        ("Cover", {"fields": ("cover_image", "image_preview", "cover_image_alt")}),
        ("Publishing", {"fields": ("published_at", "is_published", "featured")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Record information", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    @admin.display(description="Cover")
    def image_preview(self, obj): return thumbnail(obj, "cover_image")


@admin.register(Publication)
class PublicationAdmin(PublishableAdmin):
    list_display = ("image_preview", "title", "publication_type", "publication_year", "featured", "is_published", "display_order")
    list_editable = ("featured", "is_published", "display_order")
    list_filter = ("publication_type", "publication_year", "featured", "is_published")
    search_fields = ("title", "authors", "journal_or_publisher", "abstract", "citation")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("title", "slug", "publication_type", "authors")}),
        ("Bibliographic Information", {"fields": ("journal_or_publisher", "publication_year", "volume", "issue", "pages")}),
        ("Abstract & Citation", {"fields": ("abstract", "citation")}),
        ("Links & Document", {"fields": ("doi", "external_url", "document", "cover_image", "image_preview")}),
        ("Publishing", {"fields": ("is_published", "featured")}),
        ("Display", {"fields": ("display_order",)}),
        ("Record Information", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    @admin.display(description="Cover")
    def image_preview(self, obj): return thumbnail(obj, "cover_image")


@admin.register(ProfessionalExperience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("job_title", "organization", "start_date", "is_current", "featured", "is_active", "display_order")
    list_editable = ("featured", "is_active", "display_order")
    list_filter = ("is_current", "featured", "is_active")
    search_fields = ("job_title", "organization", "summary", "responsibilities", "achievements")
    date_hierarchy = "start_date"


@admin.register(Project)
class ProjectAdmin(PublishableAdmin):
    list_display = ("image_preview", "title", "category", "status", "featured", "is_published", "display_order")
    list_editable = ("featured", "is_published", "display_order")
    list_filter = ("category", "status", "featured", "is_published")
    search_fields = ("title", "summary", "description", "organization_or_client")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    @admin.display(description="Image")
    def image_preview(self, obj): return thumbnail(obj, "image")


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GalleryItem)
class GalleryItemAdmin(PublishableAdmin):
    change_list_template = "admin/app/galleryitem/change_list.html"
    list_display = ("image_preview", "title", "category", "event_date", "featured", "is_published", "display_order")
    list_editable = ("featured", "is_published", "display_order")
    list_filter = ("category", "featured", "is_published")
    search_fields = ("title", "caption", "location")
    readonly_fields = ("image_preview", "created_at", "updated_at")
    @admin.display(description="Image")
    def image_preview(self, obj): return thumbnail(obj, "image")

    def get_urls(self):
        return [
            path(
                "bulk-upload/",
                self.admin_site.admin_view(self.bulk_upload_view),
                name="app_galleryitem_bulk_upload",
            ),
        ] + super().get_urls()

    @staticmethod
    def _title_from_filename(filename):
        stem = Path(filename).stem
        stem = re.sub(r"^(img|dsc|pxl)[-_]?\d+[-_]?", "", stem, flags=re.I)
        stem = re.sub(r"[_-]+", " ", stem)
        stem = re.sub(r"\s+", " ", stem).strip()
        return stem.title() or "Community Moment"

    def bulk_upload_view(self, request):
        if not self.has_add_permission(request):
            return HttpResponseForbidden("You do not have permission to add gallery images.")
        if request.method == "POST":
            form = GalleryBulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploads = form.cleaned_data["images"]
                highest = GalleryItem.objects.aggregate(Max("display_order"))["display_order__max"] or 0
                with transaction.atomic():
                    for offset, upload in enumerate(uploads, 1):
                        title = self._title_from_filename(upload.name)
                        prefix = form.cleaned_data["title_prefix"].strip()
                        if prefix:
                            title = f"{prefix} — {title}"
                        GalleryItem.objects.create(
                            image=upload,
                            title=title[:180],
                            alt_text=title[:220],
                            category=form.cleaned_data["category"],
                            event_date=form.cleaned_data["event_date"],
                            location=form.cleaned_data["location"],
                            caption=form.cleaned_data["caption"],
                            featured=form.cleaned_data["mark_featured"],
                            is_published=form.cleaned_data["publish_immediately"],
                            display_order=highest + offset,
                        )
                self.message_user(
                    request,
                    f"{len(uploads)} gallery images uploaded successfully. Review titles and alternative text for accessibility before publishing.",
                    messages.SUCCESS,
                )
                return redirect(reverse("admin:app_galleryitem_changelist"))
        else:
            form = GalleryBulkUploadForm()
        return render(request, "admin/app/galleryitem/bulk_upload.html", {
            **self.admin_site.each_context(request),
            "form": form,
            "title": "Upload Multiple Images",
            "opts": self.model._meta,
        })


@admin.register(Testimonial)
class TestimonialAdmin(PublishableAdmin):
    list_display = ("photo_preview", "person_name", "organization", "featured", "is_published", "display_order")
    list_editable = ("featured", "is_published", "display_order")
    list_filter = ("featured", "is_published")
    search_fields = ("person_name", "organization", "quote")
    readonly_fields = ("photo_preview", "created_at", "updated_at")
    @admin.display(description="Photo")
    def photo_preview(self, obj): return thumbnail(obj, "photo")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "is_read", "is_replied")
    list_filter = ("is_read", "is_replied", "created_at")
    search_fields = ("name", "email", "organization", "subject", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("name", "email", "phone", "organization", "subject", "message", "created_at")
    actions = ("mark_read", "mark_replied")
    @admin.action(description="Mark selected as read")
    def mark_read(self, request, queryset): queryset.update(is_read=True)
    @admin.action(description="Mark selected as replied")
    def mark_replied(self, request, queryset): queryset.update(is_replied=True, is_read=True)
