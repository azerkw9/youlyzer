import re
from django import forms
from .models import ContactMessage, Ad


class YouTubeURLForm(forms.Form):
    """Form for submitting a YouTube video or channel URL."""

    url = forms.URLField(
        label='',
        widget=forms.URLInput(attrs={
            'placeholder': 'Enter YouTube URL (video or channel)',
            'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 '
                     'placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 '
                     'focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200',
            'id': 'youtube-url-input',
            'autocomplete': 'off',
        }),
    )

    def clean_url(self):
        url = self.cleaned_data['url'].strip()
        youtube_patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
            r'(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/(channel|c|user|@)[\w/-]+',
        ]
        if not any(re.match(p, url) for p in youtube_patterns):
            raise forms.ValidationError('Please enter a valid YouTube video or channel URL.')
        return url


class ContactForm(forms.ModelForm):
    """Contact page form."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 '
                         'placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 '
                         'focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200',
                'id': 'contact-name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your@email.com',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 '
                         'placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 '
                         'focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200',
                'id': 'contact-email',
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Subject',
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 '
                         'placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 '
                         'focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200',
                'id': 'contact-subject',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Your message...',
                'rows': 5,
                'class': 'w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 '
                         'placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 '
                         'focus:ring-2 focus:ring-indigo-500/20 transition-all duration-200 resize-none',
                'id': 'contact-message',
            }),
        }


class AdForm(forms.ModelForm):
    """Form for creating/editing ads in custom admin."""

    class Meta:
        model = Ad
        fields = ['title', 'image', 'link', 'text', 'is_active', 'position']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 text-gray-900 '
                         'focus:outline-none focus:border-indigo-500 transition-all duration-200',
            }),
            'link': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 text-gray-900 '
                         'focus:outline-none focus:border-indigo-500 transition-all duration-200',
                'placeholder': 'https://example.com',
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 text-gray-900 '
                         'focus:outline-none focus:border-indigo-500 transition-all duration-200 resize-none',
                'rows': 3,
            }),
            'position': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 text-gray-900 '
                         'focus:outline-none focus:border-indigo-500 transition-all duration-200',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-indigo-600 border-gray-300 focus:ring-indigo-500',
            }),
        }
