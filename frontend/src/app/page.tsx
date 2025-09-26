"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import AgentCard from "@/components/agentCard"
import {Separator} from "@/components/ui/separator";
import {AgentConfig} from "@/types/agent"; // adjust path if needed

export default function Home() {
    const [agents, setAgents] = useState<AgentConfig[]>([0]) // store ids for cards
    const [counter, setCounter] = useState(1) // unique keys

    function addNewAgent() {
        setAgents(prev => [
            ...prev,
            {
                id: counter,
                name: "",
                description: "",
                prompt: "",
                model: "",
                toolkit: "",
            }
        ])
        setCounter(prev => prev + 1)
    }

    function updateAgent(id: number, newConfig: Partial<AgentConfig>) {
        setAgents(prev =>
            prev.map(agent =>
                agent.id === id ? { ...agent, ...newConfig } : agent
            )
        )
    }



    function deleteAgent(id: number) {
        setAgents((prev) => prev.filter((agentId) => agentId !== id))
    }

    async function deployAgents() {
        try {
            console.log("data: ", agents)
            const response = await fetch("/api/deploy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(agents), // send all configs
            })
            if (!response.ok) throw new Error("Failed to deploy")
            console.log("Deployed successfully!")
        } catch (error) {
            console.error(error)
        }
    }

    return (
        <div className="w-full flex flex-row">
            <div className="w-1/2 p-12"></div>
            <div className="w-1/2 flex flex-col p-12 max-h-[100vh] overflow-hidden">
                <div className="flex-1 overflow-y-auto pr-2 box-border space-y-6">
                {agents.map((agent) => (
                    <div key={agent.id}>
                        <AgentCard
                            key={agent.id}
                            agent={agent}
                            onUpdate={(newConfig) => updateAgent(agent.id, newConfig)}
                            onDelete={() => deleteAgent(agent.id)}
                        />
                    </div>
                ))}

                <Button
                    variant="outline"
                    className="mt-4 mb-4 w-full font-semibold"
                    onClick={addNewAgent}
                >
                    🆕 Add new Agent
                </Button>
                </div>

                <div className="mt-4 sticky bottom-0 pt-4">
                    <Separator className="mb-2"/>
                    <div className="w-full flex flex-row justify-end">
                        <Button
                        className="mt-4 text-white text-lg font-semibold bg-linear-65 from-red-500 to-purple-500 hover:opacity-75"
                        size="lg"
                        onClick={deployAgents}
                    >
                        Deploy
                    </Button></div>
                </div>
            </div>
        </div>
    )
}
