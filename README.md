roundtwo
=======================

A simple airplane router. For ground delays' sake.


## Purpose

A simple one-pager to see current ground flight status over Lisbon airport (LPPT).

A button to press and trigger optimal routing decision for each plane, for the current plane group.


## Architecture

Django project for managing DB and simple one pager.
Periodic Celery service using flightradar24 API to insert current airplane status into the PostgreSQL db.
A Tornado web server to stream search results into the browser.


## Reference

Images used:

[plane svg] (https://commons.wikimedia.org/wiki/File:Aircraft_Airport_ecomo.svg)
[favicon] (https://commons.wikimedia.org/wiki/File:Icon-boxing-gloves.jpg)
