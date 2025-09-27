import { useState } from "react";
import { createPortal } from "react-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Copy, Code, X, Check } from "lucide-react";

interface IframeExportButtonProps {
    slug: string;
    baseUrl?: string;
}

export default function IframeExportButton({ slug, baseUrl = "https://your-domain.com" }: IframeExportButtonProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [width, setWidth] = useState("400");
    const [height, setHeight] = useState("600");
    const [copied, setCopied] = useState(false);

    const iframeUrl = `${baseUrl}/chat/${slug}`;

    const iframeCode = `<iframe
  src="${iframeUrl}"
  width="${width}"
  height="${height}"
  frameborder="0"
  allow="microphone; camera"
  style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
  title="AI Chat Assistant">
</iframe>`;

    const embedScript = `<!-- AI Chat Widget -->
<div id="ai-chat-widget"></div>
<script>
  (function() {
    var iframe = document.createElement('iframe');
    iframe.src = '${iframeUrl}';
    iframe.width = '${width}';
    iframe.height = '${height}';
    iframe.frameBorder = '0';
    iframe.allow = 'microphone; camera';
    iframe.style.cssText = 'border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);';
    iframe.title = 'AI Chat Assistant';
    document.getElementById('ai-chat-widget').appendChild(iframe);
  })();
</script>`;

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    return (
        <>
            <Button
                onClick={() => setIsOpen(true)}
                variant="outline"
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
                <Code className="w-4 h-4 mr-2" />
                Export Iframe
            </Button>

            {isOpen && typeof window !== 'undefined' && createPortal(
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
                    <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <CardTitle>Export Chat as Iframe</CardTitle>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsOpen(false)}
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        </CardHeader>

                        <CardContent className="space-y-6">
                            {/* Preview */}
                            <div>
                                <h3 className="text-sm font-medium mb-2">Preview</h3>
                                <div className="border rounded-lg p-4 bg-gray-50 flex justify-center">
                                    <iframe
                                        src={iframeUrl}
                                        width={Math.min(parseInt(width), 300)}
                                        height={Math.min(parseInt(height), 200)}
                                        frameBorder="0"
                                        className="rounded border shadow-sm"
                                        title="Chat Preview"
                                    />
                                </div>
                            </div>

                            {/* Dimensions */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium mb-1 block">Width (px)</label>
                                    <Input
                                        type="number"
                                        value={width}
                                        onChange={(e) => setWidth(e.target.value)}
                                        placeholder="400"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm font-medium mb-1 block">Height (px)</label>
                                    <Input
                                        type="number"
                                        value={height}
                                        onChange={(e) => setHeight(e.target.value)}
                                        placeholder="600"
                                    />
                                </div>
                            </div>

                            {/* Direct URL */}
                            <div>
                                <h3 className="text-sm font-medium mb-2">Direct URL</h3>
                                <div className="flex gap-2">
                                    <Input
                                        value={iframeUrl}
                                        readOnly
                                        className="font-mono text-sm"
                                    />
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => copyToClipboard(iframeUrl)}
                                    >
                                        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </Button>
                                </div>
                            </div>

                            {/* HTML Iframe Code */}
                            <div>
                                <h3 className="text-sm font-medium mb-2">HTML Iframe Code</h3>
                                <div className="relative">
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                    <code>{iframeCode}</code>
                  </pre>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700"
                                        onClick={() => copyToClipboard(iframeCode)}
                                    >
                                        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </Button>
                                </div>
                            </div>

                            {/* JavaScript Embed */}
                            <div>
                                <h3 className="text-sm font-medium mb-2">JavaScript Embed</h3>
                                <p className="text-xs text-gray-600 mb-2">
                                    Use this if you need to dynamically load the chat widget
                                </p>
                                <div className="relative">
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                    <code>{embedScript}</code>
                  </pre>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700"
                                        onClick={() => copyToClipboard(embedScript)}
                                    >
                                        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </Button>
                                </div>
                            </div>

                            {/* Usage Instructions */}
                            <div className="bg-blue-50 p-4 rounded-lg">
                                <h4 className="font-medium text-blue-900 mb-2">How to Use</h4>
                                <ul className="text-sm text-blue-800 space-y-1">
                                    <li>1. Copy the HTML iframe code above</li>
                                    <li>2. Paste it into your website's HTML</li>
                                    <li>3. Adjust width/height as needed</li>
                                    <li>4. The chat will load automatically</li>
                                </ul>
                            </div>

                            {/* Security Note */}
                            <div className="bg-yellow-50 p-4 rounded-lg">
                                <h4 className="font-medium text-yellow-900 mb-2">Security Note</h4>
                                <p className="text-sm text-yellow-800">
                                    Make sure to update the baseUrl prop to match your actual domain.
                                    Consider implementing iframe security measures like Content Security Policy (CSP) headers.
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </div>,
                document.body
            )}
        </>
    );
}