import React from 'react';
import './Notification.css';

export type NotificationType = 'success' | 'error' | 'info';

export interface NotificationProps {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
  onClose?: (id: string) => void;
}

const Notification: React.FC<NotificationProps> = ({ 
  id, 
  type, 
  message, 
  onClose 
}) => {
  const handleClose = () => {
    if (onClose) {
      onClose(id);
    }
  };

  return (
    <div className={`notification notification--${type}`}>
      <div className="notification__content">
        <span className="notification__message">{message}</span>
      </div>
      <button className="notification__close" onClick={handleClose}>
        &times;
      </button>
    </div>
  );
};

export default Notification;