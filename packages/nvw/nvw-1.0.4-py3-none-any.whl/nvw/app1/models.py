from django.db import models


class EnvironmentParameter(models.Model):
    env_name = models.CharField(max_length=50)
    parameters = models.TextField()
    post_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.env_name}({self.pk})({self.post_date})'


class ConfigTemplate(models.Model):
    env_name = models.CharField(max_length=50)
    template_string = models.TextField()
    post_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.env_name}({self.pk})({self.post_date})'


class ReportEntryType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.type_name}'


class Report(models.Model):
    env_name = models.CharField(max_length=50)
    report_name = models.CharField(
        max_length=50, unique=True, primary_key=True)

    def __str__(self):
        return f'{self.env_name}-{self.report_name}'


class ReportEntry(models.Model):
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, to_field='report_name')
    entry_type = models.ForeignKey(
        ReportEntryType, on_delete=models.CASCADE, to_field='type_name')
    content_file = models.FileField(null=True, blank=True, default=None)
    content_text = models.TextField(null=True, blank=True, default=None)
    post_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    meta_data = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.report}-{self.pk} ({self.entry_type})'
