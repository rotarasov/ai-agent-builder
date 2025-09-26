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
import { toast } from "sonner"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"

const FormSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().min(1, "Description is required"),
    model: z.string({ message: "Please select a model" }),
    toolkit: z.string().optional(),
})

export default function AgentCard() {
    const [isOpen, setIsOpen] = useState(true)

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: "",
            description: "",
            model: "",
            toolkit: "",
        },
    })

    function onSubmit(data: z.infer<typeof FormSchema>) {
        toast("Agent saved", {
            description: (
                <pre className="mt-2 w-[320px] rounded-md bg-neutral-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
            ),
        })
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

                        <h2 className="font-semibold">Configuration</h2>
                        <div className="flex flex-row gap-2">
                            <FormField
                                control={form.control}
                                name="model"
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
                                                <SelectItem value="gpt-4">GPT-4</SelectItem>
                                                <SelectItem value="gpt-3.5">GPT-3.5</SelectItem>
                                                <SelectItem value="custom">Custom</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="toolkit"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Tools (optional)</FormLabel>
                                        <Select
                                            onValueChange={field.onChange}
                                            defaultValue={field.value}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select a Tool for this Agent" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="Gmail">Gmail</SelectItem>
                                                <SelectItem value="Notion">Notion</SelectItem>
                                                <SelectItem value="Slack">Slack</SelectItem>
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
