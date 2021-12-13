from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.instance_loaders import CachedInstanceLoader
from django import forms
from django.forms import Textarea
from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


from .models import *

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


class CourseStepInline(SortableInlineAdminMixin, admin.StackedInline):
    model = CourseStep
    extra = 1

    fields = (
        ('day_number', 'time'),
        ('test', 'survey'),
        'text_message',
        ('text_message_image', 'text_message_file')
    )

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [
        CourseStepInline,
    ]


class TrainingStepInline(SortableInlineAdminMixin, admin.TabularInline):
    model = TrainingStep


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    inlines = [
        TrainingStepInline,
    ]


@admin.register(TrainingStep)
class TrainingStepAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(TestEvent)
class TestEventAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(CourseStep)
class CourseStepAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class TicketMessageInline(admin.StackedInline):
    model = TicketMessage
    extra = 0

    fields = (
        'message_type', 'text',
        'image', 'created_at'
    )

    readonly_fields = (
        'created_at', 'message_type'
    )

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [
        TicketMessageInline
    ]

    readonly_fields = (
        'problem_type', 'bot_problem_type',
    )


class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = [
            'text',
            'answer_1', 'answer_1_weight',
            'answer_2', 'answer_2_weight',
            'answer_3', 'answer_3_weight',
            'answer_4', 'answer_4_weight',
            'answer_5', 'answer_5_weight',
            'answer_6', 'answer_6_weight',
        ]

    images = forms.FileField(label='images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))


class TestQuestionInline(SortableInlineAdminMixin, admin.StackedInline):
    model = TestQuestion
    extra = 0
    form = TestQuestionForm


class TestEventInline(SortableInlineAdminMixin, admin.TabularInline):
    model = TestEvent
    extra = 1


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [
        TestQuestionInline, TestEventInline
    ]


class SurveyQuestionInline(SortableInlineAdminMixin, admin.StackedInline):
    model = SurveyQuestion
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    inlines = [
        SurveyQuestionInline
    ]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses_passed', 'current_courses')
    search_fields = ['phone', 'name', 'handle']
    list_display = ['phone', 'name', 'handle', 'is_tester']


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    fields = (
        'id',
        'name'
    )

    readonly_fields = (
        'id',
    )


class BulkSaveMixin:
    """
    Overridden to store instance so that it can be imported in bulk.
    https://github.com/django-import-export/django-import-export/issues/939#issuecomment-509435531
    """
    bulk_instances = []

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        self.before_save_instance(instance, using_transactions, dry_run)
        if not using_transactions and dry_run:
            # we don't have transactions and we want to do a dry_run
            pass
        else:
            self.bulk_instances.append(instance)
        self.after_save_instance(instance, using_transactions, dry_run)

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        if self.bulk_instances:
            try:
                self._meta.model.objects.bulk_create(self.bulk_instances)
            except Exception as e:
                # Be careful with this
                # Any exceptions caught here will be raised.
                # However, if the raise_errors flag is False, then the exception will be
                # swallowed, and the row_results will look like the import was successful.
                # Setting raise_errors to True will mitigate this because the import process will
                # clearly fail.
                # To be completely correct, any errors here should update the result / row_results
                # accordingly.
                raise e
            finally:
                self.bulk_instances.clear()


class AccessCodeResource(BulkSaveMixin, resources.ModelResource):
    # related_item = fields.Field(
    #     column_name='course_category_id',
    #     attribute='course_category_id',
    #     widget=widgets.IntegerWidget(),
    # )

    class Meta:
        model = AccessCode
        use_bulk = True
        batch_size = 500
        force_init_instance = True
        skip_diff = True
        skip_unchanged = True
        instance_loader_class = CachedInstanceLoader


@admin.register(AccessCode)
class AccessCodeAdmin(ImportExportModelAdmin):
    resource_class = AccessCodeResource
    skip_admin_log = True
    list_display = ('code', 'is_active')


models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
