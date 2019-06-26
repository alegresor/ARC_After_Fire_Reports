from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length = 200)
    department = models.CharField(max_length=4, choices=(('MATH', 'Math'), ('CS', 'Computer Science')), default='MATH')
    number = models.IntegerField()
    season = models.CharField(max_length=6, choices=(('Fall','Fall'), ('Spring','Spring'), ('Summer','Summer')), default='FA')
    year = models.IntegerField()
    description = models.CharField(max_length = 500)
    files = models.FileField(upload_to='courseUploads/', default=settings.MEDIA_ROOT+'/errorFile.txt')
    
    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length = 200)
    collaborators = models.CharField(max_length = 200)
    publication = models.CharField(max_length = 200)
    date = models.DateField()
    files = models.FileField(upload_to='projectUploads/', default=settings.MEDIA_ROOT+'/errorFile.txt')
    contentType = models.CharField(max_length=2, choices=(('TA', 'Talk'), ('PO', 'Poster'), ('PA', 'Paper')), default='PA')

    def __str__(self):
        return self.title
