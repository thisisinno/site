from django.core.management.base import BaseCommand
from app.models import Expertise, ResearchInterest, SiteProfile


class Command(BaseCommand):
    help = "Create or refresh safe generic Social Work portfolio defaults."

    def handle(self, *args, **options):
        profile, created = SiteProfile.objects.get_or_create(pk=1)
        expertise = [
            ("Social Work Practice", "Ethical, person-centred practice that promotes dignity, resilience and self-determination.", "bi bi-people"),
            ("Community Development", "Participatory approaches that strengthen local capacity, ownership and sustainable community wellbeing.", "bi bi-diagram-3"),
            ("Child & Family Welfare", "Strengths-based support for child protection, family wellbeing and safe, nurturing environments.", "bi bi-heart"),
            ("Social Protection", "Inclusive systems and programs that reduce vulnerability and improve access to essential support.", "bi bi-shield-check"),
            ("Mental Health & Psychosocial Support", "Compassionate, trauma-aware approaches to psychosocial wellbeing and community support.", "bi bi-chat-heart"),
            ("Gender & Social Inclusion", "Practice and advocacy that address exclusion and expand equitable participation.", "bi bi-universal-access"),
            ("Research & Evaluation", "Rigorous inquiry, learning and evaluation that translate evidence into practical improvement.", "bi bi-journal-check"),
            ("Policy & Advocacy", "Evidence-led engagement that elevates community voices and advances social justice.", "bi bi-megaphone"),
        ]
        for order, (title, description, icon) in enumerate(expertise, 1):
            Expertise.objects.update_or_create(title=title, defaults={"short_description": description, "icon": icon, "display_order": order, "is_active": True})
        interests = [
            ("Child and Family Welfare", "Systems, services and community conditions that support children and families to thrive."),
            ("Community Development", "Participatory, asset-based approaches to inclusive and sustainable local development."),
            ("Gender and Social Inclusion", "Barriers to participation and approaches that strengthen equity, voice and belonging."),
            ("Social Protection", "Policies and programs that reduce poverty, risk and vulnerability across the life course."),
            ("Mental Health and Psychosocial Support", "Accessible, culturally responsive approaches to individual and community wellbeing."),
            ("Youth Development", "Opportunities, protective factors and systems that enable young people to participate and flourish."),
            ("Poverty and Vulnerability", "Structural drivers of disadvantage and locally grounded pathways toward resilience."),
            ("Program Monitoring & Evaluation", "Ethical measurement and learning that improve program quality and accountability."),
            ("Evidence-Informed Social Work Practice", "Connecting research, practitioner expertise and lived experience in responsible decisions."),
        ]
        for order, (title, description) in enumerate(interests, 1):
            ResearchInterest.objects.update_or_create(title=title, defaults={"description": description, "display_order": order, "is_active": True})
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} site profile; seeded {len(expertise)} expertise areas and {len(interests)} research interests."))
