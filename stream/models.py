# stream/models.py
from django.db import models
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Person(models.Model):
    face_id = models.CharField(max_length=64, unique=True, default=generate_uuid)
    name = models.CharField(max_length=100, blank=True, null=True)
    embedding = models.JSONField(null=True, blank=True)  
    total_detections = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.face_id[:8]

class ExpressionRecord(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="expressions")
    expression = models.CharField(max_length=50)   
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('person', 'expression')

    def __str__(self):
        return f"{self.person} - {self.expression}: {self.count}"
