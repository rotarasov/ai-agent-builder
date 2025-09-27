import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        // Parse incoming JSON body
        const agents = await request.json();

        console.log("Received agents:", agents);

        // Forward to external API
        const response = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL +"/api/v1/agent-sets/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // Add auth header if needed:
                // "Authorization": `Bearer ${process.env.BACKEND_API_KEY}`
            },
            body: JSON.stringify(agents),
        });

        if (!response.ok) {
            const text = await response.text();
            console.error("External API error:", text);
            return NextResponse.json({ error: "Failed to deploy agents" }, { status: 500 });
        }
        return NextResponse.json({ success: true, response});
    } catch (err: any) {
        console.error("POST /api/deploy error:", err.message);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
