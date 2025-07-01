from django.db import models
from datetime import date

STATUS_CHOICE = [
    ('Active', 'Active'),
    ('In-Active', 'In-Active'),
]

ROLE_CHOICE = [
    ('Admin', 'Admin'),
    ('Employee', 'Employee')
]

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    pin = models.CharField(max_length=4)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='Active')
    role = models.CharField(max_length=10, choices=ROLE_CHOICE, default='Employee')
    total_cs_leave = models.PositiveIntegerField(default=0)
    total_e_leave = models.PositiveIntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

LEAVE_TYPE_CHOICE = [
    ('CS', 'Sick/Casual'),
    ('E', 'Earned'),
]

class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=2, choices=LEAVE_TYPE_CHOICE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    date_applied = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
