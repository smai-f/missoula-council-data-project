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
	gcloud projects create missoula-mt-council-data --set-as-default
	pulumi stack init missoula-mt-council-data

set-cors: ## Set cors for the bucket
	gsutil cors set cors.json gs://missoula-mt-council-data.appspot.com/

destroy: ## Fully teardown Pulumi and GCloud
	pulumi stack rm missoula-mt-council-data --force
	gcloud projects deletemissoula-mt-council-data 
	rm -f .keys/missoula-mt-council-data.json

gen-key: ## Generate a service account JSON
	mkdir .keys/ -p
	gcloud iam service-accounts create missoula-mt-council-data \
    	--description="CDP Dev Service Account for $(USER)" \
    	--display-name="missoula-mt-council-data"
	gcloud projects add-iam-policy-binding missoula-mt-council-data \
    	--member="serviceAccount:missoula-mt-council-data@missoula-mt-council-data.iam.gserviceaccount.com" \
		--role="roles/owner"
	gcloud iam service-accounts keys create .keys/missoula-mt-council-data.json \
  		--iam-account "missoula-mt-council-data@missoula-mt-council-data.iam.gserviceaccount.com"