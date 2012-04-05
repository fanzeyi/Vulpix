# Makefile console for config Vulpix
# Author: Zeray Rice <fanzeyi1994@gmail.com>

runner=$(EUID)

less:
	lessc less/style.less > static/css/style.css
run:
	./runner.sh
