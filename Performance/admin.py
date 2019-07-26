from django.contrib import admin
from .models import *
import pandas as pd
import datetime
from Performance.models import Employee, Position, Score
from daterange_filter.filter import DateRangeFilter
from django.http import HttpResponse
from io import BytesIO
import numpy as np
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ScoreAdmin(admin.ModelAdmin):
    actions = ["direct_export", "export_pivot_by_score", "export_pivot_by_position"]
    date_hierarchy = 'date'  # 详细时间分层筛选
    list_filter = (('date', DateRangeFilter), "date")
    search_fields = ['employee_name__name', 'position_name__name', 'score', 'remark']  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'employee_name', 'position_name', 'get_position_score', 'score', 'date', 'remark')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    # list_display_links = ('id', )  # 设置页面上哪个字段可单击进入详细页面
    # fields = ('category', 'book')  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示
    raw_id_fields = ('employee_name', 'position_name')
    # fieldsets = [
    #     ("学生", {'fields': ['student_name', 'school', 'grade', '_class']}),
    #     ('课程', {'fields': ['term', 'class_type', 'course_name_1', 'course_name_2', 'course_name_3']}),
    #     ('更多课程', {'fields': ['course_name_4', 'course_name_5', 'course_name_6'], 'classes': ['collapse']}),
    #     ("缴费", {'fields': ['price', 'pay_date', 'return_price', 'return_date']}),
    #     ("备注", {'fields': ['remark']}),
    # ]  # 调整分区

    def direct_export(self, request, queryset):
        outfile = BytesIO()
        data = pd.DataFrame(queryset.values())
        data = data.rename(columns={"id": "序号", "employee_name": "员工姓名", "position_name": "岗位", "score": "得分", "date": "日期", "remark": "备注"})
        data = data[["序号", "员工姓名", "岗位", "得分",  "日期", "备注"]]
        data = data.sort_values(by=["序号"], ascending=True)
        data = data.fillna("")
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename="{}"'.format("Direct export " + filename + ".xlsx")
        data.to_excel(outfile, index=False)
        response.write(outfile.getvalue())
        return response

    def export_pivot_by_score(self, request, queryset):
        outfile = BytesIO()
        data = pd.DataFrame(queryset.values())
        data = data.rename(columns={"id": "序号", "employee_name_id": "员工姓名", "position_name_id": "岗位", "score": "得分", "date": "日期", "remark": "备注"})
        data = data[["员工姓名", "岗位", "得分",  "日期", "备注"]]
        data = data.sort_values(by=["员工姓名"], ascending=True)
        data = data.fillna("")
        position_data = Position.objects.values()
        position_data = pd.DataFrame(position_data)
        position_data = position_data.rename(columns={"id": "序号", "name": "岗位", "score": "岗位分数"})
        position_data = position_data[["岗位", "岗位分数"]]
        data = pd.merge(data, position_data, on="岗位", how="left")
        data["得分"] = data["得分"] + data["岗位分数"]
        data = pd.pivot_table(data, values=["得分"], index=["员工姓名"], aggfunc=np.sum)
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename="{}"'.format("Export pivot by score " + filename + ".xlsx")
        data.to_excel(outfile)
        response.write(outfile.getvalue())
        return response

    def export_pivot_by_position(self, request, queryset):
        outfile = BytesIO()
        data = pd.DataFrame(queryset.values())
        data = data.rename(columns={"id": "序号", "employee_name_id": "员工姓名", "position_name_id": "岗位", "score": "得分", "date": "日期", "remark": "备注"})
        data = data[["员工姓名", "岗位", "得分",  "日期", "备注"]]
        data["岗位次数"] = data["岗位"]
        data = data.sort_values(by=["员工姓名"], ascending=True)
        data = data.fillna("")
        data = pd.pivot_table(data, values=["岗位次数"], index=["员工姓名", "岗位"], aggfunc=np.count_nonzero)
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename="{}"'.format("Export pivot by position " + filename + ".xlsx")
        data.to_excel(outfile)
        response.write(outfile.getvalue())
        return response

    direct_export.short_description = '直接导出'
    export_pivot_by_score.short_description = '统计分数'
    export_pivot_by_position.short_description = '统计岗位次数'


class PositionAdmin(admin.ModelAdmin):
    list_filter = ('name', 'score')  # 过滤器
    search_fields = ['name', 'score']  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'name', 'score')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'name')  # 设置页面上哪个字段可单击进入详细页面
    # list_editable = ['name', 'score']  # 直接编辑字段
    # fields = ('category', 'book')  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示


class EmployeeAdmin(admin.ModelAdmin):
    list_filter = ('sex', )  # 过滤器
    search_fields = ['name', 'sex', 'staff_id']  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'name', 'sex', 'staff_id')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'name')  # 设置页面上哪个字段可单击进入详细页面
    # list_editable = ['name', 'sex', 'staff_id']  # 直接编辑字段
    # fields = ('category', 'book')  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Score, ScoreAdmin)


admin.site.site_header = 'ICC绩效管理系统'
admin.site.site_title = 'ICC绩效管理'
admin.site.index_title = 'ICC绩效管理'