from django.db import models
from django.utils import timezone

# Create your models here.

class session(models.Model):
	sess_id = models.CharField(max_length=3)
	
	def __str__(self):
		return self.sess_id
		
class connection(models.Model):
	sess_id = models.ForeignKey(session, on_delete=models.CASCADE)
	p1 = models.CharField(max_length=200)
	p2 = models.CharField(max_length=200)
	connected = models.BooleanField(default = False)
	p1_nm = models.CharField(max_length=20, default = "null" )
	p2_nm = models.CharField(max_length=20, default = "null" )
	timestamp = models.DateTimeField(default=timezone.now)
	reset = models.BooleanField(default = False)
    
class status(models.Model):
	sess_id = models.ForeignKey(session, on_delete=models.CASCADE)
	cell_1 = models.CharField(max_length=1)
	cell_2 = models.CharField(max_length=1)
	cell_3 = models.CharField(max_length=1)
	cell_4 = models.CharField(max_length=1)
	cell_5 = models.CharField(max_length=1)
	cell_6 = models.CharField(max_length=1)
	cell_7 = models.CharField(max_length=1)
	cell_8 = models.CharField(max_length=1)
	cell_9 = models.CharField(max_length=1)
	game = models.BooleanField(default = False)
	game_state = models.CharField(max_length=5, default = "null" )
	turn = models.CharField(max_length=10, default = "null" )
	
