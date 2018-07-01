from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from cms.models import *

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


# Create your models here.
class test(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)
        verbose_name_plural = '根'


class test0(models.Model):
    lists = models.CharField(choices=STYLE_CHOICES, default='', max_length=100)
    str = models.CharField(max_length=20)

    def __str__(self):
        return self.lists

    class Meta:
        verbose_name_plural = '根0'


class test00(models.Model):
    lists = models.CharField(choices=STYLE_CHOICES, default='', max_length=100)
    str = models.CharField(max_length=20)

    def __str__(self):
        return self.lists

    class Meta:
        verbose_name_plural = '根00'


class test000(models.Model):
    lists = models.ForeignKey(test00, default='', on_delete=models.CASCADE)
    str = models.CharField(max_length=20)

    def __str__(self):
        # 这个比较神奇 在test000添加条目时 取得值type test00 貌似因为你自己添加条目是参照外键的 然后又返回这个对象而不是对应的字符串
        # 也就是说 外键参考的字段 要格式化返回
        return '{}'.format(self.lists)

    class Meta:
        verbose_name_plural = '根000'


class test1(models.Model):
    title = models.ForeignKey(test, on_delete=models.CASCADE, verbose_name='参照基础表')
    list = models.OneToOneField(test0, null=True, on_delete=models.CASCADE, default='', verbose_name='一对一 根0')
    list0 = models.ManyToManyField(test00, default='', verbose_name='多对多 根00')
    list00 = models.ForeignKey(test000, null=True, default='', on_delete=models.CASCADE, verbose_name='参照 根000')
    str = models.CharField(max_length=100, blank=True)

    def get_many(self):
        return "\n".join([p.lists for p in self.list0.all()])

    class Meta:
        verbose_name_plural = '实验'


class Authority(models.Model):
    TRUN = ((0, '决赛'), (1, '半决赛'), (2, '初赛'), (3, '复赛'), (4, '组合制决赛'), (6, '组合制初赛'),)

    usernamex = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='users', verbose_name='用户')
    eventsx = models.ForeignKey(Events, on_delete=models.CASCADE, verbose_name='赛事')
    eventTypex = models.ForeignKey(EventType, on_delete=models.CASCADE, verbose_name='类型')
    # single=models.DecimalField(verbose_name='单次',max_digits=5,decimal_places=2)
    # single = models.TimeField(verbose_name='单次', default='0')
    # average = models.TimeField(verbose_name='平均', default='0')
    single = models.CharField(verbose_name='单次', max_length=10, default='0')
    average = models.CharField(verbose_name='平均', max_length=10, default='0')
    detail = models.CharField(verbose_name='详情', max_length=50, blank=True)
    turn = models.SmallIntegerField(verbose_name='轮次', choices=TRUN, default=0)

    class Meta:
        verbose_name_plural = '官方记录'  # ordering = ('username',)
