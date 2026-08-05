# convenience to run common ansible configurations

# for speed
ENVVAR := ANSIBLE_GATHERING=false
ANSIBLE := ansible-playbook
PLAYBOOK := site.yml

.PHONY: web-api

web-api:
	${ENVVAR} ${ANSIBLE} ${PLAYBOOK} --limit web --tags $@

web-static:
	${ENVVAR} ${ANSIBLE} ${PLAYBOOK} --limit web --tags $@

web-dev:
	${ENVVAR} ${ANSIBLE} ${PLAYBOOK} --limit web --tags web-api,web-static

shell-api:
	${ENVVAR} ${ANSIBLE} ${PLAYBOOK} --limit shell --tags $@
