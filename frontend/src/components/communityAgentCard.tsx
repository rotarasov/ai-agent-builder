import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import {Card, CardAction, CardHeader, CardTitle} from '@/components/ui/card'


interface CommunityAgentCardProps {
    name: string,
    slug: string
}


export default function CommunityAgentCard(props: CommunityAgentCardProps) {
    const router = useRouter()

    const handleClick = () => {
        router.push(`/chat/${props.slug}?name=${props.name}`)
    }

    return (
        <div>
            <Card>
                <CardHeader className="h-full flex items-center justify-between">
                    <CardTitle>{props.name}</CardTitle>
                    <CardAction>
                        <div>
                            <Button
                                className="text-white font-semibold bg-linear-65 from-violet-500 to-purple-500 hover:opacity-75"
                                variant="default"
                                onClick={handleClick}
                            >
                                Chat Now
                            </Button>
                        </div>
                    </CardAction>
                </CardHeader>
            </Card>
        </div>
    )
}