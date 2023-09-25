import subprocess
import os
import shutil

from cleo.commands.command import Command
from cleo.helpers import argument, option

class mspybuilder(Command):
    name = "build"
    description = "build misspy documents"

    def handle(self):
        cwd = os.getcwd()
        subprocess.run("make html", shell=True)
        subprocess.run("make html", shell=True)
        os.chdir(os.path.join(cwd, "en"))
        subprocess.run("make html", shell=True)
        os.chdir(cwd)
        shutil.move('en/build', os.path.join(cwd, "build/en"))
        print("成功✨")
