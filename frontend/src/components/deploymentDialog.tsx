import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { AgentConfig } from "@/types/agent";

interface DeployConfirmationDialogProps {
    agents: AgentConfig[];
    onDeploy: (systemName: string) => Promise<void>;
}

export default function DeployConfirmationDialog({
                                                     agents,
                                                     onDeploy
                                                 }: DeployConfirmationDialogProps) {
    const [systemName, setSystemName] = useState("");
    const [isDeploying, setIsDeploying] = useState(false);
    const [open, setOpen] = useState(false);

    const handleDeploy = async () => {
        if (!systemName.trim()) return;

        setIsDeploying(true);
        try {
            await onDeploy(systemName.trim());
            setOpen(false);
            setSystemName("");
        } catch (error) {
            console.error("Deployment failed:", error);
        } finally {
            setIsDeploying(false);
        }
    };

    const validAgentsCount = agents.filter(agent =>
        agent.name.trim() && agent.system_prompt.trim()
    ).length;

    const isDeployDisabled = validAgentsCount === 0 || !systemName.trim() || isDeploying;

    return (
        <AlertDialog open={open} onOpenChange={setOpen}>
            <AlertDialogTrigger asChild>
                <Button
                    className="mt-4 text-white text-lg font-semibold bg-gradient-to-r from-red-500 to-purple-500 hover:opacity-75"
                    size="lg"
                    disabled={validAgentsCount === 0}
                >
                    Deploy
                </Button>
            </AlertDialogTrigger>

            <AlertDialogContent className="max-w-md">
                <AlertDialogHeader>
                    <AlertDialogTitle>Deploy Agent System</AlertDialogTitle>
                    <AlertDialogDescription>
                        You're about to deploy {validAgentsCount} agent{validAgentsCount !== 1 ? 's' : ''} to production.
                        Please give your system a name to continue.
                    </AlertDialogDescription>
                </AlertDialogHeader>

                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="system-name">System Name</Label>
                        <Input
                            id="system-name"
                            placeholder="e.g., Customer Support Crew"
                            value={systemName}
                            onChange={(e) => setSystemName(e.target.value)}
                            disabled={isDeploying}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !isDeployDisabled) {
                                    handleDeploy();
                                }
                            }}
                        />
                    </div>

                    {/* Agent Summary */}
                    <div className="bg-gray-50 p-3 rounded-lg">
                        <h4 className="text-sm font-medium mb-2">Agents to deploy:</h4>
                        <div className="space-y-1">
                            {agents
                                .filter(agent => agent.name.trim() && agent.system_prompt.trim())
                                .map((agent, index) => (
                                    <div key={agent.id} className="text-sm text-gray-600">
                                        {index + 1}. {agent.name || `Agent ${agent.id}`}
                                    </div>
                                ))
                            }
                        </div>
                        {agents.some(agent => !agent.name.trim() || !agent.system_prompt.trim()) && (
                            <p className="text-xs text-orange-600 mt-2">
                                Note: Agents without names or system prompts will be skipped.
                            </p>
                        )}
                    </div>
                </div>

                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isDeploying}>
                        Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleDeploy}
                        disabled={isDeployDisabled}
                        className="bg-gradient-to-r from-red-500 to-purple-500 hover:opacity-75"
                    >
                        {isDeploying ? "Deploying..." : "Deploy System"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}