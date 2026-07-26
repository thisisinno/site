from datetime import date
from textwrap import dedent

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import (
    Article, CareerMilestone, Certification, Education, Expertise, GalleryCategory,
    GalleryItem, ProfessionalExperience, Project, Publication, ResearchInterest,
    SiteProfile, Skill, Testimonial,
)


def clean(text):
    return dedent(text).strip()


class Command(BaseCommand):
    help = "Create safe Social Work defaults; use --demo for clearly labelled demonstration records."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Add non-credentialed demonstration content.")

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
            Expertise.objects.get_or_create(title=title, defaults={"short_description": description, "icon": icon, "display_order": order})

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
            ResearchInterest.objects.get_or_create(title=title, defaults={"description": description, "display_order": order})

        if not options["demo"]:
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Preserved'} site profile; safe defaults are ready. "
                "Run with --demo to add labelled sample records."
            ))
            return

        articles = [
            ("why-community-participation-matters", "Why Community Participation Matters in Sustainable Social Work Interventions", "Community Development",
             "Sustainable interventions are rarely created for communities; they are created with them. Meaningful participation strengthens ownership, relevance and long-term impact.",
             """
             Community participation is often described as a meeting, a consultation or a list of people who attended an activity. Meaningful participation is deeper. It is a continuing relationship in which people affected by a decision can shape the questions, priorities, design, implementation and review of the work. In social work, that distinction is essential because interventions touch everyday life, identity, safety and access to opportunity.

             Participatory planning begins with listening to lived experience. Community members understand local assets, informal support networks, risks and barriers that may be invisible to an external team. Listening sessions, accessible group discussions, household conversations and work with representative community structures can surface this knowledge. Good practitioners also ask who is missing. Women with care responsibilities, people with disabilities, young people and households facing stigma may require different routes into the conversation.

             Community ownership grows when people can make real choices. Inviting comments after priorities have already been fixed is not shared decision-making. A transparent process explains what is negotiable, what constraints exist and how suggestions will be used. Small working groups, community scorecards and shared action plans can turn broad consultation into accountable decisions.

             Participation also improves sustainability. When local actors understand why an activity exists, have helped adapt it and possess the skills to continue it, the work is less dependent on a short funding cycle. Sustainability does not mean transferring responsibility without resources. It means jointly considering capacity, financing, referral connections and leadership from the beginning.

             Power must remain visible throughout the process. Practitioners and institutions often control budgets, technical language and access to decision-makers. Ethical engagement requires honest reflection on that power, clear consent and safeguards against tokenism. Community representatives should not be expected to volunteer unlimited time or disclose painful experiences repeatedly for the benefit of a project.

             Feedback closes the participation loop. Communities need to hear what was learned, what changed and why some recommendations could not be adopted. Simple mechanisms—public response notes, feedback desks, trusted focal people or regular review meetings—make accountability tangible. Complaints pathways should be confidential, safe and responsive.

             Participation is therefore both a practical method and a social work value. It improves relevance, strengthens trust and affirms self-determination. Most importantly, it changes the role of the practitioner from someone who delivers solutions to someone who helps create the conditions in which collective knowledge and agency can guide change.
             """),
            ("from-data-to-dignity", "From Data to Dignity: Using Evidence Without Losing the Human Story", "Research & Evaluation",
             "Evidence can improve services, but only when measurement respects consent, context and the dignity of the people behind every data point.",
             """
             Social programs need evidence to understand reach, quality and outcomes. Quantitative data can reveal patterns: who uses a service, where gaps persist and whether change is occurring over time. Yet a percentage cannot explain how a service felt, why a family stopped attending or what dignity meant in a particular encounter.

             Qualitative evidence brings context through interviews, observation, reflective practice and stories of change. It helps practitioners understand mechanisms rather than only results. Strong evaluation brings quantitative and qualitative evidence together, treating neither as automatically superior. Administrative records may show declining attendance while conversations reveal unsafe transport, stigma or inconvenient opening hours.

             Ethical data collection starts before the first question. People should understand what is being collected, why it is needed, who will see it and whether declining will affect their access to support. Informed consent is a process, not a signature. Language, literacy, age, disability and power differences all affect whether consent is genuinely informed and voluntary.

             Research fatigue deserves serious attention. Communities may be repeatedly assessed by different organizations without seeing improvements or even receiving findings. Teams can reduce this burden by reviewing existing evidence, coordinating questions, collecting only necessary information and returning results in accessible formats.

             Protecting dignity also requires data minimization and secure handling. Sensitive details should not be collected merely because they may be interesting. Reporting must avoid combinations of details that identify a household, and stories should never be used publicly without appropriate permission and context.

             Participatory interpretation can improve accuracy. When community members, frontline workers and decision-makers examine findings together, they can challenge assumptions and identify feasible responses. This prevents an evaluation from becoming a technical document detached from practice.

             Evidence matters most when it changes services. Findings should lead to named actions, responsible people and review dates. Closing the loop with participants demonstrates that their time and knowledge were valued. A dignity-centred approach does not weaken rigor; it strengthens the relevance, ethics and practical usefulness of evidence.
             """),
            ("strengths-based-practice", "Strengths-Based Practice With Children and Families", "Child & Family Welfare",
             "Strengths-based assessment recognizes resilience and protective relationships while keeping safeguarding and children's participation firmly in view.",
             """
             Families often meet social services at moments of stress. A deficit-only assessment can reduce a complex family to risks, problems and unmet needs. Strengths-based practice widens the lens. It asks what has helped the family cope, which relationships are protective, what routines work and what hopes can motivate change.

             This approach is not unrealistic optimism. Safeguarding concerns must be assessed clearly and acted upon. The difference is that risk assessment sits alongside an understanding of capability, culture, resources and resilience. A caregiver may be struggling financially while maintaining strong emotional connection and a reliable network of relatives. Those assets matter in a practical plan.

             Children should participate in ways suited to their age, communication preferences and safety. Creative methods, careful conversation and observation can help children express what feels safe, difficult or important. Their views must be taken seriously without placing responsibility for adult decisions upon them.

             A practical assessment maps strengths at several levels: the child, family relationships, extended networks, school, community and formal services. It explores exceptions—times when the concern was less severe—and identifies what made those moments possible. Goals can then be written in observable, respectful language.

             Collaboration improves when practitioners explain concerns plainly and acknowledge effort. Families are more likely to engage when they feel heard rather than judged. Plans should identify small achievable actions, available support and how progress will be reviewed.

             Strengths-based practice ultimately protects dignity while supporting change. It allows practitioners to remain honest about harm and vulnerability without defining people by their hardest moment. That balance is central to ethical child and family social work.
             """),
            ("social-protection-more-than-assistance", "Social Protection as More Than Financial Assistance", "Social Protection",
             "Effective social protection combines material support with accessible services, dignity, community connections and pathways toward resilience.",
             """
             Cash transfers and material assistance can be vital when households face poverty, displacement, disability, illness or shocks. But vulnerability is rarely financial alone. A household may also encounter inaccessible services, discrimination, unsafe housing, caregiving pressure and weak referral networks.

             A broader social protection perspective connects income support with health, education, protection, employment and social care. The goal is not to make families navigate a maze of disconnected programs. It is to create understandable pathways and responsive systems.

             Dignity is shaped by how support is delivered. Long queues, public disclosure of vulnerability, confusing eligibility rules and disrespectful communication can undermine the value of assistance. Clear information, accessible complaints mechanisms and predictable processes are core service-quality issues.

             Community structures can improve awareness and referral when they are representative, trained and accountable. They can identify exclusion and help services adapt. They should not, however, be asked to make sensitive eligibility decisions without safeguards or replace adequately resourced professional systems.

             Resilience grows when social protection is reliable enough for households to plan, linked to quality services and responsive to changing circumstances. Learning from users is therefore essential. Social protection is most effective when it treats people not as passive recipients, but as rights-holders with knowledge, agency and aspirations.
             """),
            ("advocacy-everyday-practice", "The Role of Advocacy in Everyday Social Work Practice", "Advocacy",
             "Advocacy is not limited to public campaigns; it appears whenever social workers help people navigate systems, challenge barriers and influence fairer decisions.",
             """
             Advocacy in social work ranges from supporting one person in a service meeting to contributing evidence to policy discussion. At each level, it seeks to address an imbalance in voice, information or power.

             Individual advocacy may involve explaining rights, preparing someone to speak, requesting reasonable accommodation or coordinating a referral. The aim is not to replace a person's voice but to expand their ability to participate and decide.

             Patterns across individual cases can reveal systemic barriers. Repeated documentation problems, inaccessible facilities or harmful eligibility rules may require organizational or policy advocacy. Ethical practitioners document these patterns without exposing confidential information.

             Effective advocacy combines lived experience, practice knowledge and credible evidence. It also considers risk: public visibility can create unintended consequences for people facing stigma or insecure status. Consent and safety planning remain essential.

             Everyday advocacy is disciplined, relational work. It involves listening, mapping decision-makers, choosing realistic asks and following up. Even small procedural changes can make services more humane and accessible when they are grounded in the priorities of affected communities.
             """),
            ("building-inclusive-community-programs", "Building Inclusive Community Programs", "Gender & Social Inclusion",
             "Inclusive programs examine who can participate, who benefits and which design choices unintentionally reproduce exclusion.",
             """
             Inclusion begins before invitations are sent. Program teams need to understand how gender, age, disability, language, income, caregiving and social status shape access. A technically open activity may remain practically unavailable because of time, transport, safety or communication barriers.

             Disaggregated data can reveal differences, but numbers should be interpreted with community knowledge. Consultation needs multiple formats so participation is not limited to confident public speakers or established leaders.

             Inclusive design budgets for access. This may include accessible venues, interpretation, childcare, transport support, flexible scheduling and communication in appropriate formats. These are not optional additions; they determine who can take part.

             Representation also requires attention to influence. Having diverse people in a room does not guarantee that their perspectives shape decisions. Skilled facilitation, smaller discussion groups and transparent decision rules can make participation more equitable.

             Teams should review inclusion throughout implementation, invite confidential feedback and adapt quickly. Inclusion is an ongoing practice of noticing barriers, sharing power and being accountable for who remains at the margins.
             """),
        ]
        for index, (slug, title, category, excerpt, body) in enumerate(articles):
            Article.objects.get_or_create(slug=slug, defaults={
                "title": title, "category": category, "excerpt": excerpt, "body": clean(body),
                "author_name": "Portfolio Author — Sample Article", "published_at": timezone.now(),
                "is_published": True, "featured": index < 2,
            })

        publications = [
            ("community-participation-access-social-services", "Community Participation and Access to Social Services: A Practice-Oriented Review", "Working Paper",
             "This demonstration working paper considers how meaningful participation can influence accessibility, trust, local ownership and service uptake. It reviews practical pathways through which residents identify barriers, adapt communication, shape referral arrangements and provide feedback on service quality. Particular attention is given to groups whose perspectives may be missed by conventional consultation. The paper distinguishes attendance from influence and considers the power relationships that determine whose knowledge becomes actionable. It proposes accessible feedback loops, participatory service mapping and community scorecards as learning tools. It also notes the risks of consultation fatigue, unpaid community labor and expectations that cannot be met. The review argues that participation contributes most when organizations explain constraints, respond visibly to feedback and connect community knowledge to clear operational decisions. The record is sample content for interface demonstration and must not be represented as a verified publication."),
            ("social-protection-household-resilience", "Social Protection and Household Resilience in Vulnerable Communities", "Research Report",
             "This sample research report explores social protection as a connected system of income security, accessible services, social care and accountable referral pathways. It considers how predictable support may help households manage shocks while maintaining health, education and caregiving responsibilities. The discussion emphasizes dignity in targeting and delivery, clear communication, grievance mechanisms and attention to exclusion. It presents a practice-oriented framework for examining household resilience without placing responsibility for structural poverty on individuals. Suggested learning questions address service coordination, user experience and the role of community structures. This is demonstration content only and does not report findings from real participants."),
            ("lived-experience-monitoring-evaluation", "Integrating Lived Experience Into Program Monitoring and Evaluation", "Evaluation Report",
             "This demonstration evaluation report outlines ways to include lived experience across indicator design, data collection, interpretation and action planning. It brings together qualitative and quantitative approaches while emphasizing informed consent, data minimization and the prevention of research fatigue. The paper proposes advisory groups, accessible feedback methods and participatory sense-making sessions. It argues that engagement is meaningful only when participants can see how their knowledge changes a service. Practical cautions include confidentiality, compensation, representation and safeguarding. No real program, participant or organization is described in this sample record."),
            ("child-family-community-systems", "Strengthening Child and Family Support Through Community-Based Systems", "Policy Brief",
             "This sample policy brief considers how formal child and family services can work with safe, representative community structures. It highlights prevention, early identification, referral quality, case confidentiality and child participation. The brief cautions against shifting statutory or specialist responsibilities to unsupported volunteers. It recommends clear role definitions, supervision, safeguarding protocols and routine review of referral outcomes. A systems perspective links households, schools, health services, social workers and community groups while keeping the best interests and voice of the child central. This record is solely for portfolio demonstration."),
        ]
        for order, (slug, title, kind, abstract) in enumerate(publications, 1):
            Publication.objects.get_or_create(slug=slug, defaults={
                "title": title, "publication_type": kind, "authors": "Portfolio Author — Sample Record",
                "publication_year": timezone.now().year - (order - 1), "abstract": abstract,
                "citation": f"Portfolio Author — Sample Record ({timezone.now().year - (order - 1)}). {title}. Demonstration record; replace before launch.",
                "display_order": order, "is_published": True, "featured": order <= 3,
            })

        experiences = [
            ("Social Work & Community Engagement Practitioner — Sample", "Community-Based Organization — Replace in Admin",
             "Supporting community engagement, referral pathways, participatory program activities and initiatives designed to strengthen individual and family wellbeing."),
            ("Research, Monitoring & Learning Associate — Sample", "Social Impact Program — Replace in Admin",
             "Contributing to ethical data collection, evidence synthesis, reflective learning and accessible communication of program findings."),
            ("Program Support & Advocacy Practitioner — Sample", "Community Service Initiative — Replace in Admin",
             "Supporting inclusive program delivery, stakeholder engagement and practical advocacy around barriers to essential services."),
        ]
        responsibilities = clean("""
            Conduct community needs assessments.
            Facilitate community consultations and group discussions.
            Support referral and case coordination pathways.
            Participate in safeguarding and protection activities.
            Contribute to program monitoring and learning.
        """)
        for order, (title, organization, summary) in enumerate(experiences, 1):
            ProfessionalExperience.objects.get_or_create(job_title=title, organization=organization, defaults={
                "start_date": date(2022 + order, 1, 1), "end_date": date(2022 + order, 12, 31),
                "summary": summary, "responsibilities": responsibilities, "achievements": "Sample contribution statements must be replaced with verified information before launch.",
                "display_order": order, "is_active": True, "featured": order <= 2,
            })

        projects = [
            ("community-wellbeing-initiative", "Community Wellbeing Initiative", "Community Development"),
            ("child-family-support-mapping", "Child & Family Support Mapping", "Child Protection"),
            ("community-needs-assessment", "Community Needs Assessment", "Research"),
            ("inclusive-youth-participation", "Inclusive Youth Participation Initiative", "Gender & Inclusion"),
        ]
        for order, (slug, title, category) in enumerate(projects, 1):
            Project.objects.get_or_create(slug=slug, defaults={
                "title": title, "category": category, "role": "Demonstration professional role — Replace in Admin",
                "summary": "A demonstration community-centered initiative showing how the portfolio can present objectives, professional responsibilities and measurable learning.",
                "description": "This sample project record demonstrates a collaborative approach to planning, implementation and reflective learning. Replace it with verified project information before public launch.",
                "objectives": "Strengthen local participation.\nIdentify priority social needs.\nConnect community voices with program planning.\nImprove service awareness.",
                "outcomes": "Sample outcome area: document learning, participation and service-access improvements only after verification.",
                "status": "Completed", "display_order": order, "is_published": True, "featured": order <= 3,
            })

        skills = [
            ("Community Engagement", "Community Development"), ("Case Management", "Direct Practice"),
            ("Research & Evidence Synthesis", "Research"), ("Program Monitoring & Evaluation", "Monitoring & Evaluation"),
            ("Safeguarding", "Direct Practice"), ("Advocacy", "Advocacy"), ("Facilitation", "Facilitation"),
            ("Stakeholder Engagement", "Program Management"), ("Report Writing", "Research"), ("Program Design", "Program Management"),
        ]
        for order, (name, category) in enumerate(skills, 1):
            Skill.objects.get_or_create(name=name, category=category, defaults={"short_description": "A thematic practice skill; adjust the description and visibility in Admin.", "display_order": order})

        Education.objects.get_or_create(
            qualification="Sample Social Work Qualification — Replace in Admin",
            institution="Educational Institution — Replace in Admin",
            defaults={"field_of_study": "Social Work — Sample", "description": "DEMONSTRATION RECORD: replace with verified education before launch.", "is_published": True},
        )
        Certification.objects.get_or_create(
            title="Community-Based Practice Training — Sample",
            issuing_organization="Training Provider — Replace in Admin",
            defaults={"description": "DEMONSTRATION RECORD: replace with verified training before launch.", "is_published": True},
        )

        milestones = [
            ("Professional foundation", "Foundation in Social Work Practice"),
            ("Applied practice", "Community Engagement & Applied Practice"),
            ("Learning focus", "Research, Evaluation & Learning"),
            ("Present direction", "Current Professional Focus"),
        ]
        for order, (period, title) in enumerate(milestones, 1):
            CareerMilestone.objects.get_or_create(period=period, title=title, defaults={
                "description": "Sample milestone illustrating a broad phase of professional learning. Replace with accurate personal context in Admin.",
                "display_order": order,
            })

        testimonials = ["Sample Community Partner", "Sample Professional Colleague", "Sample Project Collaborator"]
        for order, name in enumerate(testimonials, 1):
            Testimonial.objects.get_or_create(person_name=name, defaults={
                "person_title": "Demonstration label — replace before launch",
                "quote": "Sample testimonial: replace this text with an approved statement from a real colleague, supervisor, community partner or collaborator.",
                "relationship": "SAMPLE / NOT AN ENDORSEMENT", "display_order": order,
                "is_published": True, "featured": order <= 2,
            })

        category, _ = GalleryCategory.objects.get_or_create(name="Demonstration Activities", defaults={"slug": "demonstration-activities"})
        for order, title in enumerate(["Community Engagement", "Research Workshop", "Stakeholder Consultation", "Training & Facilitation"], 1):
            GalleryItem.objects.get_or_create(category=category, title=title, defaults={
                "caption": "Branded sample placeholder. Replace with an original, consented professional image and accurate caption.",
                "alt_text": f"Sample placeholder for {title}", "display_order": order, "is_published": True,
            })

        self.stdout.write(self.style.SUCCESS(
            "Demo content is ready: 6 articles, 4 publications, 3 experience records, "
            "4 projects, 10 skills, 1 education, 1 certification, 4 milestones, "
            "3 testimonials and 4 gallery placeholders (existing records preserved)."
        ))
