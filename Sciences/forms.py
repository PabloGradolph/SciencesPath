from django import forms


class CommentForm(forms.Form):
    name = forms.CharField(label="Escribe tu nombre")
    url = forms.URLField(label="Tu sitio web", required=False)
    comment = forms.CharField()