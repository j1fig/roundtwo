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


class Node (models.Model):
    GATE = 'gate'
    MOVE = 'move'
    HOLD = 'hold'
    DEPART = 'depart'
    NODE_TYPES = (
        (GATE, 'gate'),
        (MOVE, 'move'),
        (HOLD, 'hold'),
        (DEPART, 'depart')
    )
    type = models.CharField(max_length=10,
                            choices=NODE_TYPES,
                            default=MOVE)
    latitude = models.DecimalField(max_digits=13,
                                   decimal_places=10,
                                   default=0)
    longitude = models.DecimalField(max_digits=13,
                                    decimal_places=10,
                                    default=0)
