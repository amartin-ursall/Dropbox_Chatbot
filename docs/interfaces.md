Arquitectura de la UI (alto nivel)

AppShell

LeftSidebar / ConversationsList (colapsable, resizable)

MainPane

ChatHeader

MessageViewport (lista virtualizada + ancla de scroll)

MessageBubble(User/Assistant/System)

ToolResultCard / WidgetCard (resultados enriquecidos)

CodeBlock (con copia/colapso)

Composer (textarea + adjuntos + acciones)

RightPane / Canvas / Inspector (panel secundario acoplable con pestañas)

GlobalOverlays: Toast, Dialog/Modal, CommandPalette, ContextMenu

Nombres de componentes (React/Design System - Modernizado)

Layout:
- AppShell, LeftSidebar, MainPane, RightPane, ResizableHandle, SplitView, PanelGroup

Navigation:
- ConversationItem, ConversationGroup, NewChatButton, SearchInput, FilterChip, QuickActionMenu, StorageIndicator

Chat:
- ChatHeader, MessageViewport, MessageBubble, Avatar, AvatarGroup, InlineToolbar, CitationsRail, MessageActions, ThreadView, BranchIndicator

Rich content:
- ToolResultCard, WidgetFinance, WidgetSchedule, WidgetChart, ImageCarousel, FilePreview, PDFViewer, VideoPlayer, AudioWaveform, MarkdownRenderer, MermaidDiagram, TableViewer

Code:
- CodeBlock, CodeEditor, CopyButton, ExpandButton, InsertButton, DiffViewer, SyntaxHighlighter, LanguageSelector, LineNumbers

Input:
- Composer, RichTextEditor, AttachmentTray, AttachmentCard, VoiceButton, SendButton, StopButton, EmojiPicker, MentionSuggest, SlashCommands, DragDropZone

Feedback:
- TypingIndicator, AnimatedDots, Toast, Banner, ProgressBar, Skeleton, EmptyState, ErrorBoundary, LoadingSpinner

Utility:
- ThemeToggle, ShortcutHints, DropdownMenu, Popover, Tooltip, ContextMenu, Modal, Drawer, Accordion, Tabs, Badge, Chip, Divider

Providers:
- ThemeProvider, I18nProvider, RouterProvider, CommandKProvider, WebSocketProvider, AuthProvider, AnalyticsProvider

Nuevos componentes AI-specific:
- PromptLibrary, PromptTemplate, ModelSelector, TokenCounter, StreamingText, ThinkingIndicator, ToolCallCard, FunctionInvocation, JSONViewer

Layout y grid (Modernizado)

Breakpoints (responsive-first):

xs: 375px (mobile S), sm: 640px (mobile L), md: 768px (tablet), lg: 1024px (laptop), xl: 1280px (desktop), 2xl: 1536px (wide), 3xl: 1920px (ultra-wide)

Sidebar:
- Desktop: 300px (expandido) | 64px (collapsed rail con iconos)
- Mobile: 100vw overlay con backdrop blur
- Transición: 250ms cubic-bezier(0.4, 0, 0.2, 1)

RightPane (Canvas/Inspector):
- Desktop: 400–480px (resizable con snap points)
- Tablet: 360px
- Mobile: hidden (acceso vía modal)
- Soporte para picture-in-picture en scroll

Header:
- Desktop: 64px (altura fija)
- Mobile: 56px
- Sticky con backdrop-filter: blur(12px) + shadow on scroll

Composer:
- Min: 72px | Max: 240px (auto-grow hasta 10 líneas)
- Padding interno: 16px
- Soporte para rich text preview y multi-file attachments

Max width de contenido:
- Burbuja de mensaje: 768px
- Código: 100% (con horizontal scroll si necesario)
- Imágenes/media: 1024px

Paleta de colores (Dark Mode + semánticos)

--surface-0: #0B1220

--surface-1: #0F172A (slate-900)

--surface-2: #1F2937 (gray-800)

--text-primary: #E5E7EB

--text-secondary: #9CA3AF

--border: #334155

--brand-400: #A78BFA (violet-400)

--brand-600: #7C3AED

--link: #60A5FA

Estados:
--success: #10B981 · --warning: #F59E0B · --danger: #EF4444 · --info: #0EA5E9

