from django.db import models


class Ad(models.Model):
    """Managed advertisements displayed across the site."""

    POSITION_CHOICES = [
        ('home', 'Home Page'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, help_text='Text content for text-only ads')
    is_active = models.BooleanField(default=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='home')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Messages submitted through the contact form."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Sender's IP address")
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f'{self.subject} — {self.name}'
