#!/bin/bash

echo "=== Hotel Management System Kubernetes Deployment ==="
echo ""

# Function to check if minikube is running
check_minikube() {
    if ! minikube status | grep -q "Running"; then
        echo "Starting Minikube..."
        minikube start
    else
        echo "✓ Minikube is already running"
    fi
}

# Function to build Docker images in Minikube
build_images() {
    echo ""
    echo "Building Docker images in Minikube..."
    
    # Point shell to Minikube's Docker daemon
    eval $(minikube docker-env)
    
    # Build auth-service
    echo "Building auth-service..."
    docker build -t auth-service:latest ./auth-service/
    
    # Build hotel-service
    echo "Building hotel-service..."
    docker build -t hotel-service:latest ./hotel-service/
    
    # Build booking-service
    echo "Building booking-service..."
    docker build -t booking-service:latest ./booking-service/
    
    # Build payment-service
    echo "Building payment-service..."
    docker build -t payment-service:latest ./payment-service/
    
    # Build notification-service
    echo "Building notification-service..."
    docker build -t notification-service:latest ./notification-service/
    
    # Build frontend
    echo "Building frontend..."
    docker build -t frontend:latest ./frontend/
    
    # Build gateway
    echo "Building gateway..."
    docker build -t gateway:latest ./gateway/
    
    echo "✓ All images built successfully"
}

# Function to deploy MySQL databases
deploy_mysql() {
    echo ""
    echo "Deploying MySQL databases..."
    
    kubectl apply -f k8s/mysql/auth-mysql.yaml
    kubectl apply -f k8s/mysql/hotel-mysql.yaml
    kubectl apply -f k8s/mysql/booking-mysql.yaml
    kubectl apply -f k8s/mysql/payment-mysql.yaml
    kubectl apply -f k8s/mysql/notification-mysql.yaml
    
    echo "Waiting for MySQL databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=auth-mysql --timeout=300s
    kubectl wait --for=condition=ready pod -l app=hotel-mysql --timeout=300s
    kubectl wait --for=condition=ready pod -l app=booking-mysql --timeout=300s
    kubectl wait --for=condition=ready pod -l app=payment-mysql --timeout=300s
    kubectl wait --for=condition=ready pod -l app=notification-mysql --timeout=300s
    
    echo "✓ MySQL databases are ready"
}

# Function to deploy Kafka
deploy_kafka() {
    echo ""
    echo "Deploying Kafka and Zookeeper..."
    
    kubectl apply -f k8s/kafka/kafka.yaml
    
    echo "Waiting for Kafka to be ready..."
    kubectl wait --for=condition=ready pod -l app=zookeeper --timeout=300s
    kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
    
    echo "✓ Kafka is ready"
}

# Function to deploy backend services
deploy_backend() {
    echo ""
    echo "Deploying backend services..."
    
    kubectl apply -f k8s/backend/auth-service.yaml
    kubectl apply -f k8s/backend/hotel-service.yaml
    kubectl apply -f k8s/backend/booking-service.yaml
    kubectl apply -f k8s/backend/payment-service.yaml
    kubectl apply -f k8s/backend/notification-service.yaml
    
    echo "Waiting for backend services to be ready..."
    kubectl wait --for=condition=ready pod -l app=auth-service --timeout=300s
    kubectl wait --for=condition=ready pod -l app=hotel-service --timeout=300s
    kubectl wait --for=condition=ready pod -l app=booking-service --timeout=300s
    kubectl wait --for=condition=ready pod -l app=payment-service --timeout=300s
    kubectl wait --for=condition=ready pod -l app=notification-service --timeout=300s
    
    echo "✓ Backend services are ready"
}

# Function to deploy frontend and update API base URL
deploy_frontend() {
    echo ""
    echo "Deploying gateway and frontend..."
    
    # Deploy gateway first
    kubectl apply -f k8s/gateway/gateway.yml
    
    # Get Minikube IP dynamically
    MINIKUBE_IP=$(minikube ip)
    echo "Using Minikube IP: $MINIKUBE_IP"
    
    # Update frontend configuration with current Minikube IP
    sed "s|value: http://.*:30080|value: http://$MINIKUBE_IP:30080|g" k8s/frontend/frontend.yml > /tmp/frontend-updated.yml
    kubectl apply -f /tmp/frontend-updated.yml
    
    kubectl apply -f k8s/php-myAdmin/php-myadmin.yml
    
    echo "Waiting for frontend services to be ready..."
    kubectl wait --for=condition=ready pod -l app=gateway --timeout=300s
    kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
    kubectl wait --for=condition=ready pod -l app=phpmyadmin --timeout=300s
    
    echo "✓ Frontend services are ready"
}

# Function to display access URLs
show_urls() {
    echo ""
    echo "=== Application URLs ==="
    echo ""
    
    MINIKUBE_IP=$(minikube ip)
    
    echo "🌐 Frontend Application:"
    echo "   http://${MINIKUBE_IP}:30001"
    echo ""
    
    echo "🚪 API Gateway:"
    echo "   http://${MINIKUBE_IP}:30080"
    echo ""
    
    echo "🗄️  phpMyAdmin:"
    echo "   http://${MINIKUBE_IP}:30090"
    echo ""
    
    echo "📊 Kubernetes Dashboard (optional):"
    echo "   minikube dashboard"
    echo ""
}

# Function to show pod status
show_status() {
    echo ""
    echo "=== Pod Status ==="
    kubectl get pods -o wide
    echo ""
    echo "=== Services ==="
    kubectl get services
}

# Main deployment flow
main() {
    cd "$(dirname "$0")/.."
    
    check_minikube
    build_images
    deploy_mysql
    deploy_kafka
    deploy_backend
    deploy_frontend
    show_status
    show_urls
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "💡 Run 'kubectl get pods' to check pod status"
    echo "💡 Run 'kubectl logs <pod-name>' to view logs"
    echo "💡 Run './k8s/cleanup.sh' to remove all resources"
}

# Run main function
main "$@"
