roundtwo
=======================

A simple airplane router. For ground delays' sake.


## Purpose

A simple one-pager to see current ground flight status over Lisbon airport (LPPT).

A button to press and trigger optimal routing decision for each plane, for the current plane group.


## Architecture

Periodic Celery service using flightradar24 API to insert current airplane status into the PostgreSQL db.
