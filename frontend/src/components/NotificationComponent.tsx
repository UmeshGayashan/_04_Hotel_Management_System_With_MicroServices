import React, { useState, useEffect, useCallback } from 'react';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: string;
  read: boolean;
  created_at: string;
}

interface NotificationComponentProps {
  userId: number;
  apiBaseUrl: string;
}

const NotificationComponent: React.FC<NotificationComponentProps> = ({ userId, apiBaseUrl }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  // Fetch notifications from API
  const fetchNotifications = useCallback(async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/notifications?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, [apiBaseUrl, userId]);

  // Fetch unread count
  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/notifications/${userId}/unread-count`);
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, [apiBaseUrl, userId]);

  // Mark notification as read
  const markAsRead = async (notificationId: number) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/notifications/${notificationId}?user_id=${userId}`, {
        method: 'PUT',
      });
      if (response.ok) {
        setNotifications(prev =>
          prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Setup WebSocket connection
  useEffect(() => {
    const wsUrl = `ws://${window.location.hostname}:30080/ws/${userId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWebsocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'notification') {
          const newNotification = message.data;
          setNotifications(prev => [newNotification, ...prev]);
          setUnreadCount(prev => prev + 1);
          
          // Show browser notification if permission granted
          if (Notification.permission === 'granted') {
            new Notification(newNotification.title, {
              body: newNotification.message,
              icon: '/notification-icon.png'
            });
          }
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWebsocket(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [userId]);

  // Initial data fetch
  useEffect(() => {
    fetchNotifications();
    fetchUnreadCount();
  }, [fetchNotifications, fetchUnreadCount]);

  // Request notification permission
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'user': return '👤';
      case 'booking': return '📅';
      case 'service': return '🏨';
      case 'payment': return '💳';
      default: return '📢';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="notification-component">
      {/* Notification Bell */}
      <button
        className="notification-bell"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          background: 'none',
          border: 'none',
          fontSize: '24px',
          cursor: 'pointer',
          padding: '8px'
        }}
      >
        🔔
        {unreadCount > 0 && (
          <span
            className="notification-badge"
            style={{
              position: 'absolute',
              top: '0',
              right: '0',
              background: '#ff4444',
              color: 'white',
              borderRadius: '50%',
              padding: '2px 6px',
              fontSize: '12px',
              minWidth: '18px',
              height: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div
          className="notification-dropdown"
          style={{
            position: 'absolute',
            top: '100%',
            right: '0',
            width: '300px',
            maxHeight: '400px',
            overflowY: 'auto',
            background: 'white',
            border: '1px solid #ddd',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 1000
          }}
        >
          <div
            style={{
              padding: '16px',
              borderBottom: '1px solid #eee',
              fontWeight: 'bold'
            }}
          >
            Notifications
          </div>

          {notifications.length === 0 ? (
            <div style={{ padding: '16px', textAlign: 'center', color: '#666' }}>
              No notifications yet
            </div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${!notification.read ? 'unread' : ''}`}
                style={{
                  padding: '12px 16px',
                  borderBottom: '1px solid #eee',
                  backgroundColor: !notification.read ? '#f0f8ff' : 'white',
                  cursor: 'pointer'
                }}
                onClick={() => !notification.read && markAsRead(notification.id)}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                  <span style={{ fontSize: '20px', flexShrink: 0 }}>
                    {getNotificationIcon(notification.type)}
                  </span>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: 'bold' }}>
                      {notification.title}
                    </h4>
                    <p style={{ margin: '0 0 4px 0', fontSize: '13px', color: '#666' }}>
                      {notification.message}
                    </p>
                    <small style={{ fontSize: '11px', color: '#999' }}>
                      {formatTime(notification.created_at)}
                    </small>
                  </div>
                  {!notification.read && (
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        backgroundColor: '#007bff',
                        borderRadius: '50%',
                        flexShrink: 0
                      }}
                    />
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationComponent;
