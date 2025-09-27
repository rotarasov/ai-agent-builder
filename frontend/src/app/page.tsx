"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import AgentCard from "@/components/agentCard"
import {Separator} from "@/components/ui/separator";
import {AgentConfig, AgentSet} from "@/types/agent";
import CommunityAgentCard from "@/components/communityAgentCard";
import DeployConfirmationDialog from "@/components/deploymentDialog";

export default function Home() {
    const [agents, setAgents] = useState<AgentConfig[]>([{
        id: 0,
        name: "",
        description: "",
        system_prompt: "",
        model_name: "",
        tools: "",
    }]) // store ids for cards
    const [counter, setCounter] = useState(1) // unique keys
    const [agent_sets, setAgent_sets] = useState<AgentSet[]>([]) // Agent sets
    const [tools, setTools] = useState<string[]>([])


    function addNewAgent() {
        setAgents(prev => [
            ...prev,
            {
                id: counter,
                name: "",
                description: "",
                system_prompt: "",
                model_name: "",
                tools: "",
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
    async function fetchTools() {
        const res = await fetch("/api/tools")
        return await res.json()
    }

    async function fetchAgentSets() {
        const res = await fetch("/api/agentsets")
        const data = await res.json();
        console.log("agent sets: ", data);
        return data;
    }


    React.useEffect(() => {
        async function loadTools() {
            const fetchedTools = await fetchTools()
            setTools(fetchedTools)
        }
        loadTools().then(r => {})
    }, [])

    React.useEffect(() => {
        async function loadSets() {
            const fetchedSets = await fetchAgentSets()
            setAgent_sets(fetchedSets)
        }
        loadSets().then(r => {})
    }, [])


    function deleteAgent(id: number) {
        setAgents(prev => prev.filter(agent => agent.id !== id))
    }

    async function deployAgents(name:string) {
        try {
            const payload = {agents:
                    agents.map(({ id, tools, ...rest }) => ({
                ...rest,
                tools: Array.isArray(tools) ? tools : [tools], // wrap in array if needed
            })),
            name: name}
            console.log("data to deploy:", payload);

            const response = await fetch("/api/deploy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload), // send all configs
            })
            if (!response.ok) throw new Error("Failed to deploy")
            console.log("Deployed successfully!", response)
        } catch (error) {
            console.error(error)
        }
    }


    return (
        <div className="w-full flex flex-row">
            <div className="w-1/2 p-12 overflow-hidden h-[100vh]">
                <h1 className="font-semibold text-xl pb-2">🤖 Community Agents</h1>
                <div className="flex flex-1 flex-col gap-2 overflow-y-auto">
                    {agent_sets.map((set) => (
                    <CommunityAgentCard
                        key={set.uuid}
                        name={set.name || "Placeholder Name"}
                        slug={set.uuid}
                    />
                ))}</div>
            </div>
            <div className="w-1/2 flex flex-col p-12 h-[100vh] overflow-hidden bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50">
                <h1 className="font-semibold text-xl pb-2">Build a new Agents crew</h1>
                <div className="flex-1 overflow-y-auto pr-2 box-border space-y-6">
                    {agents.map((agent) => (
                        <div key={agent.id}>
                            <AgentCard
                                key={agent.id}
                                agent={agent}
                                onUpdate={(newConfig) => updateAgent(agent.id, newConfig)}
                                onDelete={() => deleteAgent(agent.id)}
                                tools={tools}
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
                        <div className="w-full flex flex-row justify-end">
                            <DeployConfirmationDialog
                                agents={agents}
                                onDeploy={deployAgents}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
