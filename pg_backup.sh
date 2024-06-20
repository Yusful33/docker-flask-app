#!/bin/bash

# Set variables
BACKUP_FILE="postgres-$(date +%Y%m%d%H%M%S).sql"
S3_BUCKET="s3://yc-docker-test-bucket/flask-app-backups"

# Perform the backup
pg_dump -h <postgres-host> -U <your-user> -F c -b -v -f /tmp/$BACKUP_FILE <your-database>

# Upload to S3
aws s3 cp /tmp/$BACKUP_FILE $S3_BUCKET/$BACKUP_FILE

# Remove local backup file
rm /tmp/$BACKUP_FILE
