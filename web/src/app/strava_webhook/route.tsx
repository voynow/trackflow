import AWS from 'aws-sdk';
import { NextRequest, NextResponse } from 'next/server';

const sqs = new AWS.SQS({ region: 'us-east-1' });

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

    const params = {
        QueueUrl: 'https://sqs.us-east-1.amazonaws.com/498969721544/trackflow-webhook-msg-queue',
        MessageBody: JSON.stringify(event),
    };

    try {
        const data = await sqs.sendMessage(params).promise();
        console.log(`Message sent to SQS with ID: ${data.MessageId}`);
    } catch (err) {
        console.error(`Error sending message to SQS: ${err}`);
    }

    return NextResponse.json({}, { status: 200 });
}
