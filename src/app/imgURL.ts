export const captureImage = async () => {
    const response = await fetch('/api/fetchImage');
    
    if (!response.ok) {
      throw new Error('Erro ao capturar imagem');
    }
  
    const imageBlob = await response.blob();
    const imageUrl = URL.createObjectURL(imageBlob);
    console.log('img url: ', imageUrl)
    return imageUrl;
  };
  
  

  import Tesseract from 'tesseract.js';

const recognizePlate = async (imageUrl: string) => {
  const result = await Tesseract.recognize(imageUrl, 'eng')
//   , {
//     logger: (info) => console.log(info),
//   });
  const plateText = result.data.text.trim();
  console.log('plateText: ', plateText)
  return plateText;
};

const platesDatabase = ['ABC1234', 'XYZ5678', 'LMN9123', 'RIO2A18']; // Placas válidas

const checkPlateInDatabase = (plate: string) => {
    return platesDatabase.includes(plate);
  };
  
  // Exemplo de uso:
  export const processPlateRecognition = async (imageUrl: string) => {
    const recognizedPlate = await recognizePlate(imageUrl);
    const isPlateInDatabase = checkPlateInDatabase(recognizedPlate);
  
    if (isPlateInDatabase) {
      console.log('Placa reconhecida no banco de dados: ', recognizedPlate);
      return true;
    } else {
      console.log('Placa não encontrada no banco de dados');
      return false;
    }
  };
  