Gradiente de marca:
linear-gradient(135deg, #7C3AED 0%, #06B6D4 100%) (violeta → cian) para acentos hero.

Tokens de diseño (CSS variables)
:root {
  --radius-xs: 6px; --radius-sm: 10px; --radius-md: 14px; --radius-lg: 16px; --radius-2xl: 24px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-6: 24px; --space-8: 32px;
  --shadow-1: 0 1px 2px rgba(0,0,0,.06);
  --shadow-2: 0 4px 12px rgba(0,0,0,.10);
  --shadow-3: 0 10px 24px rgba(0,0,0,.16);
  --focus-ring: 0 0 0 3px rgba(37,99,235,.35);

  /* colores dark mode */
  --surface-0: #0B1220;
  --surface-1: #0F172A;
  --surface-2: #1F2937;
  --text-primary: #E5E7EB;
  --text-secondary: #9CA3AF;
  --border: #334155;
  --brand-400: #A78BFA;
  --brand-600: #7C3AED;
  --link: #60A5FA;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --info: #0EA5E9;
}

Tipografía (Modernizada)

Font stack:
- Sans: 'Inter Variable', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif
- Mono: 'Fira Code', 'JetBrains Mono', 'SF Mono', 'Cascadia Code', Consolas, monospace
- Display: 'Cal Sans' (opcional, para hero/marketing)

Escala tipográfica (fluid responsive):
- display-1: 48px/56px (clamp 36-48px) · weight 700
- display-2: 40px/48px (clamp 32-40px) · weight 700
- display-3: 32px/40px (clamp 28-32px) · weight 600
- h1: 28px/36px (clamp 24-28px) · weight 600
- h2: 24px/32px (clamp 20-24px) · weight 600
- h3: 20px/28px (clamp 18-20px) · weight 600
- h4: 18px/26px · weight 600
- body-large: 17px/26px · weight 400
- body: 16px/24px · weight 400
- body-small: 15px/22px · weight 400
- caption: 14px/20px · weight 500
- overline: 13px/18px · weight 600 · uppercase · letter-spacing: 0.05em
- mono-code: 14px/22px (Fira Code) · weight 400, 500

Pesos variables:
- Variable font axes: wght 300-700
- Regular: 400, Medium: 500, Semibold: 600, Bold: 700
- Mono: 400, 500 (semibold para keywords)

Features OpenType:
- font-feature-settings: 'cv02', 'cv03', 'cv04', 'ss01', 'ss02' (Inter)
- Ligatures en código: 'calt', 'liga' (Fira Code)
- Tabular numbers: 'tnum' (para tablas/métricas)

Accesibilidad:
- Contraste WCAG AAA: mínimo 7:1 en headings, 4.5:1 en body
- Tamaño mínimo: 14px (legibilidad)
- Line-height: 1.5-1.6 para párrafos largos
- Max line-length: 70ch (óptima lectura)

Estados y comportamientos clave (Modernizados)

Streaming & Generación:
- MessageBubble con StreamingText (typewriter effect + cursor pulsante)
- ThinkingIndicator (animated dots) mientras procesa
- StopButton (⌘/Ctrl+.) para interrumpir
- RegenerateButton con opciones: "Try again", "Continue", "Branch"
- Progress indicator para tareas largas (con ETA estimado)

Citas & Referencias:
- CitationChip inline con número superscript [1]
- CitationsRail lateral con preview cards
- Hover: popover con snippet + source link
- Click: scroll to source + highlight

CodeBlock (Mejorado):
- Auto-detección de lenguaje con 150+ sintaxis
- Syntax highlighting (Shiki/Prism)
- Botones: Copy, Expand/Collapse, Insert, Download, Share
- Line numbers con selección de rango
- Diff view para comparaciones
- Run/Execute en playground (sandboxed)

Adjuntos & Media:
- AttachmentTray con grid de miniaturas (max 10 visibles)
- Drag & drop zone con progress bars
- Preview modal con zoom, rotate, download
- Formatos: Images, PDF, Office docs, Code files, Audio, Video
- Límites: 25MB per file, 10 files max

Widgets & Rich Content:
- ToolResultCard variantes:
  • TableViewer (sortable, filterable, exportable)
  • ChartWidget (line, bar, pie con interactividad)
  • ImageGallery (masonry layout + lightbox)
  • CalendarWidget (agenda, timeline view)
  • MapWidget (con markers y geocoding)
  • JSONViewer (collapsible tree con search)

Virtualización:
- VirtualizedList (react-virtual) para 1000+ mensajes
- Infinite scroll bidireccional
- ScrollAnchor con smooth scroll
- "Jump to latest" floating button
- Scroll position persistence

Errores & Notificaciones:
- ErrorBoundary con retry/reset options
- Toast system (stack máx 3):
  • Success (✓) 3s autodismiss
  • Error (✗) 6s con action
  • Info (ℹ️) 4s autodismiss
  • Warning (⚠️) persistente
- Banner global para maintenance/updates
- Inline error states con sugerencias de fix

Atajos de teclado (extendidos):
- ⌘/Ctrl+K: Command Palette
- ⌘/Ctrl+N: New chat
- ⌘/Ctrl+Enter: Send message
- ⌘/Ctrl+.: Stop generation
- ⌘/Ctrl+R: Regenerate
- ⌘/Ctrl+\: Toggle right panel
- ⌘/Ctrl+B: Toggle sidebar
- ⌘/Ctrl+F: Search in conversation
- ⌘/Ctrl+/: Show shortcuts
- Esc: Cancel/close/blur
- ↑/↓: Navigate history en Composer
- Tab: Accept autocomplete
- Shift+Enter: New line in Composer

Estilos de las burbujas

User: fondo --brand-600, texto blanco, radius 16–20px, alineada a derecha

Assistant: --surface-2, borde --border, radius 16–20px, alineada a izquierda

System/Info: --surface-1, tipografía secundaria, icono sutil

Estructura de datos (modelo)
type Conversation = {
  id: string; title: string; createdAt: string; updatedAt: string;
  messages: MessageSummary[];
}
type Message = {
  id: string; role: 'user'|'assistant'|'system';
  content: RichText[]; // text, code, image, widget
  citations?: Citation[];
  toolInvocations?: ToolInvocation[];
  createdAt: string; state?: 'streaming'|'complete'|'error';
}
type ToolInvocation = {
  id: string; name: string; status: 'running'|'succeeded'|'failed';
  input: any; output?: any; widgetType?: 'table'|'image'|'chart'|'schedule';
}

Estados del Composer (máquina simple)

idle → typing → sending → assistant_streaming → idle

Interrupciones: assistant_streaming → stopped|error

Subestados: attaching, recording_voice, uploading

Accesibilidad (A11y)

Roles y etiquetas:

role="log" + aria-live="polite" en MessageViewport

aria-expanded/aria-controls en paneles acoplables

Focus visible con --focus-ring

Objetivos táctiles ≥ 44×44px

Navegación por teclado completa (Tab/Shift+Tab, Home/End para viewport)

Z-index (capas)

0 contenido

10 header/footer

20 popovers/menus

30 toasts

40 dialogs

50 command-palette

Sombras/elevación (mapa)

Flat: sin sombra (cards en --surface-2)

Hover: --shadow-1

Active: --shadow-2

Modal: --shadow-3 + backdrop rgba(0,0,0,.45)

Microinteracciones

Transición 150–200ms ease-out, transform + opacity

MessageBubble entra con fade+slide 8px

TypingIndicator como tres puntos con prefers-reduced-motion soportado

Estructura del Sidebar (Modernizada)

Header:
- Logo + avatar usuario (con dropdown: settings, logout)
- NewChatButton (⌘/Ctrl+N) - primario, destacado
- CollapseButton (toggle rail mode)

SearchBar:
- Input con icon search + ⌘K shortcut hint
- Filtros rápidos: All, Pinned, Today, Week, Archived
- Búsqueda fuzzy con highlighting de resultados

ConversationList (virtualized):
- Grupos colapsables con contador:
  • Pinned (máx 5, drag-reorder)
  • Today
  • Yesterday
  • Last 7 days
  • Last 30 days
  • Archived (load on demand)

ConversationItem:
- Hover: background highlight + quick actions (pin, archive, delete)
- Active: border-left accent (--brand-400)
- Context menu (right-click): rename, duplicate, export, share
- Drag & drop para organizar/mover a grupos

Footer:
- Storage usage indicator (con upgrade CTA si aplica)
- Shortcuts hint button (?)

Panel derecho (Canvas/Inspector - Modernizado)

Pestañas (con iconos + badge counters):
1. Canvas (📄)
   - Document preview/edit
   - Code playground con hot reload
   - Image/media viewer con zoom/pan
   - Export options (PDF, MD, HTML)

2. Tools (🛠️)
   - Historial de tool invocations
   - Status indicators (running/success/failed)
   - Input/output expandibles
   - Retry/edit functionality

3. Details (ℹ️)
   - Message metadata:
     • Model usado
     • Tokens: input/output/total
     • Latency/duration
     • Cost estimate
   - Citations & sources
   - Version history (branches)

4. Analytics (📊) [nuevo]
   - Conversation insights
   - Token usage charts
   - Response quality metrics
   - Export conversation data

Features:
- Resizable: snap points a 360/420/520/640px
- Picture-in-picture mode (floating mini panel)
- Keyboard shortcut: ⌘/Ctrl+\ (toggle)
- Persist state per conversation