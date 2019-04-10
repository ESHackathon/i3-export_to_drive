.PHONY: build test
default: build

build:
	docker build -t eshackathon/i3_export_to_drive .

test:
	-rm -rf /tmp/i3-export_to_drive
	mkdir /tmp/i3-export_to_drive
	cp test.json /tmp/i3-export_to_drive/test.json
	docker run -e LANG=C.UTF-8 --volume /tmp/i3-export_to_drive:/app/work eshackathon/i3_export_to_drive work/test.json > /tmp/i3-export_to_drive/output.txt
	@echo --- START OUTPUT ---
	@cat /tmp/i3-export_to_drive/output.txt
	@echo --- END OUTPUT ---
	-rm -rf /tmp/i3-export_to_drive

shell:
	docker run -it --entrypoint=/bin/sh eshackathon/i3_export_to_drive
