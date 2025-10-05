declare module 'jira-client' {
  interface JiraClientOptions {
    protocol: string;
    host: string;
    username: string;
    password: string;
    apiVersion: string;
    strictSSL: boolean;
  }

  interface JiraSearchOptions {
    maxResults?: number;
    startAt?: number;
    fields?: string[];
  }

  class JiraApi {
    constructor(options: JiraClientOptions);
    
    searchJira(jql: string, options?: JiraSearchOptions): Promise<any>;
    findIssue(issueKey: string): Promise<any>;
    addNewIssue(issue: any): Promise<any>;
    updateIssue(issueKey: string, issue: any): Promise<any>;
    addComment(issueKey: string, comment: string): Promise<any>;
    listProjects(): Promise<any>;
  }

  export default JiraApi;
}