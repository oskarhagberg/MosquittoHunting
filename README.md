# Mosquitto Hunting

http://www.youtube.com/watch?v=AKlkD-D20OI

or a suit of python scripts for testing and monitoring [mosquitto](http://mosquitto.org), an [MQTT](http://mqtt.org) message broker.

## Getting Started

First install Homebrew Python that comes with pip: 
(Will take a few minutes. Grab a coffee.)

    brew install python

Then install mosquitto if its not already done:

    brew install mosquitto

Finally install the python mosquitto wrapper:

    sudo pip install mosquitto

Confirm installation with:

    pydoc mosquitto

Optionally, install jsonschema

    sudo pip install jsonschema