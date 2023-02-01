# -*- coding: utf-8 -*-
import sys
from modules.router import routing, external

routing(sys)
if external(): sys.exit(1)
