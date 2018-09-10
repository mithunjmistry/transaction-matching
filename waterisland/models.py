from django.db import models


class Balances(models.Model):
    vendor = models.IntegerField()
    currency = models.CharField(max_length=45)
    trader_balance = models.DecimalField(decimal_places=2, max_digits=16, default=0.00)
    balance = models.DecimalField(decimal_places=2, max_digits=16, default=0.00)


class Institutions(models.Model):
    institution = models.CharField(max_length=150)
    code = models.CharField(max_length=45)


class Transactions(models.Model):
    vendor = models.IntegerField()
    date = models.DateField()
    institution = models.ForeignKey(Institutions, on_delete=models.CASCADE)
    trader_total = models.DecimalField(decimal_places=2, max_digits=16, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=16, default=0.00)
    comments = models.TextField(max_length=200)


class AllFiles(models.Model):
    filename = models.CharField(max_length=45)
    uploaded = models.IntegerField(default=0)
    value = models.CharField(max_length=45)

