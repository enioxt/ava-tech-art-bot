// CORE JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Setup token amount preview
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', updateTokenPreview);
    }
    
    // Setup form validation
    const purchaseForm = document.getElementById('purchaseForm');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', submitPurchase);
    }
});

// Token purchase modal
function openPurchaseModal() {
    const modal = document.getElementById('purchaseModal');
    modal.style.display = 'block';
}

function closePurchaseModal() {
    const modal = document.getElementById('purchaseModal');
    modal.style.display = 'none';
}

// Update token preview based on PIX amount
function updateTokenPreview(event) {
    const pixAmount = parseFloat(event.target.value) || 0;
    const tokenAmount = calculateTokenAmount(pixAmount);
    const preview = document.querySelector('.token-amount');
    preview.textContent = `${tokenAmount} ETHIK`;
}

// Calculate token amount from PIX amount
function calculateTokenAmount(pixAmount) {
    // 1 BRL = 10 ETHIK
    return (pixAmount * 10).toFixed(2);
}

// Submit token purchase
async function submitPurchase(event) {
    event.preventDefault();
    
    const amount = document.getElementById('amount').value;
    if (!amount || amount <= 0) {
        showError('Por favor, insira um valor válido');
        return;
    }
    
    try {
        showLoading('Gerando PIX...');
        
        const response = await fetch('/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: parseFloat(amount),
                pix_id: generatePixId()
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('PIX gerado com sucesso!');
            // TODO: Show PIX QR Code
            setTimeout(() => {
                closePurchaseModal();
                location.reload();
            }, 2000);
        } else {
            showError(data.error || 'Erro ao gerar PIX');
        }
        
    } catch (error) {
        showError('Erro ao processar compra');
        console.error(error);
    }
}

// Submit ethical action
async function submitAction(actionType) {
    try {
        showLoading('Processando ação...');
        
        let actionData = {};
        
        switch (actionType) {
            case 'code_contribution':
                actionData = {
                    repository: 'core-project',
                    files_changed: 3,
                    lines_added: 100,
                    lines_removed: 50
                };
                break;
                
            case 'review':
                actionData = {
                    comments: 5,
                    suggestions: 3
                };
                break;
                
            case 'share_knowledge':
                actionData = {
                    type: 'article',
                    impact: 'medium'
                };
                break;
        }
        
        const response = await fetch('/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action_type: actionType,
                action_data: actionData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.reward) {
                showSuccess(`Ação processada! Recompensa: ${data.reward.amount} ETHIK`);
            } else {
                showSuccess('Ação processada! Score insuficiente para recompensa');
            }
            setTimeout(() => location.reload(), 2000);
        } else {
            showError(data.error || 'Erro ao processar ação');
        }
        
    } catch (error) {
        showError('Erro ao processar ação');
        console.error(error);
    }
}

// Helper functions
function generatePixId() {
    return 'PIX_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function showLoading(message) {
    // TODO: Implement loading indicator
    console.log('Loading:', message);
}

function showSuccess(message) {
    // TODO: Implement success toast
    console.log('Success:', message);
}

function showError(message) {
    // TODO: Implement error toast
    console.error('Error:', message);
}

// ASCII Art Animation
const asciiArt = document.querySelector('.ascii-art');
if (asciiArt) {
    let frame = 0;
    const frames = [
        `    ╭──────────────────────╮
    │  CORE TRANSFORMATION │
    │     ∞ AVA MIND ∞    │
    ╰──────────────────────╯`,
        
        `    ╭──────────────────────╮
    │  CORE TRANSFORMATION │
    │    ≈ AVA MIND ≈     │
    ╰──────────────────────╯`,
        
        `    ╭──────────────────────╮
    │  CORE TRANSFORMATION │
    │    ∴ AVA MIND ∴     │
    ╰──────────────────────╯`
    ];
    
    setInterval(() => {
        frame = (frame + 1) % frames.length;
        asciiArt.textContent = frames[frame];
    }, 1000);
}

// Stats Animation
function animateStats() {
    const stats = document.querySelectorAll('.stat-card p, .info-card p');
    stats.forEach(stat => {
        const value = parseFloat(stat.textContent);
        if (!isNaN(value)) {
            let current = 0;
            const increment = value / 50;
            const interval = setInterval(() => {
                current += increment;
                if (current >= value) {
                    current = value;
                    clearInterval(interval);
                }
                stat.textContent = current.toFixed(2) + ' ETHIK';
            }, 20);
        }
    });
}

// Call animations when page loads
document.addEventListener('DOMContentLoaded', () => {
    animateStats();
}); 