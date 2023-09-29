from django.db import models

class Activity(models.Model):
    name = models.CharField(max_length=100 , unique=True )
    def __str__(self):
        return self.name

class Hour(models.Model):
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.activity:
            return self.activity.name
        else:
            return "No Activity"

