from django.contrib import admin

# Register your models here.
from myApp.models import  user_data, query_login, course_table, course_pdf, pdf_table, UserVoteTable, UserTagTable, UserPreviewTable, PdfTagTable

admin.site.register(user_data)
admin.site.register(query_login)
admin.site.register(course_table)
admin.site.register(course_pdf)
admin.site.register(pdf_table)
admin.site.register(UserVoteTable)
admin.site.register(UserTagTable)
admin.site.register(UserPreviewTable)
admin.site.register(PdfTagTable)
