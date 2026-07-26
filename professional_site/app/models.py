from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    display_order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        abstract = True


class SiteProfile(TimeStampedModel):
    full_name = models.CharField(max_length=160, blank=True, default="")
    credentials = models.CharField(max_length=160, blank=True, default="")
    professional_title = models.CharField(
        max_length=220,
        default="Social Work Practitioner, Researcher & Community Development Professional",
    )
    professional_subtitle = models.CharField(max_length=240, blank=True, default="Advancing dignity, inclusion and community wellbeing")
    welcome_eyebrow = models.CharField(max_length=120, default="Social Work • Research • Community Impact")
    welcome_heading = models.CharField(max_length=180, default="Welcome to Jesca Social Work")
    hero_intro = models.TextField(default="I am a social work professional committed to strengthening individuals, families and communities through compassionate practice, research, advocacy and evidence-informed interventions.")
    mission_statement = models.TextField(default="To advance social justice, human dignity and community wellbeing through ethical social work practice, research, advocacy and sustainable community engagement.")
    professional_philosophy = models.TextField(default="Meaningful social change begins by listening to communities, respecting human dignity and transforming evidence into practical action.")
    about_short = models.TextField(default="My work is grounded in empathy, ethical practice and partnership with communities. I bring together social work practice, research and advocacy to support inclusive and sustainable change.")
    about_full = models.TextField(blank=True, default="This portfolio presents a developing record of professional practice, research interests and community engagement. Personal biographical details can be added here through the administration area.")
    populations_of_interest = models.TextField(blank=True, default="Children and families; vulnerable and underserved populations; women and young people; community-based organizations.")
    key_competencies = models.TextField(blank=True, default="Ethical social work practice\nCommunity engagement and facilitation\nResearch and evidence synthesis\nProgram design, monitoring and evaluation\nPolicy analysis and advocacy")
    professional_values = models.TextField(blank=True, default="Human dignity\nSocial justice\nIntegrity and accountability\nInclusion and participation\nEvidence-informed practice")
    profile_photo = models.ImageField(upload_to="profile/", blank=True)
    profile_photo_alt = models.CharField(max_length=220, blank=True, default="Professional portrait")
    portrait_focus_x = models.PositiveSmallIntegerField(
        default=50, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Horizontal crop focus, from 0 (left) to 100 (right).",
    )
    portrait_focus_y = models.PositiveSmallIntegerField(
        default=25, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Vertical crop focus, from 0 (top) to 100 (bottom).",
    )
    portrait_zoom = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.08,
        validators=[MinValueValidator(1.0), MaxValueValidator(1.3)],
        help_text="Portrait crop zoom between 1.00 and 1.30.",
    )
    secondary_photo = models.ImageField(upload_to="profile/", blank=True)
    cv_file = models.FileField(upload_to="cv/", blank=True, help_text="Upload a current PDF curriculum vitae.")
    email = models.EmailField(blank=True)
    secondary_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=60, blank=True)
    location = models.CharField(max_length=180, blank=True)
    website_name = models.CharField(max_length=140, default="Jesca Social Work")
    footer_statement = models.CharField(max_length=280, default="Ethical social work, rigorous research and meaningful community partnership.")
    copyright_name = models.CharField(max_length=160, blank=True)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)

    class Meta:
        verbose_name = "site profile"
        verbose_name_plural = "site profile"

    def __str__(self):
        return self.full_name or self.website_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteProfile.objects.exists():
            raise ValidationError("Only one site profile may be created.")
        super().save(*args, **kwargs)


class SocialLink(OrderedModel, TimeStampedModel):
    PLATFORM_CHOICES = [(x, x) for x in ("LinkedIn", "ResearchGate", "ORCID", "Google Scholar", "X / Twitter", "Facebook", "Instagram", "YouTube", "Other")]
    profile = models.ForeignKey(SiteProfile, related_name="social_links", on_delete=models.CASCADE)
    platform = models.CharField(max_length=40, choices=PLATFORM_CHOICES)
    label = models.CharField(max_length=80)
    url = models.URLField()
    icon_class = models.CharField(max_length=80, blank=True, help_text="Optional Bootstrap Icons class, e.g. bi bi-linkedin.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("display_order", "platform")

    def __str__(self):
        return self.label


class Expertise(OrderedModel, TimeStampedModel):
    title = models.CharField(max_length=140, unique=True)
    short_description = models.TextField()
    icon = models.CharField(max_length=80, blank=True, help_text="Bootstrap Icons class.")
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "title"); verbose_name_plural = "areas of expertise"
    def __str__(self): return self.title


class ImpactMetric(OrderedModel, TimeStampedModel):
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=30, blank=True, help_text="Leave blank until a verified value is available.")
    suffix = models.CharField(max_length=20, blank=True)
    short_description = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "label")
    def __str__(self): return self.label


class CareerMilestone(OrderedModel, TimeStampedModel):
    period = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    organization = models.CharField(max_length=180, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="milestones/", blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "period")
    def __str__(self): return f"{self.period} — {self.title}"


