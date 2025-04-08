#!/usr/bin/env bash
set -e

# common stuff
MODULE_NAME=ouzo
#ATTEMPT_SUFFIX="-16"
SLEEP=5

source ../../scripts/common.sh

# create the account to run the build 
gcloud \
    iam service-accounts create ${DEPLOY_ACCOUNT_NAME} \
    --project=$PROJECT_ID \
    --display-name="${MODULE_NAME}-deployer${ATTEMPT_SUFFIX}" \
    --description="Deployer${ATTEMPT_SUFFIX} for ${MODULE_NAME} "
sleep $SLEEP

#
# PROJECT LEVEL ROLES
#

# grants to the account the role to allow write logs to Cloud Logging (used by cloudbuild.yaml)
#gcloud \
#    projects add-iam-policy-binding $PROJECT_ID \
#    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
#    --role=roles/logging.logWriter \
#    --condition=None
#sleep $SLEEP

# https://cloud.google.com/run/docs/configuring/services/build-service-account#required-roles-for-the-deployer-account
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/run.sourceDeveloper \
    --condition=None
sleep $SLEEP
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/serviceusage.serviceUsageConsumer \
    --condition=None
sleep $SLEEP
# seems to be needed both in project and in the resource... TODO check this
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/iam.serviceAccountUser \
    --condition=None
sleep $SLEEP
gcloud iam service-accounts add-iam-policy-binding "projects/daisy-dev01/serviceAccounts/ouzo-552@daisy-dev01.iam.gserviceaccount.com" \
    --project=$PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/iam.serviceAccountUser \
    --condition=None
sleep $SLEEP

# https://cloud.google.com/run/docs/configuring/services/build-service-account#required-roles-for-the-cloud-build-service-account
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/run.builder \
    --condition=None
sleep $SLEEP

#
# REPO ROLES seems to be unnecesary because wider permissions above
#
# grants the account the role to allow it read the python repo
#gcloud \
#    artifacts repositories add-iam-policy-binding $PYTHON_REPO_FULL_NAME \
#    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
#    --role=roles/artifactregistry.reader \
#    --condition=None
#sleep $SLEEP
# grants the account the role to allow it write the image into the repo 
#gcloud \
#    artifacts repositories add-iam-policy-binding $DOCKER_REPO_FULL_NAME \
#    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
#    --role=roles/artifactregistry.writer \
#    --condition=None
#sleep $SLEEP

#
# BQ RELATED ROLES TO THE DEPLOYER TO RUN THE TESTS
#
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --role=roles/bigquery.jobUser \
    --condition=None
sleep $SLEEP

# grants the account the role over the table to allow it to read
# https://cloud.google.com/bigquery/docs/access-control
#
bq \
    add-iam-policy-binding \
    --member="serviceAccount:${DEPLOY_ACCOUNT}" \
    --project_id=$PROJECT_ID \
    --dataset_id=orange \
    --role=roles/bigquery.dataViewer \
    catalogo_electronico_by_gln
sleep $SLEEP

#
# TRIGGER
# https://cloud.google.com/sdk/gcloud/reference/builds/triggers/create/github
#
gcloud \
    builds triggers create github \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="${MODULE_NAME}-trigger${ATTEMPT_SUFFIX}" \
    --service-account="projects/${PROJECT_ID}/serviceAccounts/${DEPLOY_ACCOUNT}" \
    --repo-owner="tekii" \
    --repo-name="daisy" \
    --branch-pattern="^ouzo$" \
    --included-files="ouzo_root/**" \
    --ignored-files="ouzo_root/scripts/**" \
    --build-config="ouzo_root/cloudbuild.yaml" \
    --substitutions="_CRUN_ACCOUNT=ouzo-552@daisy-dev01.iam.gserviceaccount.com,_PYTHON_REPO_URL=${PYTHON_REPO_URL}"



