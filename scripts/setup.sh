#!/usr/bin/env bash
set -e

# common stuff
PACKAGE_NAME=ouzo
#ATTEMPT_SUFFIX="-16"
SLEEP=5

source ../../scripts/common.sh

#
# TEST ACCOUNT
#
TEST_ACCOUNT_NAME=${PACKAGE_NAME}-test${ATTEMPT_SUFFIX}
TEST_ACCOUNT_EMAIL="${TEST_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
TEST_ACCOUNT="projects/${PROJECT_ID}/serviceAccounts/${TEST_ACCOUNT_EMAIL}"

gcloud \
    iam service-accounts create ${TEST_ACCOUNT_NAME} \
    --project=$PROJECT_ID \
    --display-name="${PACKAGE_NAME} test account ${ATTEMPT}" \
    --description="Test account ${ATTEMPT} for service ${PACKAGE_NAME} "
sleep $SLEEP

gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${TEST_ACCOUNT_EMAIL}" \
    --role=roles/logging.logWriter \
    --condition=None
sleep $SLEEP
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${TEST_ACCOUNT_EMAIL}" \
    --role=roles/bigquery.jobUser \
    --condition=None
sleep $SLEEP
bq \
    add-iam-policy-binding \
    --member="serviceAccount:${TEST_ACCOUNT_EMAIL}" \
    --project_id=$PROJECT_ID \
    --dataset_id=orange \
    --role=roles/bigquery.dataViewer \
    catalogo_electronico_by_gln
sleep $SLEEP

#
# BUILD ACCOUNT
#
gcloud \
    iam service-accounts create ${BUILD_ACCOUNT_NAME} \
    --project=$PROJECT_ID \
    --display-name="${PACKAGE_NAME} build account ${ATTEMPT}" \
    --description="Build account ${ATTEMPT} for service ${PACKAGE_NAME}"
sleep $SLEEP

#
# PROJECT LEVEL ROLES
#

# https://cloud.google.com/run/docs/configuring/services/build-service-account#required-roles-for-the-deployer-account
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/run.sourceDeveloper \
    --condition=None
sleep $SLEEP
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/serviceusage.serviceUsageConsumer \
    --condition=None
sleep $SLEEP
# seems to be needed both in project and in the resource... TODO check this
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/iam.serviceAccountUser \
    --condition=None
sleep $SLEEP
gcloud iam service-accounts add-iam-policy-binding "${TEST_ACCOUNT_EMAIL}" \
    --project=$PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/iam.serviceAccountUser \
    --condition=None
sleep $SLEEP

# https://cloud.google.com/run/docs/configuring/services/build-service-account#required-roles-for-the-cloud-build-service-account
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/run.builder \
    --condition=None
sleep $SLEEP

#
# REPO ROLES seems to be unnecesary because wider permissions above
#
# grants the account the role to allow it read the python repo
#gcloud \
#    artifacts repositories add-iam-policy-binding $PYTHON_REPO \
#    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
#    --role=roles/artifactregistry.reader \
#    --condition=None
#sleep $SLEEP
# grants the account the role to allow it write the image into the repo 
#gcloud \
#    artifacts repositories add-iam-policy-binding $DOCKER_REPO \
#    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
#    --role=roles/artifactregistry.writer \
#    --condition=None
#sleep $SLEEP

#
# BQ RELATED ROLES TO THE DEPLOYER TO RUN THE TESTS
#
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --role=roles/bigquery.jobUser \
    --condition=None
sleep $SLEEP

# grants the account the role over the table to allow it to read
# https://cloud.google.com/bigquery/docs/access-control
#
bq \
    add-iam-policy-binding \
    --member="serviceAccount:${BUILD_ACCOUNT_EMAIL}" \
    --project_id=$PROJECT_ID \
    --dataset_id=orange \
    --role=roles/bigquery.dataViewer \
    catalogo_electronico_by_gln
sleep $SLEEP

#
# TRIGGER TRIGGER TRIGGER 
#
# ATTENTION THIS IS NOT THE ACTUAL BUILD
#
# https://cloud.google.com/sdk/gcloud/reference/builds/triggers/create/github
#
gcloud \
    builds triggers create github \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="${PACKAGE_NAME}-trigger${ATTEMPT_SUFFIX}" \
    --service-account="${BUILD_ACCOUNT}" \
    --repo-owner="tekii" \
    --repo-name="daisy" \
    --branch-pattern="^ouzo$" \
    --included-files="ouzo_root/**" \
    --ignored-files="ouzo_root/scripts/**" \
    --build-config="ouzo_root/cloudbuild.yaml" \
    --substitutions="_CRUN_ACCOUNT=${TEST_ACCOUNT_EMAIL},_PYTHON_REPO_URL=${PYTHON_REPO_URL}"



