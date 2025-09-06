# Kubernetes Deployment for Hotel Management System

This guide provides instructions to deploy the Hotel Management System using Kubernetes with Minikube.

## Prerequisites

1. **Minikube installed**: Follow [Minikube installation guide](https://minikube.sigs.k8s.io/docs/start/)
2. **kubectl installed**: Follow [kubectl installation guide](https://kubernetes.io/docs/tasks/tools/)
3. **Docker installed**: Required for building images

## Quick Start

### 1. Start Minikube
```bash
minikube start
```
```bash
minikube delete && minikube start --driver=docker
```

### 2. Deploy the Application
```bash
# Navigate to the project directory
cd /path/to/Hotel_Management_System_With_MicroServices

# Run the deployment script
./k8s/deploy.sh
```

The script will:
- Start Minikube (if not running)
- Build all Docker images
- Deploy MySQL databases
- Deploy backend services
- Deploy gateway and frontend
- Show access URLs

### 3. Access the Application

After deployment, you can access:

- **Frontend Application**: `http://<minikube-ip>:30001`
- **API Gateway**: `http://<minikube-ip>:30080`
- **phpMyAdmin**: `http://<minikube-ip>:30090`

To get the Minikube IP:
```bash
minikube ip
```

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Build Docker Images
```bash
# Point to Minikube's Docker daemon
eval $(minikube docker-env)

# Build all images
docker build -t auth-service:latest ./auth-service/
docker build -t hotel-service:latest ./hotel-service/
docker build -t booking-service:latest ./booking-service/
docker build -t payment-service:latest ./payment-service/
docker build -t frontend:latest ./frontend/
```

### 2. Deploy MySQL Databases
```bash
kubectl apply -f k8s/mysql/auth-mysql.yaml
kubectl apply -f k8s/mysql/hotel-mysql.yaml
kubectl apply -f k8s/mysql/booking-mysql.yaml
kubectl apply -f k8s/mysql/payment-mysql.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=auth-mysql --timeout=300s
kubectl wait --for=condition=ready pod -l app=hotel-mysql --timeout=300s
kubectl wait --for=condition=ready pod -l app=booking-mysql --timeout=300s
kubectl wait --for=condition=ready pod -l app=payment-mysql --timeout=300s
```

### 3. Deploy Backend Services
```bash
kubectl apply -f k8s/backend/auth-service.yaml
kubectl apply -f k8s/backend/hotel-service.yaml
kubectl apply -f k8s/backend/booking-service.yaml
kubectl apply -f k8s/backend/payment-service.yaml

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=auth-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=hotel-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=booking-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=payment-service --timeout=300s
```

### 4. Deploy Gateway and Frontend
```bash
kubectl apply -f k8s/gateway/gateway.yml
kubectl apply -f k8s/frontend/frontend.yml
kubectl apply -f k8s/php-myAdmin/php-myadmin.yml

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=gateway --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=phpmyadmin --timeout=300s
```

## Service Ports

- **Auth Service**: 8001
- **Hotel Service**: 8002
- **Booking Service**: 8003
- **Payment Service**: 8004
- **Notification Service**: 8005
- **Gateway**: 80 (exposed on 30080)
- **Frontend**: 3000 (exposed on 30001)
- **phpMyAdmin**: 80 (exposed on 30090)
- **Kafka**: 9092
- **Zookeeper**: 2181

## Monitoring and Troubleshooting

### Check Pod Status
```bash
kubectl get pods -o wide
```

### Check Services
```bash
kubectl get services
```

### View Pod Logs
```bash
kubectl logs <pod-name>
```

### Describe Pod (for troubleshooting)
```bash
kubectl describe pod <pod-name>
```

### Access Kubernetes Dashboard
```bash
minikube dashboard
```

### Port Forwarding (alternative access method)
```bash
# Forward gateway port
kubectl port-forward service/gateway 8080:80

# Forward frontend port
kubectl port-forward service/frontend 3001:3000
```

## Database Access

### Connect to MySQL via phpMyAdmin
1. Open `http://<minikube-ip>:30090`
2. Select the appropriate server (auth-mysql, hotel-mysql, etc.)
3. Use credentials:
   - **Username**: auth_user, hotel_user, booking_user, or payment_user
   - **Password**: authpass, hotelpass, bookingpass, or paymentpass

### Direct MySQL Connection
```bash
# Port forward MySQL service
kubectl port-forward service/auth-mysql 3307:3306

# Connect using MySQL client
mysql -h localhost -P 3307 -u auth_user -pauthpass auth_db
```

## Cleanup

To remove all resources:
```bash
./k8s/cleanup.sh
```

Or manually:
```bash
kubectl delete -f k8s/frontend/
kubectl delete -f k8s/gateway/
kubectl delete -f k8s/php-myAdmin/
kubectl delete -f k8s/backend/
kubectl delete -f k8s/mysql/
```

## Troubleshooting Common Issues

### 1. ImagePullBackOff Error
- Ensure images are built in Minikube's Docker environment
- Run: `eval $(minikube docker-env)` before building images

### 2. Service Not Accessible
- Check if Minikube is running: `minikube status`
- Get Minikube IP: `minikube ip`
- Verify service ports: `kubectl get services`

### 3. Pod CrashLoopBackOff / Error Status
**Common Issue: ModuleNotFoundError: No module named 'MySQLdb'**

This error occurs when the DATABASE_URL uses the wrong MySQL driver format. The fix is to use `mysql+pymysql://` instead of `mysql://` in the DATABASE_URL.

**Solution:**
```bash
# Check pod logs to confirm the issue
kubectl logs <pod-name>

# The DATABASE_URL should use pymysql driver:
# mysql+pymysql://user:password@host:port/database
```

**Other CrashLoopBackOff troubleshooting:**
- Check pod logs: `kubectl logs <pod-name>`
- Verify environment variables and database connections
- Ensure databases are running: `kubectl get pods -l app=*-mysql`

### 4. Database Connection Issues
- Verify MySQL pods are running: `kubectl get pods | grep mysql`
- Check database credentials in secrets: `kubectl get secrets`
- Test database connectivity via phpMyAdmin

**Missing Tables Error (Table 'auth_db.users' doesn't exist):**

If you get errors about missing tables, you can manually create them:

```bash
# Create users table in auth database
kubectl exec -it deployment/auth-mysql -- mysql -u auth_user -pauthpass auth_db -e "
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  role ENUM('customer','staff') NOT NULL DEFAULT 'customer',
  full_name VARCHAR(255) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

# Create services table in hotel database
kubectl exec -it deployment/hotel-mysql -- mysql -u hotel_user -photelpass hotel_db -e "
CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  service VARCHAR(255) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_service_name (service)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

# Create bookings table
kubectl exec -it deployment/booking-mysql -- mysql -u booking_user -pbookingpass booking_db -e "
CREATE TABLE IF NOT EXISTS bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  service_id INT NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  scheduled_for DATETIME NULL,
  status ENUM('pending','confirmed','canceled') NOT NULL DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_user_id (user_id),
  INDEX ix_service_id (service_id),
  INDEX ix_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"

# Create payments table
kubectl exec -it deployment/payment-mysql -- mysql -u payment_user -ppaymentpass payment_db -e "
CREATE TABLE IF NOT EXISTS payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT NOT NULL,
  user_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  method VARCHAR(32) NOT NULL DEFAULT 'card',
  status ENUM('pending','succeeded','failed','refunded') NOT NULL DEFAULT 'succeeded',
  provider VARCHAR(32) NULL,
  provider_payment_id VARCHAR(128) NULL,
  idempotency_key VARCHAR(64) NOT NULL,
  error_code VARCHAR(64) NULL,
  error_message VARCHAR(255) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY ux_idempotency_key (idempotency_key),
  KEY ix_booking_id (booking_id),
  KEY ix_user_id (user_id),
  KEY ix_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
```

### 5. Persistent Volume Issues
- Check PVC status: `kubectl get pvc`
- Ensure sufficient storage: `kubectl describe pvc <pvc-name>`

## Environment Variables

The following environment variables are configured:

### Auth Service
- `DATABASE_URL`: mysql://auth_user:authpass@auth-mysql:3306/auth_db
- `JWT_SECRET_KEY`: your_secret
- `JWT_ALGORITHM`: HS256

### Hotel Service
- `DATABASE_URL`: mysql://hotel_user:hotelpass@hotel-mysql:3306/hotel_db

### Booking Service
- `DATABASE_URL`: mysql://booking_user:bookingpass@booking-mysql:3306/booking_db
- `HOTEL_SERVICE_BASE_URL`: http://hotel-service:8002

### Payment Service
- `DATABASE_URL`: mysql://payment_user:paymentpass@payment-mysql:3306/payment_db
- `BOOKING_SERVICE_URL`: http://booking-service:8003

## Architecture

```
Frontend (30001) → Gateway (30080) → Backend Services
                                   ├── Auth Service (8001)
                                   ├── Hotel Service (8002)
                                   ├── Booking Service (8003)
                                   ├── Payment Service (8004)
                                   └── Notification Service (8005) ← Kafka Events
                                           │                              ↑
                                           ├── auth-mysql                 │
                                           ├── hotel-mysql                │
                                           ├── booking-mysql              │
                                           ├── payment-mysql              │
                                           ├── notification-mysql         │
                                           └─── Kafka + Zookeeper ────────┘
                                                (Event Streaming)
```

## Kafka Integration

The system now includes a notification service that uses Apache Kafka for event-driven communication:

### Event Types
- **User Events**: User registration, profile updates
- **Booking Events**: Booking creation, updates, cancellations
- **Service Events**: New hotel services, service updates
- **Payment Events**: Payment processing, refunds

### Real-time Notifications
- WebSocket connections for instant notifications
- Browser push notifications (when permission granted)
- Event-driven architecture for decoupled communication

### Notification Service Features
- REST API for notification management (`/api/v1/notifications`)
- WebSocket endpoint for real-time updates (`/ws/{user_id}`)
- Kafka consumer for processing events from other services
- MySQL database for notification persistence
