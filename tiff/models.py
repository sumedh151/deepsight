from django.db import models

class TifImage(models.Model):
	image = models.FileField(upload_to = 'tif-images/' , null = True , blank = True)