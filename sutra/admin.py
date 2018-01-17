from django.contrib import admin
from sutra.models import Tripitaka, Sutra, Reel, Page, LQSutra, OImg, OCut, Batch

# Register your models here.


class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'v_no', 'v_page_no','r_page_no','img_path', 'o_img', 'o_cut']
    list_per_page = 20


class BatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'sub_date', 'org', 'des']
    list_per_page = 20


class OCutAdmin(admin.ModelAdmin):
    list_display = ['cut_code', 'batch', 'v_no', 'cut_ori', 'cut_json', 'cut_gened', 'col_json', 'col_gened', 'column_ready', 'col_no']
    list_per_page = 20
    list_filter = ['v_no', 'cut_gened']
    search_fields = ['cut_code', ]


class OImgAdmin(admin.ModelAdmin):
    list_display = ['img_code', 'v_no', 'v_page_no', 'img_path', 'big_image', 'img_1200', 'img_s3', 'img_cropped', 'width', 'height']
    list_per_page = 20
    list_filter = ['v_no', 'big_image', 'img_1200', 'img_s3', 'img_cropped']
    search_fields = ['img_code', ]


class SutraAdmin(admin.ModelAdmin):
    list_display = ['sid', 'name', 'lqsutra' ]
    list_per_page = 20


class SutraInline(admin.StackedInline):
    model = Sutra


class TripitakaAdmin(admin.ModelAdmin):
    inlines = [SutraInline]  # Inline


class LQSutraAdmin(admin.ModelAdmin):
    inlines = [SutraInline]  # Inline


class ReelInline(admin.TabularInline):
    model = Reel
    list_display = ('code',)


admin.site.register(Tripitaka, TripitakaAdmin)
admin.site.register(Sutra, SutraAdmin)
admin.site.register(LQSutra, LQSutraAdmin)
admin.site.register(OImg, OImgAdmin)
admin.site.register(OCut, OCutAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register([Reel, ])
