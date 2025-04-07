from django.db import models

class Intern(models.Model):
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=128)  # Use Django's hashing for security
    full_name = models.CharField(max_length=255)
    start_date = models.DateField()
    time_to_render = models.DurationField()  # Represents the total time to render (e.g., internship duration)
    time_rendered = models.DurationField(default="0:00:00")  # Tracks time already rendered

    def __str__(self):
        return self.full_name
