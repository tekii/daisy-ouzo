#!/usr/bin/env bash
set -e

# common stuff
MODULE_NAME=ouzo
ATTEMPT_SUFFIX="-16"
SLEEP=3

source ../../scripts/common.sh

# create the account to run the build 
gcloud \
    iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --project=$PROJECT_ID \
    --display-name="Builder ${ATTEMPT_SUFFIX} ${MODULE_NAME}" \
    --description="Builder ${ATTEMPT_SUFFIX} for ${MODULE_NAME} "
sleep $SLEEP

# grants to the account the role to allow write logs to Cloud Logging (used by cloudbuild.yaml)
gcloud \
    projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role=roles/logging.logWriter \
    --condition=None
sleep $SLEEP

# grants the account the role to allow it read the python repo
gcloud \
    artifacts repositories add-iam-policy-binding $PYTHON_REPO_FULL_NAME \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role=roles/artifactregistry.reader \
    --condition=None
sleep $SLEEP

# grants the account the role to allow it write the image into the repo 
gcloud \
    artifacts repositories add-iam-policy-binding $DOCKER_REPO_FULL_NAME \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role=roles/artifactregistry.writer \
    --condition=None
sleep $SLEEP

## grants the role to allow run builds
## https://cloud.google.com/build/docs/iam-roles-permissions#predefined_roles
#gcloud projects add-iam-policy-binding $PROJECT_ID \
#    --member="serviceAccount:${SERVICE_ACCOUNT}" \
#    --role=roles/cloudbuild.serviceAgent \
##   --role="roles/storage.objectUser" -role="roles/artifactregistry.writer"


#gcloud iam service-accounts add-iam-policy-binding --project=daisy-tekii builder-tester@daisy-tekii.iam.gserviceaccount.com --role=roles/cloudbuild.serviceAgent

# create package trigger
# https://cloud.google.com/sdk/gcloud/reference/builds/triggers/create/github
gcloud \
    builds triggers create github \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="${MODULE_NAME}-trigger${ATTEMPT_SUFFIX}" \
    --service-account="projects/${PROJECT_ID}/serviceAccounts/${SERVICE_ACCOUNT}" \
    --repo-owner="tekii" \
    --repo-name="daisy" \
    --branch-pattern="^ouzo$" \
    --included-files="ouzo_root/**" \
    --build-config="ouzo_root/cloudbuild.yaml" \
    --substitutions="_CRUN_ACCOUNT=ouzo-552@daisy-dev01.iam.gserviceaccount.com,_PYTHON_REPO_URL=${PYTHON_REPO_URL}"



