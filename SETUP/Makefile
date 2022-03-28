.PHONY: help login init set-cors destroy gen-key
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

login: ## Run GCloud and Pulumi logins
	pulumi logout
	pulumi login
	gcloud auth login
	gcloud auth application-default login

init: ## Create google project and pulumi stack
	gcloud projects create missoula-council-data-proj --set-as-default
	pulumi stack init missoula-council-data-proj

set-cors: ## Set cors for the bucket
	gsutil cors set cors.json gs://missoula-council-data-proj.appspot.com/

destroy: ## Fully teardown Pulumi and GCloud
	pulumi stack rm missoula-council-data-proj --force
	gcloud projects delete missoula-council-data-proj
	rm -f .keys/missoula-council-data-proj.json

gen-key: ## Generate a service account JSON
	mkdir .keys/ -p
	gcloud iam service-accounts create missoula-council-data-proj \
    	--description="CDP Dev Service Account for $(USER)" \
    	--display-name="missoula-council-data-proj"
	gcloud projects add-iam-policy-binding missoula-council-data-proj \
    	--member="serviceAccount:missoula-council-data-proj@missoula-council-data-proj.iam.gserviceaccount.com" \
		--role="roles/owner"
	gcloud iam service-accounts keys create .keys/missoula-council-data-proj.json \
  		--iam-account "missoula-council-data-proj@missoula-council-data-proj.iam.gserviceaccount.com"