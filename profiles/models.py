from django.conf import settings
from django.db import models


class Profile(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("matched", "Matched"),
        ("on_hold", "On Hold"),
    ]

    profile_id = models.CharField(max_length=50, unique=True)
    display_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    second_contact_number = models.CharField(max_length=20, blank=True, null=True)

    looking_for = models.CharField(max_length=50, blank=True, null=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)

    date_of_birth = models.CharField(max_length=50, blank=True, null=True)
    time_of_birth = models.CharField(max_length=50, blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)

    star = models.CharField(max_length=100, blank=True, null=True)
    rasi = models.CharField(max_length=100, blank=True, null=True)
    sub_caste = models.CharField(max_length=100, blank=True, null=True)
    gothram = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)

    schooling = models.CharField(max_length=255, blank=True, null=True)
    graduation = models.CharField(max_length=255, blank=True, null=True)
    masters = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    years_of_exp = models.CharField(max_length=50, blank=True, null=True)
    job_location = models.CharField(max_length=255, blank=True, null=True)
    visa_status = models.CharField(max_length=100, blank=True, null=True)

    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_native = models.CharField(max_length=255, blank=True, null=True)

    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=255, blank=True, null=True)
    mother_native = models.CharField(max_length=255, blank=True, null=True)

    siblings = models.TextField(blank=True, null=True)
    parents_staying = models.CharField(max_length=255, blank=True, null=True)

    actual_property = models.TextField(blank=True, null=True)
    shared_property = models.TextField(blank=True, null=True)
    expected_property = models.TextField(blank=True, null=True)

    preferred_height = models.CharField(max_length=50, blank=True, null=True)
    age_gap = models.CharField(max_length=50, blank=True, null=True)
    preferred_sub_caste = models.CharField(max_length=100, blank=True, null=True)
    astrology = models.CharField(max_length=100, blank=True, null=True)
    looking_country = models.CharField(max_length=100, blank=True, null=True)
    looking_state = models.CharField(max_length=100, blank=True, null=True)
    education_preference = models.CharField(max_length=255, blank=True, null=True)
    career_preferences = models.CharField(max_length=255, blank=True, null=True)
    special_conditions = models.TextField(blank=True, null=True)

    story_summary = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.display_id:
            last = Profile.objects.filter(display_id__startswith="RR-").order_by("-display_id").first()
            if last and last.display_id:
                num = int(last.display_id.split("-")[1]) + 1
            else:
                num = 1
            self.display_id = f"RR-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.display_id or self.profile_id

class GeneratedPDF(models.Model):
    TIER_CHOICES = [
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="pdfs")
    file_path = models.CharField(max_length=500)
    version = models.IntegerField(default=1)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="premium")
    template_used = models.CharField(max_length=100, default="default")
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.profile_id} - v{self.version} ({self.tier})"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("pdf_generated", "PDF Generated"),
        ("pdf_previewed", "PDF Previewed"),
        ("pdf_downloaded", "PDF Downloaded"),
        ("pdf_emailed", "PDF Emailed"),
        ("photo_uploaded", "Photo Uploaded"),
        ("photo_deleted", "Photo Deleted"),
        ("profile_synced", "Profile Synced"),
        ("bulk_pdf_generated", "Bulk PDF Generated"),
    ]

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="activities", blank=True, null=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    detail = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        name = self.profile.display_id if self.profile else "System"
        return f"{name} — {self.get_action_display()} — {self.created_at:%d %b %Y %H:%M}"


class ProfileNote(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="notes")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.profile.display_id} — {self.text[:50]}"


class Interaction(models.Model):
    TYPE_CHOICES = [
        ("phone_call", "Phone Call"),
        ("whatsapp", "WhatsApp Chat"),
        ("walkin", "Walk-in"),
        ("email", "Email"),
        ("other", "Other"),
    ]

    OUTCOME_CHOICES = [
        ("interested", "Interested"),
        ("not_interested", "Not Interested"),
        ("callback", "Call Back Later"),
        ("docs_pending", "Documents Pending"),
        ("shortlisted", "Shortlisted Match"),
        ("info_gathered", "Info Gathered"),
        ("no_answer", "No Answer"),
        ("other", "Other"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="phone_call")
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default="info_gathered")
    summary = models.TextField(help_text="Key points from the conversation")
    transcript = models.TextField(blank=True, default="", help_text="Full transcript (auto-generated from audio)")
    audio_file = models.FileField(upload_to="call_recordings/", blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.profile.display_id} — {self.get_interaction_type_display()} — {self.created_at:%d %b %Y %H:%M}"


class GenerationLog(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True, null=True)
    llm_status = models.CharField(max_length=50, blank=True, null=True)
    pdf_status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.profile_id} - {self.status}"