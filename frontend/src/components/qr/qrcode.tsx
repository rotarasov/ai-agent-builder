"use client";

import { useQRCode } from "next-qrcode";


type QRProps = {
    data: string;
};

export default function QRCode({data}: QRProps) {
    const { Canvas } = useQRCode();

    return (
        <div className="flex flex-col items-center justify-center space-y-4">
            <Canvas
                text={data}
                options={{
                    errorCorrectionLevel: "M",
                    margin: 3,
                    scale: 4,
                    width: 200,
                    color: {
                        dark: "#000000",
                        light: "#FFFFFF",
                    },
                }}
            />
        </div>
    );
}
