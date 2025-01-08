aws ec2 run-instances \
    --image-id ami-0cdc56cf41c025c96 --count 1 \
    --instance-type g6e.xlarge \
    --key-name malik \
    --user-data file://my_script.txt \
    --iam-instance-profile Arn="arn:aws:iam::684891021291:instance-profile/ecsInstanceRole" \
    --block-device-mappings file://mapping.json \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ML-inference},{Key=Bucket,Value=vip-bucket-sandbox-test}]' \
    --metadata-options "InstanceMetadataTags=enabled" 
