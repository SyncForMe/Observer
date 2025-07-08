# Deployment Guide

This guide covers various deployment options for the AI Agent Simulation Platform.

## Table of Contents

- [Quick Deployment](#quick-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)

---

## Quick Deployment

### Using Docker Compose (Recommended)

The easiest way to deploy the entire stack:

```bash
# Clone the repository
git clone https://github.com/your-username/ai-agent-simulation.git
cd ai-agent-simulation

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Configure environment variables
nano backend/.env  # Edit with your settings
nano frontend/.env  # Edit with your settings

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Setup

If you prefer to run services individually:

```bash
# 1. Start MongoDB
docker run -d --name mongo -p 27017:27017 mongo:latest

# 2. Start Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001

# 3. Start Frontend
cd frontend
yarn install
yarn build
yarn start
```

---

## Production Deployment

### Infrastructure Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100Mbps

**Recommended Production:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps
- Load Balancer
- SSL Certificate

### Production Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    environment:
      - NODE_ENV=production
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    environment:
      - ENVIRONMENT=production
      - MONGO_URL=mongodb://mongodb:27017/ai_agent_simulation
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secure_password
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
```

Deploy with:
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

## Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile.prod`:

```dockerfile
# Build stage
FROM node:16-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Build and Run

```bash
# Build images
docker build -t ai-agent-backend:latest ./backend
docker build -t ai-agent-frontend:latest ./frontend

# Run containers
docker run -d --name backend -p 8001:8001 ai-agent-backend:latest
docker run -d --name frontend -p 80:80 ai-agent-frontend:latest
```

---

## Kubernetes Deployment

### Namespace

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-agent-simulation
```

### MongoDB Deployment

Create `k8s/mongodb.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: ai-agent-simulation
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
      volumes:
      - name: mongodb-storage
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
  namespace: ai-agent-simulation
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
```

### Backend Deployment

Create `k8s/backend.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ai-agent-simulation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ai-agent-backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          value: "mongodb://mongodb-service:27017/ai_agent_simulation"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: ai-agent-simulation
spec:
  selector:
    app: backend
  ports:
  - port: 8001
    targetPort: 8001
```

### Frontend Deployment

Create `k8s/frontend.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ai-agent-simulation
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ai-agent-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: ai-agent-simulation
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
```

### Ingress Configuration

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-agent-ingress
  namespace: ai-agent-simulation
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: tls-secret
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8001
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n ai-agent-simulation

# Check services
kubectl get services -n ai-agent-simulation

# View logs
kubectl logs -f deployment/backend -n ai-agent-simulation
```

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Database
MONGO_URL=mongodb://localhost:27017/ai_agent_simulation

# Authentication
JWT_SECRET=your-super-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=7200

# AI Services
FAL_KEY=your-fal-ai-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
# API Configuration
REACT_APP_BACKEND_URL=https://your-domain.com

# Application
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.4.0

# Analytics (optional)
REACT_APP_GOOGLE_ANALYTICS=G-XXXXXXXXXX
REACT_APP_SENTRY_DSN=https://your-sentry-dsn
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=1r/s;

    # Upstream servers
    upstream backend {
        server backend:8001;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API routes
        location /api {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            limit_req zone=general burst=5 nodelay;
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
        }
    }
}
```

---

## Monitoring and Logging

### Health Check Endpoints

Add health checks to your backend:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.4.0"
    }

@app.get("/health/db")
async def db_health_check():
    try:
        # Check MongoDB connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Logging Configuration

Create `backend/logging.conf`:

```ini
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_app]
level=INFO
handlers=consoleHandler,fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/app.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Monitoring with Prometheus

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

---

## Security Considerations

### SSL/TLS Configuration

1. **Get SSL Certificate:**
   ```bash
   # Using Let's Encrypt
   certbot certonly --webroot -w /var/www/html -d your-domain.com
   ```

2. **Configure Nginx SSL:**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
       ssl_prefer_server_ciphers on;
   }
   ```

### Database Security

1. **MongoDB Authentication:**
   ```bash
   # Connect to MongoDB
   mongo admin
   
   # Create admin user
   db.createUser({
     user: "admin",
     pwd: "secure_password",
     roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase"]
   })
   ```

2. **Database Backup:**
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   mongodump --out /backup/mongodb_$DATE
   
   # Cleanup old backups (keep last 7 days)
   find /backup -name "mongodb_*" -mtime +7 -delete
   ```

### Firewall Configuration

```bash
# UFW configuration
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Environment Security

1. **Use secrets management:**
   ```bash
   # Using Docker secrets
   echo "super_secret_jwt_key" | docker secret create jwt_secret -
   ```

2. **Regular security updates:**
   ```bash
   # Update system packages
   apt update && apt upgrade -y
   
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

---

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using port 8001
   netstat -tlnp | grep 8001
   
   # Kill process using port
   sudo kill -9 $(sudo lsof -t -i:8001)
   ```

2. **Database connection issues:**
   ```bash
   # Check MongoDB status
   systemctl status mongod
   
   # Check logs
   tail -f /var/log/mongodb/mongod.log
   ```

3. **Memory issues:**
   ```bash
   # Check memory usage
   free -h
   
   # Check container memory
   docker stats
   ```

### Logs and Debugging

```bash
# Check application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check system logs
journalctl -u docker -f

# Database logs
docker exec -it mongodb tail -f /var/log/mongodb/mongod.log
```

---

## Performance Optimization

### Database Optimization

1. **Create indexes:**
   ```javascript
   // Connect to MongoDB
   use ai_agent_simulation;
   
   // Create indexes
   db.agents.createIndex({ "user_id": 1 });
   db.saved_agents.createIndex({ "user_id": 1, "is_favorite": 1 });
   db.conversations.createIndex({ "user_id": 1, "timestamp": -1 });
   ```

2. **Connection pooling:**
   ```python
   # In your FastAPI app
   from motor.motor_asyncio import AsyncIOMotorClient
   
   client = AsyncIOMotorClient(
       MONGO_URL,
       maxPoolSize=10,
       minPoolSize=5,
       maxIdleTimeMS=30000,
       serverSelectionTimeoutMS=5000
   )
   ```

### Caching

1. **Redis caching:**
   ```python
   import redis
   
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   
   @lru_cache(maxsize=100)
   def get_agent_data(agent_id: str):
       # Cache agent data
       pass
   ```

2. **Frontend caching:**
   ```javascript
   // Service worker caching
   const CACHE_NAME = 'ai-agent-v1';
   const urlsToCache = [
     '/',
     '/static/js/bundle.js',
     '/static/css/main.css'
   ];
   ```

---

For more deployment help, check the [GitHub Issues](https://github.com/your-username/ai-agent-simulation/issues) or contact support@ai-agent-simulation.com.