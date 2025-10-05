#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import JiraClient from "jira-client";
import dotenv from "dotenv";

dotenv.config();

// Configurar cliente de Jira
const jira = new JiraClient({
  protocol: "https",
  host: process.env.JIRA_HOST || "",
  username: process.env.JIRA_EMAIL || "",
  password: process.env.JIRA_API_TOKEN || "",
  apiVersion: "2",
  strictSSL: true,
});

// Crear servidor MCP
const server = new Server(
  {
    name: "jira-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Definir herramientas disponibles
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_issues",
        description: "Buscar issues en Jira usando JQL",
        inputSchema: {
          type: "object",
          properties: {
            jql: {
              type: "string",
              description: "Query JQL para buscar issues",
            },
            maxResults: {
              type: "number",
              description: "Número máximo de resultados",
              default: 50,
            },
          },
          required: ["jql"],
        },
      },
      {
        name: "get_issue",
        description: "Obtener detalles de un issue específico",
        inputSchema: {
          type: "object",
          properties: {
            issueKey: {
              type: "string",
              description: "Clave del issue (ej: PROJ-123)",
            },
          },
          required: ["issueKey"],
        },
      },
      {
        name: "create_issue",
        description: "Crear un nuevo issue en Jira",
        inputSchema: {
          type: "object",
          properties: {
            project: {
              type: "string",
              description: "Clave del proyecto",
            },
            summary: {
              type: "string",
              description: "Resumen del issue",
            },
            description: {
              type: "string",
              description: "Descripción detallada",
            },
            issueType: {
              type: "string",
              description: "Tipo de issue (Bug, Task, Story, etc.)",
              default: "Task",
            },
          },
          required: ["project", "summary", "issueType"],
        },
      },
      {
        name: "update_issue",
        description: "Actualizar un issue existente",
        inputSchema: {
          type: "object",
          properties: {
            issueKey: {
              type: "string",
              description: "Clave del issue a actualizar",
            },
            fields: {
              type: "object",
              description: "Campos a actualizar",
            },
          },
          required: ["issueKey", "fields"],
        },
      },
      {
        name: "add_comment",
        description: "Agregar un comentario a un issue",
        inputSchema: {
          type: "object",
          properties: {
            issueKey: {
              type: "string",
              description: "Clave del issue",
            },
            comment: {
              type: "string",
              description: "Texto del comentario",
            },
          },
          required: ["issueKey", "comment"],
        },
      },
      {
        name: "list_projects",
        description: "Listar todos los proyectos disponibles",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  };
});

// Implementar las herramientas
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args = {} } = request.params;

    switch (name) {
      case "search_issues": {
        if (!args || typeof args.jql !== 'string') {
          throw new Error("Se requiere un JQL válido");
        }
        
        const results = await jira.searchJira(args.jql, {
          maxResults: (args.maxResults as number) || 50,
        });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case "get_issue": {
        if (!args || typeof args.issueKey !== 'string') {
          throw new Error("Se requiere una clave de issue válida");
        }
        
        const issue = await jira.findIssue(args.issueKey);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(issue, null, 2),
            },
          ],
        };
      }

      case "create_issue": {
        if (!args || typeof args.project !== 'string' || typeof args.summary !== 'string' || typeof args.issueType !== 'string') {
          throw new Error("Se requieren campos válidos para crear un issue");
        }
        
        const newIssue = await jira.addNewIssue({
          fields: {
            project: {
              key: args.project,
            },
            summary: args.summary,
            description: args.description || "",
            issuetype: {
              name: args.issueType,
            },
          },
        });
        return {
          content: [
            {
              type: "text",
              text: `Issue creado exitosamente: ${newIssue.key}`,
            },
          ],
        };
      }

      case "update_issue": {
        if (!args || typeof args.issueKey !== 'string' || !args.fields) {
          throw new Error("Se requiere una clave de issue y campos válidos para actualizar");
        }
        
        await jira.updateIssue(args.issueKey, {
          fields: args.fields,
        });
        return {
          content: [
            {
              type: "text",
              text: `Issue ${args.issueKey} actualizado exitosamente`,
            },
          ],
        };
      }

      case "add_comment": {
        if (!args || typeof args.issueKey !== 'string' || typeof args.comment !== 'string') {
          throw new Error("Se requiere una clave de issue y un comentario válido");
        }
        
        await jira.addComment(args.issueKey, args.comment);
        return {
          content: [
            {
              type: "text",
              text: `Comentario agregado a ${args.issueKey}`,
            },
          ],
        };
      }

      case "list_projects": {
        const projects = await jira.listProjects();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(projects, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Herramienta desconocida: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// Iniciar servidor
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Jira MCP Server ejecutándose en stdio");
}

main().catch((error) => {
  console.error("Error fatal:", error);
  process.exit(1);
});