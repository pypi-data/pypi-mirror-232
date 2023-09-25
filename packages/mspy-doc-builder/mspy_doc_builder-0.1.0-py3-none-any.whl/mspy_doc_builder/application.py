#!/usr/bin/env python

from .build import mspybuilder

from cleo.application import Application


def main():
    application = Application()
    application.add(mspybuilder())
    application.run()