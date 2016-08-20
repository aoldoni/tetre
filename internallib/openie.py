#!/usr/bin/env python

def openie_to_pretty(entry):
    return entry[2].strip() + " ( " + entry[1].strip() + " , " + entry[3].strip() + " ) - " + entry[0].strip()