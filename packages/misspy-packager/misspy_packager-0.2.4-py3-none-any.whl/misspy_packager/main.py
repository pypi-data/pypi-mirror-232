from misspy_packager.packager import publish

from cleo.application import Application

def main():
    application = Application()
    application.add(publish())
    application.run()