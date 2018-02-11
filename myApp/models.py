from django.db import models

# Create your models here.
class user_data(models.Model):
    Name= models.CharField(max_length=30)
    Institution= models.CharField(max_length=30)
    Email= models.CharField(max_length=30)
    Password = models.CharField(max_length=30)

    def __str__(self):
        return self.Name

class query_login(models.Model):
    Email= models.CharField(max_length=30)
    Password = models.CharField(max_length=30)

class course_table(models.Model):
    Institution= models.CharField(max_length=30)
    department = models.CharField(max_length=30)
    LevelTerm = models.IntegerField()
    course=models.CharField(max_length=30)

class course_pdf(models.Model):
    Institution=models.CharField(max_length=30)
    course=models.CharField(max_length=30)
    pdfID=models.CharField(max_length=40)

class pdf_table(models.Model):
    pdfID = models.CharField(max_length=40)
    CourseTeacher= models.CharField(max_length=40)
    uploader= models.CharField(max_length=40)
    uploadDate=models.DateTimeField(auto_now_add=False)
    fileName= models.CharField(max_length=40)
    driveID= models.CharField(max_length=500)
    lastAccessed= models.DateTimeField(auto_now_add=False)
    vote=models.IntegerField()

class SingleLineModel(models.Model):
    Field= models.CharField(max_length=40)

class UserVoteTable(models.Model):
    pdfID = models.CharField(max_length=40)
    Email = models.CharField(max_length=30)

class DoubleLineModel(models.Model):
    field1= models.CharField(max_length=30)
    field2 = models.CharField(max_length=30)

class UserTagTable(models.Model):
    Email = models.CharField(max_length=30)
    Tag = models.CharField(max_length=30)

class UserPreviewTable(models.Model):
    Email = models.CharField(max_length=30)
    pdfID = models.CharField(max_length=30)

class PdfTagTable(models.Model):
    pdfID = models.CharField(max_length=40)
    Tag = models.CharField(max_length=30)