
.PHONY: show build taint-web taint-shell taint-machines taint-db-ebs

show:
	terraform show

build:
	terraform init
	terraform apply

taint-web:
	terraform taint aws_instance.web

taint-shell:
	terraform taint aws_instance.shell

taint-machines: taint-web taint-shell
	terraform apply

taint-db-ebs:
	terraform taint aws_ebs_volume.db_data_journal
