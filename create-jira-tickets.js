#!/usr/bin/env node
import JiraClient from "jira-client";
import dotenv from "dotenv";
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Cargar variables de entorno desde jira-mcp-server/.env
dotenv.config({ path: join(__dirname, 'jira-mcp-server', '.env') });

// Configurar cliente de Jira
const jira = new JiraClient({
    protocol: "https",
    host: process.env.JIRA_HOST || "",
    username: process.env.JIRA_EMAIL || "",
    password: process.env.JIRA_API_TOKEN || "",
    apiVersion: "2",
    strictSSL: true,
});

// Definir las Historias de Usuario con sus criterios de aceptación
const userStories = [
    {
        key: "US-01",
        summary: "Subir archivo desde el chat",
        description: `Como usuario, quiero poder adjuntar un archivo directamente en la conversación del chatbot, para iniciar el proceso de organización.

*Criterios de Aceptación:*
- El usuario inicia el flujo del chatbot
- El usuario selecciona un archivo y lo envía
- El sistema guarda el archivo en almacenamiento temporal
- El chatbot confirma la recepción del archivo`
    },
    {
        key: "US-02",
        summary: "Guía por preguntas",
        description: `Como usuario, quiero que el chatbot me haga preguntas secuenciales (p. ej., tipo de documento, cliente, fecha), para capturar la información necesaria.

*Criterios de Aceptación:*
- El usuario ha subido un archivo temporal
- El chatbot pregunta por tipo de documento, cliente y fecha
- El usuario responde a todas las preguntas
- El sistema genera un nombre de archivo nuevo con esos datos
- El chatbot muestra el nombre sugerido al usuario`
    },
    {
        key: "US-03",
        summary: "Validación de respuestas",
        description: `Como usuario, quiero que el sistema valide mis respuestas (p. ej., formato de fecha), para evitar errores antes de continuar.

*Criterios de Aceptación:*
- El sistema valida el formato de las respuestas del usuario
- Si el formato es incorrecto, el chatbot solicita corrección
- Solo continúa con datos validados correctamente`
    },
    {
        key: "US-04",
        summary: "Renombrado automático",
        description: `Como usuario, quiero que el sistema proponga un nuevo nombre de archivo basado en mis respuestas y conserve la extensión original, para estandarizar la nomenclatura.

*Criterios de Aceptación:*
- El sistema genera un nombre de archivo usando los datos proporcionados
- Se conserva la extensión original del archivo
- El nombre sigue un formato estandarizado
- El chatbot muestra el nombre sugerido al usuario`
    },
    {
        key: "US-05",
        summary: "Sugerencia de ruta",
        description: `Como usuario, quiero que el sistema me sugiera la ruta de Dropbox donde debería ir el archivo según mis respuestas, para ubicarlo correctamente.

*Criterios de Aceptación:*
- El usuario ha respondido a las preguntas
- El sistema genera la ruta sugerida en Dropbox
- El chatbot muestra la ruta sugerida al usuario`
    },
    {
        key: "US-06",
        summary: "Resumen previo a confirmación",
        description: `Como usuario, quiero ver un resumen con el nuevo nombre y la ruta sugerida, para revisar y decidir si continuar.

*Criterios de Aceptación:*
- El chatbot muestra un resumen completo con:
  - Nombre original del archivo
  - Nuevo nombre propuesto
  - Ruta de destino en Dropbox
- El usuario puede revisar la información antes de confirmar`
    },
    {
        key: "US-07",
        summary: "Confirmar o cancelar",
        description: `Como usuario, quiero poder confirmar o cancelar la operación desde el chat, para tener control sobre la subida.

*Criterios de Aceptación:*
- El chatbot presenta opciones de "Confirmar" y "Cancelar"
- Si el usuario confirma, se procede a la subida
- Si el usuario cancela, se aborta el proceso
- El chatbot confirma la acción tomada`
    },
    {
        key: "US-08",
        summary: "Subida a Dropbox",
        description: `Como usuario, quiero que, al confirmar, el archivo temporal se suba a la ruta indicada en Dropbox con el nuevo nombre, para completar el proceso.

*Criterios de Aceptación:*
- El usuario confirma la subida
- El sistema sube el archivo a la ruta indicada en Dropbox
- El archivo se guarda con el nuevo nombre
- El chatbot confirma que el archivo fue subido exitosamente`
    },
    {
        key: "US-09",
        summary: "Mensajes de estado en el chat",
        description: `Como usuario, quiero recibir mensajes claros de éxito o error en la conversación (p. ej., "archivo subido", "falló la conexión con Dropbox"), para entender qué ocurrió y qué hacer después.

*Criterios de Aceptación:*
- El chatbot muestra mensajes claros de estado
- En caso de éxito, confirma la operación realizada
- En caso de error, explica qué falló
- Sugiere acciones siguientes cuando sea apropiado`
    },
    {
        key: "US-10",
        summary: "Corregir antes de confirmar",
        description: `Como usuario, quiero poder corregir una respuesta (o volver un paso atrás) antes de confirmar, para ajustar el nombre o la ruta sin empezar desde cero.

*Criterios de Aceptación:*
- El usuario puede solicitar corregir una respuesta anterior
- El sistema permite volver al paso correspondiente
- Se mantiene el contexto de las respuestas previas
- El usuario puede continuar desde donde corrigió`
    }
];

async function createTickets() {
    console.log('Iniciando creación de tickets en Jira...\n');

    for (const story of userStories) {
        try {
            console.log(`Creando ${story.key}: ${story.summary}...`);

            const issue = await jira.addNewIssue({
                fields: {
                    project: {
                        key: "AD"
                    },
                    summary: `${story.key} — ${story.summary}`,
                    description: story.description,
                    issuetype: {
                        name: "Tarea"
                    }
                }
            });

            console.log(`✓ Creado: ${issue.key} - ${story.summary}\n`);

        } catch (error) {
            console.error(`✗ Error al crear ${story.key}:`, error.message);
            if (error.response && error.response.data) {
                console.error('Detalles:', JSON.stringify(error.response.data, null, 2));
            }
            console.log('');
        }
    }

    console.log('Proceso completado.');
}

createTickets().catch(console.error);
