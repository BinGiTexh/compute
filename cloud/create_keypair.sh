#!/bin/bash
aws ec2 create-key-pair --key-name $$keyname --query 'KeyMaterial' --output text > $$name.pem
