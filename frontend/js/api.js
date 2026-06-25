class FraudAPI {
    static async getStats() {
        const response = await fetch('/api/stats');
        return response.json();
    }

    static async getTransactions() {
        const response = await fetch('/api/transactions');
        return response.json();
    }

    static async predictFraud(transactionData) {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transactionData)
        });
        return response.json();
    }
}
