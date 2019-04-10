#!/usr/bin/env python
# encoding: utf-8
# PYTHON_ARGCOMPLETE_OK

from functools import partial

from . import printer_console
from . import printer_gui

class Mode:
	NumOfModes=2
	Console, GUI = range(NumOfModes)

# this is WET, but i didn't find any way to make it DRY.
pr = printer_console.pr
prcolor = printer_console.prcolor
ask = printer_console.ask
pprgr = printer_console.pprgr

def setmode(mode, *arg):
	global pr
	global prcolor
	global ask
	global pprgr
	if mode == Mode.Console:
		pr = printer_console.pr
		prcolor = printer_console.prcolor
		ask = printer_console.ask
		pprgr = printer_console.pprgr
	elif mode == Mode.GUI:
		inst = arg[0]
		pr = partial(printer_gui.pr, inst)
		prcolor = partial(printer_gui.prcolor, inst)
		ask = partial(printer_gui.ask, inst)
		pprgr = partial(printer_gui.pprgr, inst)

# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4 ff=unix fileencoding=utf-8
