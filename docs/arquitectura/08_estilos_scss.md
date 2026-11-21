# SCSS y estilos de la interfaz

[Índice](../README.md) · [Entrada SCSS](../../frontend/scss/main.scss) · [CSS distribuido](../../frontend/static/css/style.css)

## Organización

| Archivo | Responsabilidad |
|---|---|
| [`_tokens.scss`](../../frontend/scss/partials/_tokens.scss) | Colores, radios, tokens y valores reutilizables |
| [`_reset.scss`](../../frontend/scss/partials/_reset.scss) | Reseteo, tipografía, foco y accesibilidad |
| [`_navigation.scss`](../../frontend/scss/partials/_navigation.scss) | Cabecera, marca, enlaces y menú |
| [`_components.scss`](../../frontend/scss/partials/_components.scss) | Formularios, tarjetas, estadísticas, tablas y avisos |
| [`_responsive.scss`](../../frontend/scss/partials/_responsive.scss) | Pantallas pequeñas y movimiento reducido |
| [`navigation.js`](../../frontend/static/js/navigation.js) | Menú móvil, accesibilidad mediante `aria-expanded` |
| [`base.html`](../../frontend/templates/base.html) | Estructura HTML semántica, menú activo y plantilla Jinja |

## Editar los estilos

En Windows ejecuta [**`frontend/build_styles.bat`**](../../frontend/build_styles.bat), que utiliza Dart Sass mediante `npx` para producir `frontend/static/css/style.css`. **Solo para editar SCSS** es necesario Node.js/npm y obtener el paquete Sass; la app distribuida no los requiere.

`build_exe.bat` empaqueta el CSS ya compilado y *no* instala Node ni Sass. Los cambios de apariencia se realizan en SCSS; el CSS generado se versiona para permitir ejecutar inmediatamente la app en equipos modestos.

## Principios de diseño

- Mantener jerarquía tipográfica, navegación activa, tarjetas de indicadores y formularios legibles.
- Las pantallas de celulares utilizan un menú desplegable accesible.
- `:focus-visible` ayuda a la navegación mediante teclado; `prefers-reduced-motion` evita animaciones molestas.
- Probar tanto la vista de administrador como `/registro` desde otro dispositivo de la LAN.
