# Notas de Desarrollo de la Interfaz Gráfica de Usuario (GUI) - Proyecto Gemini Security Monitor

Este documento detalla el progreso, los recursos integrados y las futuras posibilidades de expansión para la interfaz gráfica de usuario del proyecto Gemini Security Monitor. Sirve como una guía práctica y un registro técnico para el desarrollo continuo.

## 1. Objetivo de la GUI

El objetivo principal de esta GUI es enriquecer la experiencia del usuario al proporcionar una **interfaz centralizada y amigable** para gestionar y visualizar las funcionalidades de seguridad implementadas en el sistema. Busca simplificar la interacción con los scripts de PowerShell subyacentes y ofrecer una visión clara del estado de seguridad del equipo.

## 2. Estado Actual de la GUI

La GUI está siendo desarrollada en **Python utilizando la librería `tkinter`** y actualmente cuenta con la siguiente estructura y funcionalidades:

*   **Archivo Principal:** `security_gui.py`
*   **Pestañas Implementadas:**
    *   **Estado General:** Muestra el estado de los servicios de seguridad monitoreados (Cloudflare Warp, Microsoft Defender Antivirus, Firewall de Windows Defender, CrowdSec) y permite ejecutar el script maestro de monitoreo (`start_security_monitors.ps1`).
    *   **Logs de Seguridad:** Permite visualizar el contenido de los archivos de registro clave (`service_monitor_log.txt`, `explorer_window_log.txt`, `integrity_check_log.txt`, `event_logs_integrity.log`) con la opción de actualizar su contenido.
    *   **Integridad de C:\www:** Ofrece botones para calcular los hashes de los archivos en `C:\www\gemini-security-monitor` (establecer línea base) y para verificar la integridad del directorio, mostrando los resultados en tiempo real.
    *   **Seguridad de Puertos:** Permite ejecutar escaneos de puertos y conexiones, mostrando los resultados en tiempo real y registrándolos para análisis.
    *   **Gestión de Usuarios y Privilegios:** Permite listar usuarios locales, grupos y sus miembros, así como los permisos NTFS de directorios críticos.
    *   **Restauración del Sistema:** Permite crear puntos de restauración del sistema antes de realizar cambios críticos.
    *   **Configuración/Acerca de:** Muestra el contenido del documento `GEMINI_SECURITY_OVERVIEW.md`, proporcionando un resumen de las responsabilidades y mecanismos de seguridad.

## 3. Recursos y Herramientas Integrados

La GUI se integra con y aprovecha los siguientes recursos y herramientas:

*   **Python (`tkinter`):** Lenguaje de programación principal para el desarrollo de la GUI, elegido por su simplicidad y capacidad de interacción con scripts de sistema.
*   **Scripts de PowerShell (`.ps1`):** Son el corazón de las funcionalidades de seguridad, realizando tareas como:
    *   Monitoreo y reinicio de servicios críticos.
    *   Identificación de la entidad que detiene servicios.
    *   Monitoreo de cambios en ventanas del Explorador de Archivos y registro de procesos.
    *   Cálculo y verificación de hashes para la integridad de `C:\www\gemini-security-monitor`.
    *   Escaneo y análisis de puertos y conexiones.
    *   Listado de usuarios y privilegios.
    *   Creación de puntos de restauración del sistema.
    *   Respaldo y verificación de integridad de logs de eventos de Windows.
*   **Git:** Utilizado para el control de versiones del código fuente de la GUI y los scripts de seguridad, facilitando la colaboración y el seguimiento de cambios. El protocolo de uso se detalla en `GIT_PROTOCOL.md`.
*   **Visual Studio Code:** Entorno de desarrollo recomendado para la edición y depuración del código.

## 4. Recursos Adicionales y Futuras Integraciones (Potencial)

Se han identificado varias oportunidades para enriquecer la GUI y el sistema de seguridad aprovechando recursos adicionales, incluyendo servicios en la nube y APIs:

*   **Supabase (Opciones Gratuitas):**
    *   **Almacenamiento Remoto de Logs:** Enviar los logs generados por los scripts a una base de datos PostgreSQL en Supabase para un análisis centralizado, persistencia de datos (incluso si los logs locales son eliminados) y acceso remoto.
    *   **Almacenamiento Seguro de Configuraciones:** Guardar configuraciones sensibles o reglas personalizadas de forma remota.
    *   **Verificación de Integridad en la Nube:** Almacenar los hashes de integridad de `C:\www\gemini-security-monitor` en Supabase para una verificación más robusta y a prueba de manipulaciones locales.
    *   **Autenticación:** Si se considera un acceso multiusuario o remoto a la GUI.
*   **Google Cloud Platform (GCP - Nivel Gratuito):**
    *   **Cloud Storage:** Utilizar para copias de seguridad redundantes y seguras de logs o hashes.
    *   **Cloud Functions:** Para procesar logs, realizar análisis o ejecutar acciones de respuesta a eventos de forma remota y sin servidor.
*   **Gemini API:**
    *   **Análisis de Logs Inteligente:** Integrar la API de Gemini para enviar fragmentos de logs y obtener resúmenes, identificar patrones anómalos, detectar anomalías o sugerir acciones de remediación basadas en IA.
    *   **Generación de Informes Avanzados:** Utilizar las capacidades de IA para generar informes de seguridad más detallados, comprensibles y predictivos.
    *   **Asistencia Contextual:** Proporcionar ayuda o explicaciones en tiempo real sobre eventos de seguridad o configuraciones utilizando la IA.

## 5. Próximos Pasos en el Desarrollo

1.  **Mejora del Estado de Servicios:** Implementar la lógica para que la pestaña "Estado General" muestre el estado real de los servicios consultando directamente el sistema.
2.  **Pruebas Exhaustivas:** Realizar pruebas completas de todas las funcionalidades de la GUI y los scripts subyacentes.
3.  **Integración de Recursos en la Nube:** Comenzar a explorar y desarrollar la integración con Supabase, GCP o la API de Gemini según las prioridades.

---

Este documento es un recurso vivo y será actualizado a medida que el proyecto evolucione y se integren nuevas funcionalidades y recursos.