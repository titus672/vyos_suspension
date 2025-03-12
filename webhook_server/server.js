const express = require('express');
const bodyParser = require('body-parser');
const { NodeSSH } = require('node-ssh');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;
const HOST = '0.0.0.0';
const LOG_FILE = '/var/log/ucrm_suspension_webhook.log';
const ROUTERS_FILE = path.join(__dirname, 'config', 'routers.json');

app.use(bodyParser.json());

const ssh = new NodeSSH();

// Function to log messages
function logMessage(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    console.log(logEntry.trim());

    fs.appendFile(LOG_FILE, logEntry, (err) => {
        if (err) console.error('Failed to write log:', err);
    });
}

// Load router list
function loadRouters() {
    if (!fs.existsSync(ROUTERS_FILE)) {
        logMessage('Error: Router list file not found!');
        return [];
    }
    try {
        const data = fs.readFileSync(ROUTERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        logMessage('Error reading router list: ' + err);
        return [];
    }
}

// Function to execute SSH command
async function executeSSH(ip, username, password) {
    try {
        await ssh.connect({ host: ip, username, password });
        const result = await ssh.execCommand('/config/scripts/suspension.sh');
        logMessage(`Suspension executed on ${ip}. Output: ${result.stdout}`);
        ssh.dispose();
    } catch (err) {
        logMessage(`SSH to ${ip} failed: ${err}`);
    }
}

// Webhook endpoint
app.post('/suspend_test', async (req, res) => {
    logMessage(`Received webhook: ${JSON.stringify(req.body)}`);

    const routers = loadRouters();
    if (routers.length === 0) {
        logMessage('No routers found, skipping suspension process.');
        return res.status(500).send('No routers configured');
    }

    for (const router of routers) {
        await executeSSH(router.ip, router.username, router.password);
    }

    res.status(200).send('Webhook processed');
});

app.listen(PORT, HOST, () => {
    logMessage(`Server running at http://${HOST}:${PORT}/`);
});
