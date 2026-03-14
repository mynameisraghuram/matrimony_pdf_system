from django import forms
from profiles.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["profile_id", "display_id", "story_summary", "photo", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-control form-control-sm", "rows": 2})
            else:
                field.widget.attrs.update({"class": "form-control form-control-sm"})

        # Make at least first_name or full_name required
        self.fields["first_name"].required = True

        # Looking for as select
        self.fields["looking_for"].widget = forms.Select(
            choices=[("", "—"), ("Bride", "Bride"), ("Groom", "Groom")],
            attrs={"class": "form-select form-select-sm"},
        )

        # Marital status as select
        self.fields["marital_status"].widget = forms.Select(
            choices=[
                ("", "—"),
                ("Unmarried", "Unmarried"),
                ("Divorced", "Divorced"),
                ("Widowed", "Widowed"),
                ("Separated", "Separated"),
            ],
            attrs={"class": "form-select form-select-sm"},
        )

        # Status as select
        self.fields["status"].widget = forms.Select(
            choices=Profile.STATUS_CHOICES,
            attrs={"class": "form-select form-select-sm"},
        )
