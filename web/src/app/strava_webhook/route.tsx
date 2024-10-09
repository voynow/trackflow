import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const mode = searchParams.get('hub.mode');
    const token = searchParams.get('hub.verify_token');
    const challenge = searchParams.get('hub.challenge');

    console.log(`Received GET request with mode: ${mode}, token: ${token}, and challenge: ${challenge}`);

    if (mode === 'subscribe' && token === process.env.STRAVA_VERIFY_TOKEN) {
        console.log('Subscription mode with valid verify token, sending challenge response.');
        return NextResponse.json({ 'hub.challenge': challenge });
    } else {
        console.error('Invalid verify token, returning 403 status.');
        return new NextResponse('Invalid verify token', { status: 403 });
    }
}

export async function POST(request: NextRequest) {
    const event = await request.json();
    console.log(`Received POST request with event: ${JSON.stringify(event)}`);

    // Respond immediately to Strava with 200 OK
    const immediateResponse = NextResponse.json({}, { status: 200 });

    (async () => {
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event),
            });

            if (response.ok) {
                console.log('Successful response from signup API');
            } else {
                const errorData = await response.json();
                console.log(`Error response from signup API: ${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error(`Error occurred while processing POST request: ${error}`);
        }
    })();

    return immediateResponse;
}
