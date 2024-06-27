# qgc-aurelia-planner
Quick project for converting GeoJson files into QGroundControl plans for Aurelia X6 spraying system.

A quick project of mine to convert annotation data from pix4field into a spraying plan for a Aurelia X6 spraying system.
Currely only planning on supporting GeoJson, thought is goepanda supports kml / shape files it should be easy to change to it instead.

## TODO
* Set flight order based on shortest distance.
* Insert spraying stop and start command between points / polygons.
* Might need to add takeoff and land commands.
* Adjust speed and hight over longer distances?
* Instead of using multiple travel points on plolygons lines might make things less verbose.
* Add options for rally points and geofences.