class Education(OrderedModel, TimeStampedModel):
    qualification = models.CharField(max_length=180)
    field_of_study = models.CharField(max_length=180, blank=True)
    institution = models.CharField(max_length=180)
    location = models.CharField(max_length=160, blank=True)
    start_year = models.PositiveSmallIntegerField(blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-end_year")
    def __str__(self): return f"{self.qualification} — {self.institution}"


class Certification(OrderedModel, TimeStampedModel):
    title = models.CharField(max_length=180)
    issuing_organization = models.CharField(max_length=180)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    credential_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-year")
    def __str__(self): return self.title


class Award(OrderedModel, TimeStampedModel):
    title = models.CharField(max_length=180)
    organization = models.CharField(max_length=180, blank=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-year")
    def __str__(self): return self.title


class ProfessionalMembership(OrderedModel, TimeStampedModel):
    organization = models.CharField(max_length=180)
    membership_title = models.CharField(max_length=180, blank=True)
    start_year = models.PositiveSmallIntegerField(blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "organization")
    def __str__(self): return self.organization


class Skill(OrderedModel, TimeStampedModel):
    CATEGORIES = [(x, x) for x in ("Direct Practice", "Community Development", "Research", "Monitoring & Evaluation", "Advocacy", "Policy", "Facilitation", "Program Management", "Other")]
    name = models.CharField(max_length=140)
    category = models.CharField(max_length=60, choices=CATEGORIES)
    short_description = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "category", "name")
    def __str__(self): return self.name


class Article(TimeStampedModel):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    excerpt = models.TextField()
    body = models.TextField()
    cover_image = models.ImageField(upload_to="articles/", blank=True)
    cover_image_alt = models.CharField(max_length=220, blank=True)
    category = models.CharField(max_length=100)
    author_name = models.CharField(max_length=160, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=320, blank=True)
    class Meta: ordering = ("-published_at", "-created_at")
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse("article_detail", kwargs={"slug": self.slug})
    @property
    def reading_time(self):
        return max(1, round(len(self.body.split()) / 220))


class Publication(OrderedModel, TimeStampedModel):
    TYPES = [(x, x) for x in ("Journal Article", "Research Report", "Evaluation Report", "Policy Brief", "Book / Book Chapter", "Conference Paper", "Working Paper", "Thesis / Dissertation", "Other")]
    title = models.CharField(max_length=260)
    slug = models.SlugField(max_length=280, unique=True)
    publication_type = models.CharField(max_length=50, choices=TYPES)
    authors = models.CharField(max_length=500)
    journal_or_publisher = models.CharField(max_length=240, blank=True)
    publication_year = models.PositiveSmallIntegerField()
    volume = models.CharField(max_length=30, blank=True)
    issue = models.CharField(max_length=30, blank=True)
    pages = models.CharField(max_length=40, blank=True)
    abstract = models.TextField(blank=True)
    citation = models.TextField(blank=True)
    doi = models.CharField(max_length=180, blank=True)
    external_url = models.URLField(blank=True)
    document = models.FileField(upload_to="publications/", blank=True)
    cover_image = models.ImageField(upload_to="publications/covers/", blank=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-publication_year", "title")
    def __str__(self): return f"{self.title} ({self.publication_year})"
    def get_absolute_url(self): return reverse("publication_detail", kwargs={"slug": self.slug})


class ResearchInterest(OrderedModel, TimeStampedModel):
    title = models.CharField(max_length=160, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "title")
    def __str__(self): return self.title


class ProfessionalExperience(OrderedModel, TimeStampedModel):
    job_title = models.CharField(max_length=180)
    organization = models.CharField(max_length=180)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    summary = models.TextField()
    responsibilities = models.TextField(blank=True, help_text="One item per line.")
    achievements = models.TextField(blank=True, help_text="One item per line.")
    organization_logo = models.ImageField(upload_to="organizations/", blank=True)
    organization_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ("display_order", "-start_date")
    def __str__(self): return f"{self.job_title} — {self.organization}"
    def clean(self):
        if self.is_current and self.end_date:
            raise ValidationError({"end_date": "A current role should not have an end date."})
        if not self.is_current and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be earlier than start date."})


class Project(OrderedModel, TimeStampedModel):
    CATEGORIES = [(x, x) for x in ("Community Development", "Research", "Advocacy", "Child Protection", "Social Protection", "Gender & Inclusion", "Monitoring & Evaluation", "Training / Capacity Building", "Other")]
    STATUS = [(x, x) for x in ("Planned", "In progress", "Completed", "Ongoing")]
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    category = models.CharField(max_length=60, choices=CATEGORIES)
    role = models.CharField(max_length=160, blank=True)
    organization_or_client = models.CharField(max_length=180, blank=True)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    summary = models.TextField()
    description = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    outcomes = models.TextField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True)
    image_alt = models.CharField(max_length=220, blank=True)
    external_url = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS, default="Planned")
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-start_date", "title")
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse("project_detail", kwargs={"slug": self.slug})
    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be earlier than start date."})


class GalleryCategory(OrderedModel, TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    class Meta: ordering = ("display_order", "name"); verbose_name_plural = "gallery categories"
    def __str__(self): return self.name


class GalleryItem(OrderedModel, TimeStampedModel):
    category = models.ForeignKey(GalleryCategory, related_name="items", on_delete=models.PROTECT)
    title = models.CharField(max_length=180)
    image = models.ImageField(upload_to="gallery/", blank=True)
    alt_text = models.CharField(max_length=220, blank=True)
    caption = models.TextField(blank=True)
    event_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=160, blank=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "-event_date", "title")
    def __str__(self): return self.title


class Testimonial(OrderedModel, TimeStampedModel):
    person_name = models.CharField(max_length=160)
    person_title = models.CharField(max_length=160, blank=True)
    organization = models.CharField(max_length=180, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True)
    quote = models.TextField()
    relationship = models.CharField(max_length=180, blank=True)
    source_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    class Meta: ordering = ("display_order", "person_name")
    def __str__(self): return self.person_name


class ContactMessage(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    organization = models.CharField(max_length=180, blank=True)
    subject = models.CharField(max_length=220)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    class Meta: ordering = ("-created_at",)
    def __str__(self): return f"{self.subject} — {self.name}"
