🧠 Explicación General para una IA – Organización Documental URSALL Legal
🏢 Nivel 0: Carpeta Principal de Clientes

Cada cliente tiene una carpeta raíz única, nombrada de manera homogénea según una de las dos siguientes reglas:

Formato Grupo: GRUPO + NOMBRE

Ejemplo: GRUPO GORETTI, GRUPO NEUMATICOS, GRUPO HORINSA

Formato Individual/Empresa: Nombre Completo o Denominación Social

Ejemplo: JJ. TEALQUILA Y GESTIONA SL, PEDRO PEREZ GARCIA

🔹 Propósito: Identificar de forma unívoca al cliente.

📂 Nivel 1: Subcarpetas Principales por Cliente

Cada carpeta de cliente debe contener las mismas subcarpetas estructurales, bajo el siguiente esquema:

1. Procedimientos Judiciales

Escritos presentados

Resoluciones judiciales

Pruebas

03.1 Testifical

03.2 Pericial

03.3 Documental

Doctrina y jurisprudencia

Notificaciones del Juzgado

Anotaciones internas

Documentación del cliente

Carpeta 0 – Almacenamiento rápido

Agenda procesal y plazos

Costas y gastos

2. Proyectos Jurídicos

Cada proyecto se archiva como una carpeta independiente nombrada según la siguiente lógica:

AAAA_MM_Cliente_Proyecto_Materia


Ejemplo:
2025_06_AyuntamientoAdeje_Informe_SeguroSalud

Subcarpetas estándar en cada proyecto:

General

Documentación recibida

Borradores

Documentación de estudio

Comunicaciones

Informe/Documento final

Contratos o convenios asociados

Anexos y notas adicionales

🏷️ Guía de Nomenclatura para Procedimientos Judiciales

Cada procedimiento judicial dentro de un cliente se nombra siguiendo este formato base:

AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia

Según Jurisdicción:
📘 Contencioso-Administrativo:

Ejemplo:
2025_03_CA1_SantaCruz_245/2025_Pedro Perez Vs Cabildo Gomera_Fijeza

⚖️ Social/Laboral:

2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos

📕 Civil:

2025_06_CIV4_SanSebastian_112/2025_Juan López Vs Motor 7 Islas_ReclamacionCantidad

🚔 Penal / Instrucción:

2025_10_JPII_LaGomera_789/2025_MinisterioFiscal Vs Juan Gomez_Art316CP

🔡 Abreviaturas Estandarizadas
Jurisdicción	Abreviatura
Contencioso	CA
Social	SC
Civil	CIV
Penal	PEN
Instrucción	JPI

🔹 Demarcación: puede abreviarse si es muy larga (por ej. “Santa Cruz” → SC).

🔹 Materia: palabra clave sin tildes ni artículos, breve y clara. Ejemplos:
Fijeza, Despidos, ReclamacionCantidad, Urbanismo, Art316CP.

🔹 Partes: Se usan nombres o denominaciones abreviadas:
Pedro Perez, Motor 7 Islas, Cabildo.

📌 Reglas adicionales para IA o sistemas automatizados

Si un documento no ha sido aún clasificado, se coloca en la carpeta 08. Carpeta 0 – Almacenamiento rápido.

Todos los nombres de carpetas deben estar en mayúsculas iniciales o completamente en mayúsculas, según la política de estilo adoptada.

Las fechas siempre deben seguir el formato AAAA_MM.

🧠 ¿Cómo usar esta estructura con una IA?

Puedes entrenar o instruir a una IA (como un modelo LLM o un sistema de clasificación documental) para que:

Identifique el tipo de documento (escrito judicial, sentencia, contrato, correo, etc.).

Extraiga metadatos clave (fecha, tipo de juzgado, número de autos, partes, materia).

Clasifique automáticamente en la carpeta correspondiente dentro de la estructura del cliente.

Genere nombres de carpetas o archivos basándose en las reglas anteriores.

Detecte duplicados o documentos mal ubicados.

✅ Ejemplo práctico para la IA

📄 Documento: Sentencia del Juzgado Social nº 2 de Tenerife, procedimiento 455/2025, entre Pedro Perez y Cabildo Gomera, por despido.

🔍 La IA debe:

Detectar que es una resolución judicial.

Identificar como procedimiento:
2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos

Clasificar dentro de:
Procedimientos Judiciales > [nombre del procedimiento] > 02. Resoluciones judiciales

URSALL LEGAL
│
├── GRUPO GORETTI
│   ├── 1. Procedimientos Judiciales
│   │   ├── 2025_08_SC2_Tenerife_455/2025_Pedro Perez Vs Cabildo Gomera_Despidos
│   │   │   ├── 01. Escritos presentados
│   │   │   ├── 02. Resoluciones judiciales
│   │   │   ├── 03. Pruebas
│   │   │   │   ├── 03.1 Testifical
│   │   │   │   ├── 03.2 Pericial
│   │   │   │   ├── 03.3 Documental
│   │   │   ├── 04. Doctrina y jurisprudencia
│   │   │   ├── 05. Notificaciones del Juzgado
│   │   │   ├── 06. Anotaciones internas
│   │   │   ├── 07. Documentación del cliente
│   │   │   ├── 08. Carpeta 0 – Almacenamiento rápido
│   │   │   ├── 09. Agenda procesal y plazos
│   │   │   └── 10. Costas y gastos
│   │   └── [otros procedimientos...]
│   │
│   └── 2. Proyectos Jurídicos
│       ├── 2025_06_Ursall_Actualizacion_Polizas
│       │   ├── 00. General
│       │   ├── 01. Documentación recibida
│       │   ├── 02. Borradores
│       │   ├── 03. Documentación de estudio
│       │   ├── 04. Comunicaciones
│       │   ├── 05. Informe/Documento final
│       │   ├── 06. Contratos o convenios asociados
│       │   └── 07. Anexos y notas adicionales
│       └── [otros proyectos...]
│
├── JJ. TEALQUILA Y GESTIONA SL
│   ├── 1. Procedimientos Judiciales
│   │   └── [...]
│   └── 2. Proyectos Jurídicos
│       └── [...]
│
└── [OTROS CLIENTES...]
