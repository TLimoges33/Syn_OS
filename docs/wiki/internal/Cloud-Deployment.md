# ☁️ Cloud Deployment Guide

**Platforms**: AWS, Azure, GCP  
**For**: Cloud Engineers

Deploy SynOS to major cloud platforms.

---

## AWS Deployment

### EC2 Instance

```bash
# Launch instance
aws ec2 run-instances \
  --image-id ami-synos-latest \
  --instance-type t3.xlarge \
  --key-name my-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=SynOS}]'

# Connect
ssh -i my-key.pem ubuntu@<public-ip>
```

### ECS (Fargate)

```json
{
  "family": "synos",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "synos",
      "image": "synos/synos:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

### EKS

```bash
# Create cluster
eksctl create cluster \
  --name synos-cluster \
  --region us-east-1 \
  --nodes 3 \
  --node-type t3.large

# Deploy
kubectl apply -f k8s/
```

---

## Azure Deployment

### Virtual Machine

```bash
az vm create \
  --resource-group synos-rg \
  --name synos-vm \
  --image synos-image \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys
```

### Container Instances

```bash
az container create \
  --resource-group synos-rg \
  --name synos-container \
  --image synos/synos:latest \
  --dns-name-label synos \
  --ports 80 443 \
  --cpu 2 \
  --memory 4
```

### AKS

```bash
az aks create \
  --resource-group synos-rg \
  --name synos-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

---

## GCP Deployment

### Compute Engine

```bash
gcloud compute instances create synos-instance \
  --image-family synos \
  --machine-type n1-standard-4 \
  --zone us-central1-a
```

### Cloud Run

```bash
gcloud run deploy synos \
  --image synos/synos:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### GKE

```bash
gcloud container clusters create synos-cluster \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --zone us-central1-a
```

---

## Terraform

```hcl
# AWS example
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "synos" {
  ami           = "ami-synos-latest"
  instance_type = "t3.xlarge"
  
  tags = {
    Name = "SynOS"
  }
}

resource "aws_eip" "synos" {
  instance = aws_instance.synos.id
}

output "public_ip" {
  value = aws_eip.synos.public_ip
}
```

---

## Cost Optimization

**AWS**:
- Use Reserved Instances (save 30-70%)
- Enable Auto Scaling
- Use S3 for backups (cheaper than EBS)

**Azure**:
- Use Reserved VM Instances
- Enable autoscaling
- Use Blob Storage for archives

**GCP**:
- Use Committed Use Discounts
- Enable autoscaling
- Use Cloud Storage for backups

---

**Last Updated**: October 4, 2025
