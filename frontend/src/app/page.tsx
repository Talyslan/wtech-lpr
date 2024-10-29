'use client';

import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import NextImage from 'next/image';

const Home = () => {
  const [plate, setPlate] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState<boolean>(true);
  const time = 5000;
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (isCapturing) {
      intervalIdRef.current = setInterval(async () => {
        try {
          const response = await axios.get('/api/capture', { responseType: 'arraybuffer' });
          const imageBlob = new Blob([response.data], { type: 'image/jpeg' });
          const newImageUrl = URL.createObjectURL(imageBlob);
          setImageUrl(newImageUrl);
          const formData = new FormData();
          formData.append('image', imageBlob, 'image.jpg'); // 'image.jpg' é apenas um nome de arquivo

          // Adicionar aqui a lógica para enviar a imagem ao backend para reconhecimento
          const plateResponse = await axios.post('http://localhost:5000/recognize', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
          if (plateResponse.data && plateResponse.data.plate) {
            setPlate(plateResponse.data.plate);
          }

        } catch (error) {
          console.error('Error capturing image:', error);
          setError('Erro ao capturar a imagem');
        }
      }, time);
    } else {
      setImageUrl(null);
    }

    return () => {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
      }
    };
  }, [isCapturing]);

  const toggleCapturing = () => {
    setIsCapturing(prev => !prev);
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
    }
  };

  return (
    <div>
      <h1>Reconhecimento de Placa Veicular</h1>
      {imageUrl ? (
        <NextImage src={imageUrl} alt="Imagem da Placa" width={500} height={300} />
      ) : (
        <h2>A captura foi pausada, clique para retomar!</h2>
      )}
      
      <button onClick={toggleCapturing} style={{ marginTop: '20px' }}>
        {isCapturing ? 'Parar Captura' : 'Retomar Captura'}
      </button>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <div>
        <p>{plate}</p>
      </div>
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};

export default Home;
