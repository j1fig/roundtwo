from django.db import models


class Aircraft (models.Model):
    model_name = models.CharField(max_length=255)
    flight_number = models.CharField(max_length=255)
    flight_number = models.CharField(max_length=255)
    last_node = models.ForeignKey('optimo.Node',
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='last_node')
    next_node = models.ForeignKey('optimo.Node',
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='next_node')
    percentage = models.DecimalField(max_digits=10,
                                     decimal_places=9,
                                     default=0)
    linear_speed = models.DecimalField(max_digits=20,
                                decimal_places=10,
                                default=0)
    heading = models.DecimalField(max_digits=10,
                                  decimal_places=3,
                                  default=0)
    destination = models.ForeignKey('optimo.Node',
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name='destination')
    course = models.ManyToManyField('optimo.Node')
    taxi_speed = models.DecimalField(max_digits=20,
                                decimal_places=10,
                                default=7.71666667)
    acceleration = models.DecimalField(max_digits=20,
                                decimal_places=10,
                                default=0)

class Node (models.Model):
    NODE_TYPES = (
        'gate',
        'move',
        'hold',
        'depart'
    )
    type = models.CharField()
    latitude = models.DecimalField(max_digits=13,
                                   decimal_places=10,
                                   default=0)
    longitude = models.DecimalField(max_digits=13,
                                    decimal_places=10,
                                    default=0)
