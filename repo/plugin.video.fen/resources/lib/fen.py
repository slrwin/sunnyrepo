# -*- coding: utf-8 -*-
import sys
from modules.router import routing, exit_system_check

routing(sys)
if exit_system_check(): sys.exit(1)
