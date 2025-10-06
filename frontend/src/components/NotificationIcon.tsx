import React, { useState, useRef, useEffect } from 'react';
import { useNotifications } from '../contexts/NotificationContext';
import './NotificationIcon.css';

export function NotificationIcon() {
  const { notifications, removeNotification } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const closeWithAnimation = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsOpen(false);
      setIsClosing(false);
    }, 200); // Duración de la animación
  };

  // Cerrar el dropdown al hacer clic fuera
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) && isOpen && !isClosing) {
        closeWithAnimation();
      }
    }

    // Solo agregar el listener cuando el dropdown está abierto
    if (isOpen && !isClosing) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen, isClosing]);

  const toggleNotifications = () => {
    if (isOpen && !isClosing) {
      closeWithAnimation();
    } else if (!isOpen && !isClosing) {
      setIsOpen(true);
    }
  };

  const handleRemoveNotification = (id: string) => {
    const element = document.querySelector(`[data-notification-id="${id}"]`);
    if (element) {
      element.classList.add('removing');
      setTimeout(() => {
        removeNotification(id);
      }, 300); // Tiempo de la animación
    } else {
      removeNotification(id);
    }
  };

  return (
    <div className="notification-icon-container" ref={dropdownRef}>
      <button 
        className="notification-icon-button" 
        onClick={toggleNotifications}
        aria-label="Notificaciones"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
        </svg>
        {notifications.length > 0 && (
          <span className="notification-badge">{notifications.length}</span>
        )}
      </button>
      
      {(isOpen || isClosing) && (
        <>
          <div className={`notification-dropdown ${isClosing ? 'notification-dropdown--closing' : ''}`}>
            <div className="notification-header">
              <h3>Notificaciones</h3>
              <button 
                className="notification-close-button"
                onClick={closeWithAnimation}
              >
                ×
              </button>
            </div>
            <div className="notification-list">
              {notifications.length === 0 ? (
              <p className="notification-empty">No hay notificaciones</p>
            ) : (
              notifications.map((notification) => (
                <div 
                  key={notification.id} 
                  data-notification-id={notification.id}
                  className={`notification-item notification-item--${notification.type}`}
                >
                  <div className="notification-item-content">
                    <h4>{notification.title}</h4>
                    {notification.message && <p>{notification.message}</p>}
                  </div>
                  <button 
                    onClick={() => handleRemoveNotification(notification.id)}
                    aria-label="Eliminar notificación"
                    className="notification-close-button"
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
        </>
      )}
    </div>
  );
}