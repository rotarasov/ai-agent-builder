import dotenv from "dotenv"

dotenv.config()


export async function getToolsFromComposio() {
    const tools: string[] = []

    const response = await fetch("https://backend.composio.dev/api/v3/toolkits", {
        method: "GET",
        headers: {
            "x-api-key": process.env.COMPOSIO_API_KEY || "", // replace with your env var name
        },
    })

    if (!response.ok) {
        throw new Error(`Failed to fetch tools: ${response.status}`)
    }

    const body = await response.json()

    for (const item of body.items) {
        tools.push(item.name)
    }

    console.log(tools)
    return tools
}
