// app/api/tools/route.ts
import { NextRequest, NextResponse } from "next/server"


export async function GET() {
    const response = await fetch("https://backend.composio.dev/api/v3/toolkits", {
        method: "GET",
        headers: {
            "x-api-key": process.env.COMPOSIO_API_KEY || ""
        },
    });

    if (!response.ok) {
        return NextResponse.json({ error: "Failed to fetch tools" }, { status: 500 })
    }

    const body = await response.json()

    const tools = body.items.map((item: any) => item.name)

    return NextResponse.json(tools)
}
