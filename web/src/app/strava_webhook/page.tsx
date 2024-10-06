import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {

    if (req.method === 'GET') {
        const mode = req.query['hub.mode'];
        const token = req.query['hub.verify_token'];
        const challenge = req.query['hub.challenge'];

        if (mode === 'subscribe') {
            res.status(200).json({ 'hub.challenge': challenge });
        } else {
            res.status(403).json({ error: 'Invalid verify token' });
        }
    } else if (req.method === 'POST') {
        const event = req.body;
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/webhook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event),
            });
            if (response.ok) {
                res.status(200).json({ success: true });
            } else {
                const errorData = await response.json();
                res.status(500).json({ success: false, error: errorData });
            }
        } catch (error) {
            res.status(500).json({ success: false, error: 'Internal server error' });
        }
    } else {
        res.status(405).json({ success: false, error: 'Method Not Allowed' });
    }
}
