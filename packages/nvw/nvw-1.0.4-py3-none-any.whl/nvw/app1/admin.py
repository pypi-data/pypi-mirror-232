from django.contrib import admin

from .models import EnvironmentParameter, ConfigTemplate, Report, ReportEntry, ReportEntryType


@admin.register(EnvironmentParameter)
class ParamAdmin(admin.ModelAdmin):
    pass


@admin.register(ConfigTemplate)
class TplAdmin(admin.ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportEntry)
class ReportEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportEntryType)
class ReportEntryTypeAdmin(admin.ModelAdmin):
    pass
