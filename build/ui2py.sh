pyuic5 -x resources/load.ui     -o resources/ui_scripts/load.py     --from-imports
# Compile the resources.qrc file into Python resources script
pyrcc5 -o resources/ui_scripts/res_rc.py resources/res.qrc