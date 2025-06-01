from django.contrib import admin
from recommendations.models import RuleProduct, UserRecommendation, AssociationRule
admin.site.register(UserRecommendation)

class RuleProductInline(admin.TabularInline):
    model = RuleProduct
    extra = 0


@admin.register(AssociationRule)
class AssociationRuleAdmin(admin.ModelAdmin):
    list_display = ('support','confidence','lift')
    inlines = (RuleProductInline,)

# Register your models here.
@admin.register(RuleProduct)
class RuleProductAdmin(admin.ModelAdmin):
    list_display = ('rule','product','is_antecedent')
