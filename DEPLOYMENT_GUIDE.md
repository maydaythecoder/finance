# Fake Trading Price Simulator - Deployment Guide

## Overview

This guide covers deploying the Fake Trading Price Simulator in various environments, from local development to production systems. The simulator is designed to be lightweight and secure, requiring minimal dependencies.

## Prerequisites

### System Requirements

- **Python**: 3.7 or higher
- **Memory**: Minimum 10MB RAM
- **Storage**: Minimum 1MB disk space
- **OS**: Cross-platform (Windows, macOS, Linux)

### Dependencies

The simulator uses only Python standard library modules:

- `json`, `time`, `random`, `logging`
- `datetime`, `pathlib`, `sys`, `typing`

No external dependencies are required.

## Local Development Deployment

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd finance

# Verify Python version
python --version  # Should be 3.7+

# Run setup validation
python setup.py
```

### 2. Configuration

```bash
# Create configuration file (optional)
python config.py

# Or set environment variables
export FAKE_TRADING_VOLATILITY=0.5
export FAKE_TRADING_DURATION=60
export FAKE_TRADING_DATA_FILE=data.json
```

### 3. Validation

```bash
# Run comprehensive validation
make validate

# Or run individual checks
python setup.py
make test
make lint
```

### 4. Execution

```bash
# Basic execution
python faketrading.py

# With make
make run

# With custom parameters
python faketrading.py
```

## Docker Deployment

### 1. Dockerfile

Create a `Dockerfile`:

```dockerfile
# Use official Python runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY faketrading.py .
COPY data.json .
COPY config.py .
COPY setup.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FAKE_TRADING_VOLATILITY=0.5

# Run setup
RUN python setup.py

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (if needed for web interface)
EXPOSE 8000

# Default command
CMD ["python", "faketrading.py"]
```

### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  fake-trading:
    build: .
    container_name: fake-trading-simulator
    environment:
      - FAKE_TRADING_VOLATILITY=0.5
      - FAKE_TRADING_DURATION=60
      - FAKE_TRADING_DATA_FILE=data.json
    volumes:
      - ./data.json:/app/data.json:ro
      - ./output:/app/output
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

### 3. Build and Run

```bash
# Build image
docker build -t fake-trading-simulator .

# Run container
docker run -v $(pwd)/data.json:/app/data.json:ro fake-trading-simulator

# Or use docker-compose
docker-compose up --build
```

## Kubernetes Deployment

### 1. ConfigMap

Create `configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fake-trading-config
data:
  data.json: |
    {
      "open": 154.12,
      "high": 154.89,
      "low": 153.95,
      "close": 154.71
    }
  config.json: |
    {
      "simulation": {
        "volatility": 0.5,
        "duration_seconds": 60
      }
    }
```

### 2. Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fake-trading-simulator
  labels:
    app: fake-trading-simulator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fake-trading-simulator
  template:
    metadata:
      labels:
        app: fake-trading-simulator
    spec:
      containers:
      - name: simulator
        image: fake-trading-simulator:latest
        imagePullPolicy: IfNotPresent
        env:
        - name: FAKE_TRADING_VOLATILITY
          value: "0.5"
        - name: FAKE_TRADING_DURATION
          value: "60"
        volumeMounts:
        - name: config-volume
          mountPath: /app/data.json
          subPath: data.json
        - name: output-volume
          mountPath: /app/output
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        resources:
          requests:
            memory: "10Mi"
            cpu: "10m"
          limits:
            memory: "50Mi"
            cpu: "100m"
      volumes:
      - name: config-volume
        configMap:
          name: fake-trading-config
      - name: output-volume
        emptyDir: {}
```

### 3. Service

