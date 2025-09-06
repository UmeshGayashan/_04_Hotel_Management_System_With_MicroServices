#!/bin/bash

echo "=== Cleaning up Hotel Management System Kubernetes Resources ==="
echo ""

# Function to delete all resources
cleanup_all() {
    echo "Deleting all Kubernetes resources..."
    
    # Delete frontend and gateway
    kubectl delete -f k8s/frontend/frontend.yml --ignore-not-found=true
    kubectl delete -f k8s/gateway/gateway.yml --ignore-not-found=true
    kubectl delete -f k8s/php-myAdmin/php-myadmin.yml --ignore-not-found=true
    
    # Delete backend services
    kubectl delete -f k8s/backend/auth-service.yaml --ignore-not-found=true
    kubectl delete -f k8s/backend/hotel-service.yaml --ignore-not-found=true
    kubectl delete -f k8s/backend/booking-service.yaml --ignore-not-found=true
    kubectl delete -f k8s/backend/payment-service.yaml --ignore-not-found=true
    kubectl delete -f k8s/backend/notification-service.yaml --ignore-not-found=true
    
    # Delete Kafka
    kubectl delete -f k8s/kafka/kafka.yaml --ignore-not-found=true
    
    # Delete MySQL databases
    kubectl delete -f k8s/mysql/auth-mysql.yaml --ignore-not-found=true
    kubectl delete -f k8s/mysql/hotel-mysql.yaml --ignore-not-found=true
    kubectl delete -f k8s/mysql/booking-mysql.yaml --ignore-not-found=true
    kubectl delete -f k8s/mysql/payment-mysql.yaml --ignore-not-found=true
    kubectl delete -f k8s/mysql/notification-mysql.yaml --ignore-not-found=true
    
    echo ""
    echo "Waiting for all resources to be deleted..."
    sleep 10
    
    echo ""
    echo "=== Remaining Resources ==="
    kubectl get all
    
    echo ""
    echo "✓ Cleanup completed!"
}

# Main cleanup flow
main() {
    cd "$(dirname "$0")/.."
    cleanup_all
}

# Run main function
main "$@"
