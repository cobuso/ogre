help:
	@echo 'Usage:'
	@echo '   make local           local build of vagrant box for staging; useful for debugging'
	@echo '   make staging         local build of staging AMI on EC2'
	@echo '   make atlas           start remote Atlas build of staging AMI on EC2'


local:
	cd provision/staging && \
	time $$GOPATH/src/github.com/mitchellh/packer/bin/packer build -force \
	  -only=vmware-iso \
		-var "git_revision=$$(git log -1 --oneline --abbrev-commit | cut -d\  -f 1)" \
		-var sesame_password=eggsbacon \
		-var salt_version=v2015.8.3 \
		local.json

staging:
	cd provision/staging && \
	time $$GOPATH/src/github.com/mitchellh/packer/bin/packer build -force \
	  -only=amazon-ebs \
		-var "git_revision=$$(git log -1 --oneline --abbrev-commit | cut -d\  -f 1)" \
		-var sesame_password=eggsbacon \
		-var salt_version=v2015.8.3 \
		local.json

atlas:
	cd provision/staging && \
		packer push atlas.json

.PHONY: help local staging atlas
