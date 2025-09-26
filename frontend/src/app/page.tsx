"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import AgentCard from "@/components/agentCard" // adjust path if needed

export default function Home() {
    const [agents, setAgents] = useState<number[]>([0]) // store ids for cards
    const [counter, setCounter] = useState(1) // unique keys

    function addNewAgent() {
        setAgents((prev) => [...prev, counter])
        setCounter((prev) => prev + 1)
    }


    function deleteAgent(id: number) {
        setAgents((prev) => prev.filter((agentId) => agentId !== id))
    }

    return (
        <div className="w-full flex flex-row p-12">
            <div className="w-1/2"></div>
            <div className="w-1/2">
                {agents.map((id) => (
                    <div key={id} className="mb-6">
                        <AgentCard onDelete={() => deleteAgent(id)}/>
                    </div>
                ))}

                <Button
                    variant="outline"
                    className="mt-4 w-full font-semibold"
                    onClick={addNewAgent}
                >
                    🆕 Add new Agent
                </Button>
            </div>
        </div>
    )
}
