# Deployment Guide

This guide covers deploying FactForge backend in various environments.

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 50GB+ disk space

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: factforge
      POSTGRES_USER: factforge
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: factforge
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:latest
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - milvus_data:/var/lib/milvus
    ports:
      - "19530:19530"
    restart: unless-stopped

  api:
    build: ./api
    environment:
      DATABASE_URL: postgresql://factforge:${POSTGRES_PASSWORD}@postgres:5432/factforge
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_URL: amqp://factforge:${RABBITMQ_PASSWORD}@rabbitmq:5672/
      MILVUS_HOST: milvus
      MILVUS_PORT: 19530
      OLLAMA_URL: http://ollama:11434
      HMAC_KEY: ${HMAC_KEY}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - rabbitmq
      - milvus
    restart: unless-stopped

  worker:
    build: ./workers/enrichment_worker
    environment:
      DATABASE_URL: postgresql://factforge:${POSTGRES_PASSWORD}@postgres:5432/factforge
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_URL: amqp://factforge:${RABBITMQ_PASSWORD}@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    restart: unless-stopped

  crawler:
    build: ./crawler
    environment:
      RABBITMQ_URL: amqp://factforge:${RABBITMQ_PASSWORD}@rabbitmq:5672/
    volumes:
      - ./data:/app/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  milvus_data:
```

### Environment Variables

Create `.env.prod`:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here
RABBITMQ_PASSWORD=your_secure_password_here

# Security
HMAC_KEY=your_random_hex_key_32_chars_minimum
JWT_SECRET=your_random_jwt_secret_key_32_chars_minimum

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### Deploy

```bash
# Deploy production stack
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f api
```

## ☁️ Cloud Deployment

### AWS ECS

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name factforge
```

2. **Create Task Definition**
```json
{
  "family": "factforge-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/factforge-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/factforge"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/factforge",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Deploy Service**
```bash
aws ecs create-service \
  --cluster factforge \
  --service-name factforge-api \
  --task-definition factforge-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run

1. **Build and Push Image**
```bash
# Build image
docker build -t gcr.io/your-project/factforge-api ./api

# Push to registry
docker push gcr.io/your-project/factforge-api
```

2. **Deploy Service**
```bash
gcloud run deploy factforge-api \
  --image gcr.io/your-project/factforge-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

3. **Set Environment Variables**
```bash
gcloud run services update factforge-api \
  --set-env-vars DATABASE_URL=postgresql://user:pass@host:5432/factforge \
  --set-env-vars REDIS_URL=redis://host:6379/0
```

### Azure Container Instances

1. **Create Resource Group**
```bash
az group create --name factforge-rg --location eastus
```

2. **Deploy Container**
```bash
az container create \
  --resource-group factforge-rg \
  --name factforge-api \
  --image your-registry.azurecr.io/factforge-api:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=postgresql://user:pass@host:5432/factforge \
    REDIS_URL=redis://host:6379/0
```

## 🚀 Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Helm (optional)

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: factforge
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: factforge-config
  namespace: factforge
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/factforge"
  REDIS_URL: "redis://redis:6379/0"
  RABBITMQ_URL: "amqp://guest:guest@rabbitmq:5672/"
  MILVUS_HOST: "milvus"
  MILVUS_PORT: "19530"
  OLLAMA_URL: "http://ollama:11434"
```

### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: factforge-secrets
  namespace: factforge
type: Opaque
data:
  HMAC_KEY: <base64-encoded-key>
  JWT_SECRET: <base64-encoded-secret>
  POSTGRES_PASSWORD: <base64-encoded-password>
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: factforge-api
  namespace: factforge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: factforge-api
  template:
    metadata:
      labels:
        app: factforge-api
    spec:
      containers:
      - name: api
        image: factforge/api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: factforge-config
        - secretRef:
            name: factforge-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: factforge-api-service
  namespace: factforge
spec:
  selector:
    app: factforge-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: factforge-ingress
  namespace: factforge
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.factforge.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: factforge-api-service
            port:
              number: 80
```

## 🔧 Production Configuration

### Database
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database)
- Enable read replicas for scaling
- Configure automated backups
- Set up monitoring and alerting

### Redis
- Use managed Redis (AWS ElastiCache, Google Memorystore, Azure Cache)
- Configure clustering for high availability
- Set up monitoring and alerting

### Security
- Use secrets management (AWS Secrets Manager, Google Secret Manager, Azure Key Vault)
- Enable SSL/TLS for all connections
- Configure firewall rules
- Set up WAF (Web Application Firewall)
- Enable DDoS protection

### Monitoring
- Set up application monitoring (DataDog, New Relic, AppDynamics)
- Configure log aggregation (ELK Stack, Splunk, CloudWatch)
- Set up alerting for critical metrics
- Monitor resource usage and costs

### Backup and Recovery
- Automated database backups
- Point-in-time recovery
- Disaster recovery procedures
- Regular backup testing

## 📊 Performance Tuning

### API Optimization
- Enable gzip compression
- Configure caching headers
- Use connection pooling
- Optimize database queries
- Implement rate limiting

### Database Optimization
- Create appropriate indexes
- Configure connection pooling
- Optimize query performance
- Monitor slow queries
- Regular maintenance tasks

### Caching Strategy
- Redis for session storage
- CDN for static assets
- Application-level caching
- Database query caching

## 🚨 Troubleshooting

### Common Issues
1. **Database Connection Errors**
   - Check connection string
   - Verify network connectivity
   - Check firewall rules

2. **Redis Connection Errors**
   - Verify Redis is running
   - Check connection string
   - Monitor memory usage

3. **High Memory Usage**
   - Check for memory leaks
   - Optimize data structures
   - Increase memory limits

4. **Slow Response Times**
   - Check database performance
   - Monitor network latency
   - Optimize queries

### Debugging Commands
```bash
# Check container logs
docker logs factforge-api

# Check resource usage
docker stats

# Check database connections
docker exec -it postgres psql -U factforge -d factforge -c "SELECT * FROM pg_stat_activity;"

# Check Redis
docker exec -it redis redis-cli info

# Check RabbitMQ
docker exec -it rabbitmq rabbitmqctl list_queues
```

## 📈 Scaling

### Horizontal Scaling
- Add more API instances
- Use load balancer
- Scale workers independently
- Implement auto-scaling

### Vertical Scaling
- Increase CPU and memory
- Use faster storage
- Optimize application code
- Use faster network

### Database Scaling
- Read replicas
- Connection pooling
- Query optimization
- Partitioning

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t factforge-api:${{ github.sha }} ./api
    
    - name: Push to registry
      run: docker push your-registry/factforge-api:${{ github.sha }}
    
    - name: Deploy to production
      run: |
        kubectl set image deployment/factforge-api \
          api=your-registry/factforge-api:${{ github.sha }} \
          --namespace=factforge
```

## 📋 Maintenance

### Regular Tasks
- Update dependencies
- Security patches
- Performance monitoring
- Backup verification
- Log rotation
- Database maintenance

### Monitoring Checklist
- [ ] API response times
- [ ] Database performance
- [ ] Memory usage
- [ ] Disk space
- [ ] Error rates
- [ ] Security alerts

---

**Note**: This deployment guide covers common scenarios. Adjust configurations based on your specific requirements and infrastructure.
