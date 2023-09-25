import re
from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html


def extra_field_name(func):
    def wrapper(self, field_name):
        def inner(obj):
            return func(self, obj, field_name)

        inner.__name__ = field_name
        return inner

    return wrapper


class CustomAdmin(admin.ModelAdmin):
    blur_fields = ()
    email_fields = ()
    search_fields = ("first_name", "last_name")

    class Media:
        js = (
            "//ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js",
            "js/listDisplay.js",
        )

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__(model, admin_site)

        email_fields = self.get_email_fields()
        blur_fields = self.get_blur_fields()

        self.list_display = self.list_display + email_fields + blur_fields

    def get_blur_fields(
        self,
    ):
        blur_fields = []
        if self.blur_fields:
            for field in self.blur_fields:
                field_name = f"__blur_{field}"
                setattr(self, field_name, self._blur_field(field))
                blur_fields.append(field_name)

        return (
            tuple(blur_fields) if isinstance(self.list_display, tuple) else blur_fields
        )

    def get_email_fields(
        self,
    ):
        email_fields = []
        if self.email_fields:
            for field in self.email_fields:
                field_name = f"__email_{field}"
                setattr(self, field_name, self._email_field(field))
                email_fields.append(field_name)

        return (
            tuple(email_fields)
            if isinstance(self.list_display, tuple)
            else email_fields
        )

    @admin.display(description="Blurred field")
    @extra_field_name
    def _blur_field(self, obj, field_name):
        return format_html(
            "<span style='filter: blur(10px); cursor: pointer;' onclick='unblur(this)'>{}</span>",
            getattr(obj, field_name),
        )

    @extra_field_name
    @admin.display(description="Email address field")
    def _email_field(self, obj, field_name):
        return format_html(
            "<a href='mailto:{0}'>{0}</a>",
            getattr(obj, field_name),
        )

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Any], search_term: str
    ) -> tuple[QuerySet[Any], bool]:
        pattern = r"(?P<first_name>.+)-\/\|\\-(?P<last_name>.+)"
        match = re.match(pattern, search_term)
        use_distinct = False

        if search_term:
            if match is not None:
                search_term = f"{match.group('first_name')} {match.group('last_name')}"
                queryset, use_distinct = super(CustomAdmin, self).get_search_results(
                    request, queryset, search_term
                )
            else:
                queryset = queryset.none()

        return queryset, use_distinct
