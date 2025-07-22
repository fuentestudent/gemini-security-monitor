# Protocolo y Guía Práctica de Git para el Proyecto de Ciberseguridad

Este documento establece las directrices y mejores prácticas para el uso de Git en el proyecto de ciberseguridad, asegurando un flujo de trabajo colaborativo, eficiente y con un historial de versiones claro y consistente.

## 1. Configuración Inicial de Git

Antes de comenzar, asegúrate de que Git esté configurado correctamente en tu sistema. Si aún no lo has hecho, ejecuta los siguientes comandos en tu terminal (reemplaza con tu nombre y correo electrónico):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"
```

## 2. Flujo de Trabajo Básico

Se recomienda un flujo de trabajo basado en ramas (branching) para el desarrollo de nuevas funcionalidades y correcciones de errores.

### 2.1. Clonar el Repositorio (si no lo has hecho ya)

Si estás empezando desde cero, clona el repositorio remoto:

```bash
git clone <URL_del_repositorio_remoto>
cd <nombre_del_repositorio>
```

### 2.2. Mantener tu Rama Principal Actualizada

Antes de empezar a trabajar en una nueva funcionalidad o corrección, asegúrate de que tu rama principal (`main` o `master`) esté actualizada con los últimos cambios del repositorio remoto:

```bash
git checkout main
git pull origin main
```

### 2.3. Crear una Nueva Rama para el Desarrollo

Siempre trabaja en una rama separada para cada nueva funcionalidad o corrección de error. Esto mantiene la rama principal limpia y estable.

```bash
git checkout -b feature/nombre-de-la-funcionalidad # Para nuevas funcionalidades
# o
git checkout -b bugfix/descripcion-del-bug # Para correcciones de errores
```

### 2.4. Realizar Cambios y Confirmar (Commit)

Realiza tus cambios en los archivos. Una vez que hayas completado una parte lógica de tu trabajo, añade los cambios al área de preparación (staging area) y luego confírmalos:

```bash
git add .
# o para archivos específicos:
# git add archivo1.py archivo2.md

git commit -m "feat: Descripción concisa de la nueva funcionalidad"
# o
# git commit -m "fix: Descripción concisa de la corrección del bug"
# o
# git commit -m "docs: Actualización de la documentación"
```

**Mensajes de Commit:**
*   Utiliza un formato claro y conciso.
*   Comienza con un prefijo que indique el tipo de cambio (`feat`, `fix`, `docs`, `chore`, `refactor`, `style`, `test`, etc.).
*   La primera línea debe ser un resumen de no más de 50-72 caracteres.
*   Si es necesario, añade un cuerpo más detallado después de una línea en blanco.

### 2.5. Subir tus Cambios a la Rama Remota

Una vez que hayas realizado commits en tu rama local, súbelos al repositorio remoto:

```bash
git push origin nombre-de-tu-rama
```

### 2.6. Abrir una Solicitud de Extracción (Pull Request - PR)

Cuando tu funcionalidad o corrección esté lista para ser revisada e integrada en la rama principal, abre una Pull Request en la plataforma Git (GitHub, GitLab, Bitbucket, etc.).

## 3. Resolución de Conflictos

Si al hacer `git pull` o al intentar fusionar tu rama, Git detecta conflictos, deberás resolverlos manualmente. Git marcará los archivos con conflictos. Edita los archivos para elegir las versiones correctas y luego:

```bash
git add archivo_con_conflicto
git commit -m "fix: Resolver conflictos de fusión"
```

## 4. Convenciones de Nomenclatura

*   **Ramas:** Utiliza nombres descriptivos y en minúsculas, separados por guiones. Prefijos comunes:
    *   `feature/`: Para nuevas funcionalidades.
    *   `bugfix/`: Para correcciones de errores.
    *   `hotfix/`: Para correcciones urgentes en producción.
    *   `docs/`: Para cambios en la documentación.
    *   `chore/`: Para tareas de mantenimiento que no afectan el código de producción.
*   **Tags:** Utiliza tags para marcar versiones importantes (e.g., `v1.0.0`, `v1.0.1`).

## 5. Ignorar Archivos

Utiliza el archivo `.gitignore` para especificar archivos y directorios que Git debe ignorar (e.g., archivos de configuración local, dependencias de módulos, archivos temporales, logs). Asegúrate de que los archivos sensibles o generados automáticamente no se suban al repositorio.

## 6. Seguridad en Git

*   **Nunca subas credenciales o información sensible** directamente al repositorio. Utiliza variables de entorno o sistemas de gestión de secretos.
*   Revisa los cambios antes de hacer commit y push.
*   Utiliza SSH para la autenticación con el repositorio remoto cuando sea posible.

## 7. Herramientas Adicionales

*   **Visual Studio Code:** Utiliza las extensiones de Git para una mejor experiencia de usuario.
*   **Git LFS:** Para manejar archivos grandes (si es necesario).

---

Este protocolo es un documento vivo y puede ser actualizado a medida que el proyecto evolucione. La colaboración y el seguimiento de estas directrices son clave para el éxito del proyecto.