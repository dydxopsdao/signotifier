#!/bin/bash

# This script is used to trigger a CodeBuild build and wait for it to complete.
# It is invoked by the Terraform's "external" data source.
# See: https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external

# Exit if any of the intermediate steps fail
set -e

# Extract arguments from the input into shell variables.
# jq will ensure that the values are properly quoted
# and escaped for consumption by the shell.
eval "$(jq -r '@sh "REGION=\(.region)"')"

# Trigger a build and wait for it to complete
BUILD_ID=$(aws codebuild start-build --region=$REGION --project-name=signotifier | jq -r '.build.id')
TIMEOUT=300
while [ "$BUILD_PHASE" != 'COMPLETED' ] || [ $TIMEOUT -le 0 ]; do
  sleep 5
  BUILD_PHASE=$(aws codebuild batch-get-builds --region=$REGION --ids=$BUILD_ID | jq -r '.builds[0].currentPhase')
  TIMEOUT=$((TIMEOUT-5))
done

"$BUILD_PHASE" != 'COMPLETED' && exit 1

# Safely produce a JSON object containing the result value.
# jq will ensure that the value is properly quoted
# and escaped to produce a valid JSON string.
jq -n --arg build_id "$BUILD_ID" '{"build_id":$build_id}'
