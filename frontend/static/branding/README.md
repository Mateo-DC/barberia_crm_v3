# 🎨 Branding Assets · Golden Barber Shop + Moda Lavoe

Colección oficial de recursos gráficos e identidad visual reconstruidos en formatos vectoriales y optimizados para su implementación en la plataforma web.

---

## 📦 Archivos incluidos

| Archivo                  | Formato | Descripción y uso principal                                                                    |
| :----------------------- | :-----: | :--------------------------------------------------------------------------------------------- |
| `favicon.ico`            |   ICO   | Icono clásico del navegador basado en la **J** de _Golden Barber Shop_.                        |
| `favicon.png`            |   PNG   | Versión rasterizada de alta calidad (ideal para dispositivos Apple/móviles).                   |
| `favicon.svg`            |   SVG   | Versión vectorial escalable del icono principal.                                               |
| `monogram-j.svg`         |   SVG   | Monograma **J** diseñado para barras de navegación, cabeceras o pantallas de inicio de sesión. |
| `golden-barber-shop.svg` |   SVG   | Logotipo principal vectorial de **Golden Barber Shop**.                                        |
| `moda-lavoe.svg`         |   SVG   | Logotipo principal vectorial de **Moda Lavoe**.                                                |

---

## 📁 Ubicación recomendada en el proyecto

Para mantener el orden de los archivos estáticos, se recomienda alojar todos estos recursos en la siguiente ruta:

```text
frontend/
└── static/
    └── branding/
        ├── favicon.ico
        ├── favicon.png
        ├── favicon.svg
        ├── monogram-j.svg
        ├── golden-barber-shop.svg
        └── moda-lavoe.svg
```

---

## 💻 Guía de implementación

### 1. Configuración de Favicons (`base.html`)

Agrega las siguientes etiquetas dentro de la sección `<head>` de tu plantilla base para asegurar compatibilidad en todos los navegadores y dispositivos:

```html
<!-- Favicons & App Icons -->
<link rel="icon" href="/static/branding/favicon.ico" sizes="any" />
<link rel="icon" type="image/svg+xml" href="/static/branding/favicon.svg" />
<link rel="apple-touch-icon" href="/static/branding/favicon.png" />
```

### 2. Logo de cabecera o Login

Ejemplo de inserción del monograma en componentes de interfaz:

```html
<img
  src="/static/branding/monogram-j.svg"
  alt="Golden Barber Shop"
  width="40"
  height="40"
/>
```

---

> **ℹ️ Nota técnica:** Todos los archivos SVG han sido vectorizados y limpiados a partir de las referencias originales para garantizar nitidez en cualquier resolución y tiempos de carga óptimos.
