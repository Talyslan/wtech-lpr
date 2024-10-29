import axios from 'axios';

export async function GET() {
  try {
    const response = await axios.get('http://localhost:5000/capture', { responseType: 'arraybuffer' });

    if (response.status !== 200) {
      return new Response(
        JSON.stringify({ error: `Failed to fetch image | Status: ${response.statusText}` }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const imageBuffer = Buffer.from(response.data, 'binary');

    return new Response(imageBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'image/jpeg',
      },
    });
  } catch (error) {
    return new Response(
      JSON.stringify({ error: `Failed to capture image | ${error}` }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
