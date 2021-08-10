from django.db import models


class Employee(models.Model):
    empno = models.IntegerField()
    ename = models.CharField(max_length=50)
    esalary = models.FloatField()
    eaddress = models.CharField(max_length=200)

    def __str__(self):
        return self.ename
