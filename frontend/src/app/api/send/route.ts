// app/api/send/route.ts
import { NextRequest, NextResponse } from 'next/server';

interface SendMessageRequest {
    agent_set_id: string;
    message: string;
    conversation_id?: string;
}

interface ApiResponse {
    success: boolean;
    message: string;
    agent_response: string;
    conversation_id: string;
    usage?: {
        [key: string]: any;
    };
}

export async function POST(request: NextRequest) {
    try {
        const body: SendMessageRequest = await request.json();

        // Validate required fields
        if (!body.agent_set_id || !body.message) {
            return NextResponse.json(
                {
                    error: 'Missing required fields: agent_set_id and message are required'
                },
                { status: 400 }
            );
        }

        // Determine which endpoint to use based on whether we have a conversation_id
        const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://your-api-base-url.com';
        let apiUrl: string;
        let requestBody: any;

        if (body.conversation_id) {
            // Use existing conversation endpoint
            apiUrl = `${baseUrl}/api/v1/conversations/${body.conversation_id}/messages`;
            requestBody = {
                message: body.message
            };
        } else {
            // Create new conversation endpoint
            apiUrl = `${baseUrl}/api/v1/conversations`;
            requestBody = {
                agent_set_id: body.agent_set_id,
                message: body.message
            };
        }

        // Make request to external API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add authorization header if needed
                // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorData = await response.text();
            console.error('API Error:', errorData);
            return NextResponse.json(
                {
                    error: 'Failed to send message to agent',
                    details: errorData
                },
                { status: response.status }
            );
        }

        const data: ApiResponse = await response.json();

        // Return the response
        return NextResponse.json({
            success: data.success,
            message: data.message,
            agent_response: data.agent_response,
            conversation_id: data.conversation_id,
            usage: data.usage
        });

    } catch (error) {
        console.error('Error in send API route:', error);
        return NextResponse.json(
            {
                error: 'Internal server error',
                message: error instanceof Error ? error.message : 'Unknown error'
            },
            { status: 500 }
        );
    }
}