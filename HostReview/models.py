from django.db import models

class Profile(models.Model):
    host = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=22)

    def __str__(self):
        return f"{self.login}@{self.host}:{self.port}"

class ScanResult(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
        ('error', 'Ошибка'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='scan_results')
    log = models.TextField()
    os = models.CharField(max_length=255, blank=True)
    os_version = models.CharField(max_length=255, blank=True)
    architecture = models.CharField(max_length=255, blank=True)
    kernel = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"ScanResult for {self.profile} at {self.timestamp} with status {self.get_status_display()}"
