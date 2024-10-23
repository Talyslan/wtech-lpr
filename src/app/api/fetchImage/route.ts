// app/api/fetchImage/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const imageURL = "http://192.168.0.11/Snapshot/1/RemoteImageCapture?ImageFormat=2"
  // const streamURL = "http://192.168.0.11/Streams/1/4/ReceiveData"
  const response = await fetch(imageURL, {
    method: 'GET',
    headers: {
      Authorization: 'Basic ' + btoa('admin:Admin123'),
    },
  });

  if (!response.ok) {
    return NextResponse.json({ message: 'Erro ao capturar imagem' }, { status: 500 });
  }

  const imageBlob = await response.blob();
  return new Response(imageBlob, {
    headers: {
      'Content-Type': 'image/jpeg',
    },
  });
}