Create `service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fake-trading-service
spec:
  selector:
    app: fake-trading-simulator
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 4. Deploy

```bash
# Apply configurations
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods
kubectl logs -f deployment/fake-trading-simulator
```

## Cloud Deployment

### AWS Deployment

#### 1. ECS Task Definition

```json
{
  "family": "fake-trading-simulator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "simulator",
      "image": "fake-trading-simulator:latest",
      "environment": [
        {
          "name": "FAKE_TRADING_VOLATILITY",
          "value": "0.5"
        },
        {
          "name": "FAKE_TRADING_DURATION",
          "value": "60"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fake-trading-simulator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 2. Lambda Function

```python
import json
import os
from faketrading import PriceSimulator

def lambda_handler(event, context):
    """AWS Lambda handler for fake trading simulator."""
    
    # Get configuration from environment
    volatility = float(os.environ.get('FAKE_TRADING_VOLATILITY', '0.5'))
    data_file = os.environ.get('FAKE_TRADING_DATA_FILE', 'data.json')
    
    try:
        # Create simulator
        simulator = PriceSimulator(volatility=volatility, data_file=data_file)
        
        # Run simulation
        results = simulator.run_simulation()
        
        # Export results
        simulator.export_results()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Simulation completed successfully',
                'records': len(results),
                'final_price': simulator.current_price
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

### Google Cloud Deployment

#### 1. Cloud Run Service

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: fake-trading-simulator
spec:
  template:
    spec:
      containers:
      - image: gcr.io/project/fake-trading-simulator
        env:
        - name: FAKE_TRADING_VOLATILITY
          value: "0.5"
        - name: FAKE_TRADING_DURATION
          value: "60"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
```

#### 2. Deploy to Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/project/fake-trading-simulator

# Deploy to Cloud Run
gcloud run deploy fake-trading-simulator \
  --image gcr.io/project/fake-trading-simulator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Security Considerations

### 1. File Permissions

```bash
# Set secure permissions
chmod 644 data.json
chmod 755 faketrading.py
chmod 600 config.json  # If contains sensitive data
```

### 2. Network Security

```bash
# Firewall rules (if applicable)
# Allow only necessary ports
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
iptables -A INPUT -j DROP
```

### 3. Container Security

```dockerfile
# Use non-root user
USER appuser

# Read-only filesystem
RUN chmod 755 /app && chown -R appuser:appuser /app

# Security scanning
RUN pip install safety && safety check
```

### 4. Secrets Management

```bash
# Use environment variables for secrets
export FAKE_TRADING_API_KEY=$(aws secretsmanager get-secret-value --secret-id api-key --query SecretString --output text)

# Or use Kubernetes secrets
kubectl create secret generic fake-trading-secrets \
  --from-literal=api-key=your-api-key
```

## Monitoring and Logging

### 1. Application Logging

```python
# Configure structured logging
import logging
from config import get_simulation_config

config = get_simulation_config()
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format,
    datefmt=config.log_date_format
)
```

### 2. Health Checks

```python
# health_check.py
import os
import json
from pathlib import Path

def health_check():
    """Health check endpoint."""
    try:
        # Check if data file exists
        data_file = Path("data.json")
        if not data_file.exists():
            return False, "Data file not found"
        
        # Validate data file
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        required_keys = {"open", "high", "low", "close"}
        if not required_keys.issubset(data.keys()):
            return False, "Invalid data file"
        
        return True, "Healthy"
        
    except Exception as e:
        return False, str(e)
```

### 3. Metrics Collection

```python
# metrics.py
import time
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.price_count = 0
        self.errors = 0
    
    def start_simulation(self):
        self.start_time = datetime.now()
    
    def end_simulation(self):
        self.end_time = datetime.now()
    
    def record_price(self):
        self.price_count += 1
    
    def record_error(self):
        self.errors += 1
    
    def get_metrics(self):
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        return {
            "duration_seconds": duration,
            "price_count": self.price_count,
            "errors": self.errors,
            "prices_per_second": self.price_count / duration if duration > 0 else 0
        }
```

## Performance Optimization

### 1. Resource Limits

```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "10Mi"
    cpu: "10m"
  limits:
    memory: "50Mi"
    cpu: "100m"
```

### 2. Caching

```python
# Implement caching for repeated simulations
import functools

@functools.lru_cache(maxsize=128)
def cached_price_generation(second, volatility, market_data_hash):
    """Cache price generation for repeated parameters."""
    # Implementation here
    pass
```

### 3. Batch Processing

```python
# Process multiple simulations in batch
def batch_simulate(configs):
    """Run multiple simulations in parallel."""
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_single_simulation, config) for config in configs]
        results = [future.result() for future in futures]
    
    return results
```

## Troubleshooting

### Common Issues

#### 1. File Not Found

```bash
# Check file existence
ls -la data.json

# Verify file permissions
chmod 644 data.json

# Check working directory
pwd
```

#### 2. Permission Denied

```bash
# Fix file permissions
chmod 755 faketrading.py
chmod 644 data.json

# Check user permissions
whoami
ls -la
```

#### 3. Memory Issues

```bash
# Monitor memory usage
ps aux | grep python
free -h

# Reduce memory usage
export FAKE_TRADING_MAX_PRICE_HISTORY=100
```

#### 4. Timing Issues

```bash
# Check system clock
date

# Adjust timing precision
export FAKE_TRADING_SLEEP_PRECISION_MS=10
```

### Debug Mode

```bash
# Enable debug logging
export FAKE_TRADING_LOG_LEVEL=DEBUG

# Run with verbose output
python faketrading.py --verbose

# Check configuration
python config.py
```

## Backup and Recovery

### 1. Data Backup

```bash
# Backup data files
cp data.json data.json.backup
cp simulation_results.json simulation_results.json.backup

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data.json "backup/data_${DATE}.json"
cp simulation_results.json "backup/results_${DATE}.json"
```

### 2. Configuration Backup

```bash
# Backup configuration
cp config.json config.json.backup

# Version control
git add config.json
git commit -m "Backup configuration"
```

### 3. Recovery Procedures

```bash
# Restore from backup
cp data.json.backup data.json

# Validate restored data
python setup.py

# Test recovery
python faketrading.py
```

---

*This deployment guide is part of the Fake Trading Price Simulator project.*
