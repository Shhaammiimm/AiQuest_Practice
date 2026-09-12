

from django import forms


class MyForm(forms.Form):
    first_name = forms.CharField(label='Enter Your First Name', max_length=100)
    last_name = forms.CharField(label='Enter Your Last Name', max_length=100)
    email = forms.EmailField(label='Enter Your Email', initial="shamim@gmail.com", disabled=True)
    password = forms.CharField(label='Enter Your Password', widget=forms.PasswordInput)
    text_area = forms.CharField(label='Enter Your Text', widget=forms.Textarea)
    file_field = forms.FileField(label='Upload Your File')
    checkbox = forms.BooleanField(label='Accept Terms and Conditions', widget=forms.CheckboxInput, required=True)