import React from 'react';
import { useNotifications } from '../../contexts/NotificationContext';
import Notification from './Notification';
import './NotificationContainer.css';

const NotificationContainer: React.FC = () => {
  // Este componente ya no muestra notificaciones en pantalla
  // Las notificaciones se muestran en el panel desplegable del NotificationIcon
  return null;
};

export default NotificationContainer;