// web/src/app/strava_webhook/route.tsx
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

    try {
        const response = await fetch('http://trackflow-alb-499532887.us-east-1.elb.amazonaws.com/strava-webhook/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event),
        });

        if (!response.ok) {
            console.error(`Error sending event to FastAPI: ${response.statusText}`);
            return new NextResponse(`Error sending event to FastAPI: ${response.statusText}`, { status: 500 });
        }

        console.log(`Event successfully sent to FastAPI.`);
    } catch (err) {
        console.error(`Error sending event to FastAPI: ${err}`);
        return new NextResponse(`Error: ${err}`, { status: 500 });
    }

    // Immediate response to Strava
    return NextResponse.json({}, { status: 200 });
}
