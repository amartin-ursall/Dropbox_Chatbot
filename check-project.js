#!/usr/bin/env node
import JiraClient from "jira-client";
import dotenv from "dotenv";
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: join(__dirname, 'jira-mcp-server', '.env') });

const jira = new JiraClient({
    protocol: "https",
    host: process.env.JIRA_HOST || "",
    username: process.env.JIRA_EMAIL || "",
    password: process.env.JIRA_API_TOKEN || "",
    apiVersion: "2",
    strictSSL: true,
});

async function checkProject() {
    try {
        console.log('Obteniendo información del proyecto AD...\n');

        // Obtener el proyecto
        const project = await jira.getProject('AD');
        console.log(`Proyecto: ${project.name} (${project.key})\n`);

        // Obtener los tipos de incidencias del proyecto
        console.log('Tipos de incidencias disponibles:');
        if (project.issueTypes) {
            project.issueTypes.forEach(type => {
                console.log(`- ${type.name}`);
            });
        }
    } catch (error) {
        console.error('Error:', error.message);
        if (error.response && error.response.data) {
            console.error('Detalles:', JSON.stringify(error.response.data, null, 2));
        }
    }
}

checkProject();
