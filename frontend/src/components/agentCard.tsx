"use client"
import React, { useState } from "react"
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter,
    CardAction,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import {
    AlertDialog, AlertDialogAction, AlertDialogCancel,
    AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger
} from "@/components/ui/alert-dialog";
import {AgentConfig} from "@/types/agent";




const FormSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().min(1, "Description is required"),
    system_prompt: z.string().min(1, "Instruction is required"),
    model_name: z.string({ message: "Please select a model" }),
    tools: z.string().optional(),
})

type AgentCardProps = {
    agent: AgentConfig
    onUpdate: (newConfig: Partial<AgentConfig>) => void
    onDelete: () => void
    tools: string[]
}

export default function AgentCard({ agent, onUpdate, onDelete, tools }: AgentCardProps) {
    const [isOpen, setIsOpen] = useState(true)

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: "",
            description: "",
            model_name: "",
            tools: "",
        },
    })

    function onSubmit(data: z.infer<typeof FormSchema>) {
        onUpdate(data)
        setIsOpen(false) // collapse after save
    }


    if (!isOpen) {
        // 🔹 Closed State
        return (
            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>{form.getValues("name") || "Unnamed Agent"}</CardTitle>
                    </div>
                    <CardAction>
                        <Button variant="destructive" onClick={() => setIsOpen(true)}>Edit</Button>
                    </CardAction>
                </CardHeader>
            </Card>
        )
    }

    // 🔹 Open State
    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
                <Card>
                    <CardHeader>
                        <CardTitle>Define a new Agent</CardTitle>
                        <CardDescription>
                            Fill in the details to configure your agent
                        </CardDescription>
                        <CardAction>
                            {/* 🔹 Delete with confirmation */}
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button className="text-lg" variant="ghost" type="button">
                                        🗑️
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>
                                            Delete this agent?
                                        </AlertDialogTitle>
                                        <AlertDialogDescription>
                                            This action cannot be undone. The agent and its
                                            configuration will be permanently removed.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction
                                            className="bg-red-600 hover:bg-red-700"
                                            onClick={onDelete}
                                        >
                                            Delete
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                            <Button type="submit">Save</Button>
                        </CardAction>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Name</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Name your Agent" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Describe what this Agent should do"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="system_prompt"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Instructions (optional)</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Give this Agent specific instructions"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <h2 className="font-semibold">Configuration</h2>
                        <div className="flex flex-row gap-2">
                            <FormField
                                control={form.control}
                                name="model_name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Model</FormLabel>
                                        <Select
                                            onValueChange={field.onChange}
                                            defaultValue={field.value}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select a model" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="swiss-ai/Apertus-70B">swiss-ai/Apertus-70B</SelectItem>
                                                <SelectItem value="gpt-5-nano">gpt-5-nano</SelectItem>
                                                <SelectItem value="gpt-5">gpt-5</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="tools"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Tools (optional)</FormLabel>
                                        <Select
                                            onValueChange={field.onChange}
                                            defaultValue= ""
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select a Tool for this Agent" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {tools.map((tool: string) => (
                                                    <SelectItem key={tool} value={tool}>
                                                        {tool}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </CardContent>

                    <CardFooter />
                </Card>
            </form>
        </Form>
    )
}
