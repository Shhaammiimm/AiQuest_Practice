
from django import forms
from .models import UserInfo


class MyForm(forms.ModelForm):

    repassword = forms.CharField(
        label='Enter Your Password Again',
        widget=forms.PasswordInput
    )

    class Meta:
        model = UserInfo
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'repassword',
            'text_area',
            'file_field',
            'checkbox',
        ]

        labels = {
            'first_name': 'Enter Your First Name',
            'last_name': 'Enter Your Last Name',
            'email': 'Enter Your Email',
            'password': 'Enter Your Password',
            'text_area': 'Enter Your Text',
            'file_field': 'Upload Your File',
            'checkbox': 'Accept Terms and Conditions',
        }

        widgets = {
            'password': forms.PasswordInput(),
            'text_area': forms.Textarea(),
        }


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")

        if password != repassword:
            raise forms.ValidationError(
                "Password and Re-entered Password do not match."
            )

        return cleaned_data


