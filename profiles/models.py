from django.db import models


class Profile(models.Model):
    profile_id = models.CharField(max_length=50, unique=True)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.profile_id
    

class GeneratedPDF(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="pdfs")
    file_path = models.CharField(max_length=500)
    version = models.IntegerField(default=1)
    template_used = models.CharField(max_length=100, default="default")
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.profile_id} - v{self.version}"


class GenerationLog(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True, null=True)
    llm_status = models.CharField(max_length=50, blank=True, null=True)
    pdf_status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.profile_id} - {self.status}"