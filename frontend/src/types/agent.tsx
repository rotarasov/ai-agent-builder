export interface AgentConfig {
        id: number
        name: string
        description: string
        system_prompt: string
        model_name: string
        tools?: string
    }


export interface AgentSet {
        uuid: string;
        created_at: string;
        status: string;
        name?: string;  // Add other properties as needed
        // Add any other fields from your Supabase table
}