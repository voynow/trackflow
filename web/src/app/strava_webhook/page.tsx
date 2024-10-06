import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
    const searchParams = req.nextUrl.searchParams;
    const mode = searchParams.get('hub.mode');
    const token = searchParams.get('hub.verify_token');
    const challenge = searchParams.get('hub.challenge');

    if (mode === 'subscribe') {
        return NextResponse.json({ 'hub.challenge': challenge });
    } else {
        return NextResponse.json({ error: 'Invalid verify token' }, { status: 403 });
    }
}

export async function POST(req: NextRequest) {
    const event = await req.json();
    try {
        const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/webhook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event),
        });
        if (response.ok) {
            return NextResponse.json({ success: true });
        } else {
            const errorData = await response.json();
            return NextResponse.json({ success: false, error: errorData }, { status: 500 });
        }
    } catch (error) {
        return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
    }
}
