from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth import get_user_model


sex_selection = (
    ("M", "男"),
    ("F", "女"),
)


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, unique=True, verbose_name="姓名")
    sex = models.CharField(max_length=2, choices=sex_selection, verbose_name="性别")
    staff_id = models.CharField(max_length=11, blank=True, null=True, verbose_name="工号")

    class Meta:
        verbose_name = '人员'
        verbose_name_plural = "人员"

    def __str__(self):
        return self.name


class Position(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=30, unique=True, verbose_name="岗位名称")
    score = models.IntegerField(verbose_name="基础分数")

    class Meta:
        verbose_name = '岗位'
        verbose_name_plural = "岗位"

    def __str__(self):
        return self.name


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Score(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    employee_name = models.ForeignKey("Employee", on_delete=models.DO_NOTHING, to_field="name", related_name="employee", verbose_name="员工姓名")
    position_name = models.ForeignKey("Position", on_delete=models.DO_NOTHING, to_field="name", related_name="position", verbose_name="岗位")
    score = models.FloatField(max_length=10, verbose_name="评分")
    date = models.DateField(default=timezone.now, verbose_name="日期")
    remark = models.TextField(max_length=100, blank=True, null=True, verbose_name="备注")

    # 可在list display中增加该方法名称，以展示数据
    def get_position_score(self):
        return self.position_name.score

    get_position_score.short_description = "岗位分数"

    class Meta:
        verbose_name = '评分'
        verbose_name_plural = "评分"
