/**
 * NotificationContainer Component
 * Contenedor para todas las notificaciones
 * Modificado para no mostrar notificaciones en pantalla
 */
import React from 'react'
import { useNotifications } from '../contexts/NotificationContext'
import './NotificationContainer.css'

export function NotificationContainer() {
  // Este componente ya no muestra notificaciones en pantalla
  // Las notificaciones se muestran en el panel desplegable del NotificationIcon
  return null
}
