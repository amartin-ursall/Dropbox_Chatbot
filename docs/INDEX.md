# 📚 Índice de Documentación - Dropbox AI Organizer

## 🚀 Inicio Rápido

- **[../QUICK_START.md](../QUICK_START.md)** - Guía de inicio rápido en 3 pasos
- **[RESUMEN_CONFIGURACION.txt](./RESUMEN_CONFIGURACION.txt)** - Resumen ejecutivo completo

## ⚙️ Configuración HTTPS y Despliegue

### Desarrollo Local
- **[HTTPS_SETUP.md](./HTTPS_SETUP.md)** - Configuración HTTPS detallada para desarrollo
- **[CONFIGURACION_COMPLETADA.md](./CONFIGURACION_COMPLETADA.md)** - Resumen de todos los cambios implementados

### Producción
- **[PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)** - Guía completa de despliegue en producción
  - Certificados SSL válidos (Let's Encrypt)
  - Configuración de Nginx
  - Docker y systemd
  - DNS y dominio

## 📖 Documentación Técnica

### Sistema URSALL Legal
- **[URSALL_IMPLEMENTATION.md](./URSALL_IMPLEMENTATION.md)** - Implementación del sistema URSALL
- **[URSALL_USAGE.md](./URSALL_USAGE.md)** - Guía de uso del sistema URSALL

### Configuración y APIs
- **[SETUP_GEMINI.md](./SETUP_GEMINI.md)** - Configuración de Google Gemini AI
- **[carpetas.md](./carpetas.md)** - Estructura de carpetas del proyecto
- **[interfaces.md](./interfaces.md)** - Interfaces y tipos TypeScript
- **[diagrama_flujo_ia.md](./diagrama_flujo_ia.md)** - Diagrama de flujo de IA

## 🔍 Navegación por Tema

### Para Desarrolladores
1. Inicio rápido → [QUICK_START.md](../QUICK_START.md)
2. Configuración HTTPS → [HTTPS_SETUP.md](./HTTPS_SETUP.md)
3. Sistema URSALL → [URSALL_IMPLEMENTATION.md](./URSALL_IMPLEMENTATION.md)

### Para DevOps / Sysadmins
1. Configuración SSL → [HTTPS_SETUP.md](./HTTPS_SETUP.md)
2. Despliegue producción → [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)
3. Resumen técnico → [CONFIGURACION_COMPLETADA.md](./CONFIGURACION_COMPLETADA.md)

### Para Usuarios Finales
1. Inicio rápido → [QUICK_START.md](../QUICK_START.md)
2. Uso del sistema URSALL → [URSALL_USAGE.md](./URSALL_USAGE.md)

## 📁 Estructura de Archivos

```
docs/
├── INDEX.md (este archivo)           # Índice de documentación
│
├── 🚀 Inicio y Configuración
│   ├── RESUMEN_CONFIGURACION.txt     # Resumen ejecutivo
│   └── CONFIGURACION_COMPLETADA.md   # Cambios implementados
│
├── 🔒 HTTPS y Despliegue
│   ├── HTTPS_SETUP.md                # Setup HTTPS desarrollo
│   └── PRODUCTION_DEPLOYMENT.md      # Despliegue producción
│
├── ⚖️ Sistema URSALL
│   ├── URSALL_IMPLEMENTATION.md      # Implementación
│   └── URSALL_USAGE.md               # Guía de uso
│
└── 📖 Documentación Técnica
    ├── SETUP_GEMINI.md               # Configuración Gemini AI
    ├── carpetas.md                   # Estructura de carpetas
    ├── interfaces.md                 # Interfaces TypeScript
    └── diagrama_flujo_ia.md          # Diagrama de flujo IA
```

## 🔗 Enlaces Externos

- [Dropbox API Documentation](https://www.dropbox.com/developers/documentation)
- [Dropbox OAuth Guide](https://www.dropbox.com/developers/documentation/http/documentation#oauth2-authorize)
- [Google Gemini AI](https://ai.google.dev/)
- [Let's Encrypt](https://letsencrypt.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

## 📝 Notas

- Todos los documentos están en formato Markdown (.md) excepto RESUMEN_CONFIGURACION.txt
- Los scripts de inicio están en la carpeta `../scripts/`
- Los certificados SSL están en `../frontend/ssl/`
- Para contribuir, ver [../README.md](../README.md)

---

✅ **Documentación organizada y completa**
