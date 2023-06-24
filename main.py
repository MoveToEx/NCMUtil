import sys
import importlib as il

argv = sys.argv[1:]

if not argv[0]:
    print("No module specified")
    exit()

module = il.import_module('modules.' + argv[0])

module.main(argv[1:])
