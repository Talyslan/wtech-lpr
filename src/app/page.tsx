'use client'

import { useState } from 'react';
import { processPlateRecognition } from './imgURL';
import { captureImage } from './imgURL';
import Image from 'next/image';

export default function LPRSystem() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  const handleCapture = async () => {
    console.log("fui clicado, mas perai")
    const capturedImage = await captureImage(); // Função que captura a imagem
    console.log("mais q clicado")
    setImageUrl(capturedImage);

    const plateRecognition = await processPlateRecognition(capturedImage);
    setResult(plateRecognition ? 'Placa encontrada' : 'Placa não encontrada');
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Sistema LPR</h1>
      <button
        onClick={handleCapture}
        className="bg-blue-500 text-white p-2 rounded"
      >
        Capturar Imagem
      </button>

      {imageUrl && (
        <div className="mt-4">
          <Image
            src={imageUrl}
            alt='Captura da Câmera'
            className='2-64 h-64'
            width='500'
            height='200'
          />
        </div>
      )}

      {result && (
        <div className="mt-4 text-lg">
          <p>Resultado: {result}</p>
        </div>
      )}
    </div>
  );
}
