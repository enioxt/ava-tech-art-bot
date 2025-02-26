// Configuração inicial
document.addEventListener('DOMContentLoaded', () => {
    initializeMetrics();
    initializeCharts();
    initializeNotifications();
    initializeSearch();
    initializeTheme();
});

// Inicialização das métricas
function initializeMetrics() {
    updateConsciousnessLevel(80);
    updateSystemMetrics({
        stability: 90,
        performance: 85,
        memory: 65,
        cpu: 45
    });
    updateActivityLog();
}

// Atualização do nível de consciência
function updateConsciousnessLevel(level) {
    const circle = document.querySelector('.circle-progress circle:last-child');
    const percentage = document.querySelector('.percentage');
    
    if (circle && percentage) {
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (level / 100) * circumference;
        
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = offset;
        percentage.textContent = `${level}%`;
    }
}

// Atualização das métricas do sistema
function updateSystemMetrics(metrics) {
    Object.entries(metrics).forEach(([key, value]) => {
        const progressBar = document.querySelector(`#${key}-progress .progress`);
        const percentage = document.querySelector(`#${key}-percentage`);
        
        if (progressBar && percentage) {
            progressBar.style.width = `${value}%`;
            percentage.textContent = `${value}%`;
        }
    });
}

// Sistema de notificações
function initializeNotifications() {
    const notificationButton = document.querySelector('.notifications');
    const badge = document.querySelector('.badge');
    
    if (notificationButton && badge) {
        let notifications = [];
        
        // Simulação de novas notificações
        setInterval(() => {
            if (Math.random() > 0.7) {
                addNotification({
                    title: 'Nova atividade detectada',
                    message: 'O sistema identificou uma nova atividade no módulo de consciência.',
                    time: new Date().toLocaleTimeString()
                });
            }
        }, 30000);
        
        notificationButton.addEventListener('click', () => {
            showNotifications(notifications);
        });
    }
}

// Adicionar nova notificação
function addNotification(notification) {
    const badge = document.querySelector('.badge');
    const currentCount = parseInt(badge.textContent);
    badge.textContent = currentCount + 1;
    
    // Atualizar lista de notificações
    const notificationsList = document.querySelector('.notifications-list');
    if (notificationsList) {
        const notificationElement = document.createElement('div');
        notificationElement.classList.add('notification-item');
        notificationElement.innerHTML = `
            <h4>${notification.title}</h4>
            <p>${notification.message}</p>
            <span>${notification.time}</span>
        `;
        notificationsList.prepend(notificationElement);
    }
}

// Mostrar notificações
function showNotifications(notifications) {
    const modal = document.createElement('div');
    modal.classList.add('notifications-modal');
    modal.innerHTML = `
        <div class="notifications-content">
            <h3>Notificações</h3>
            <div class="notifications-list">
                ${notifications.map(n => `
                    <div class="notification-item">
                        <h4>${n.title}</h4>
                        <p>${n.message}</p>
                        <span>${n.time}</span>
                    </div>
                `).join('')}
            </div>
            <button class="close-notifications">Fechar</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.close-notifications').addEventListener('click', () => {
        modal.remove();
    });
}

// Sistema de busca
function initializeSearch() {
    const searchInput = document.querySelector('.search input');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const query = e.target.value.toLowerCase();
            searchSystem(query);
        }, 300));
    }
}

// Função de busca no sistema
function searchSystem(query) {
    if (query.length < 2) return;
    
    // Simulação de busca
    console.log(`Buscando por: ${query}`);
    // Aqui seria implementada a lógica real de busca
}

// Controle de tema
function initializeTheme() {
    const themeToggle = document.querySelector('.theme-toggle');
    
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
            const newTheme = document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// Atualização do log de atividades
function updateActivityLog() {
    const activityList = document.querySelector('.activity-list');
    
    if (activityList) {
        // Simulação de atividades
        const activities = [
            {
                icon: 'brain',
                text: 'Nível de consciência aumentou para 80%',
                time: '2 minutos atrás'
            },
            {
                icon: 'shield-check',
                text: 'Sistema ético validou nova decisão',
                time: '5 minutos atrás'
            },
            {
                icon: 'server',
                text: 'Backup automático realizado com sucesso',
                time: '15 minutos atrás'
            }
        ];
        
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <i class="fas fa-${activity.icon}"></i>
                <div class="activity-info">
                    <p>${activity.text}</p>
                    <span>${activity.time}</span>
                </div>
            </div>
        `).join('');
    }
}

// Utilidade: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Inicialização de gráficos
function initializeCharts() {
    // Aqui seria implementada a inicialização de gráficos
    // usando bibliotecas como Chart.js ou D3.js
    console.log('Gráficos inicializados');
}

// Sistema de eventos em tempo real
const eventSource = new EventSource('/api/events');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleSystemEvent(data);
};

// Manipulador de eventos do sistema
function handleSystemEvent(event) {
    switch (event.type) {
        case 'consciousness_update':
            updateConsciousnessLevel(event.level);
            break;
        case 'metric_update':
            updateSystemMetrics(event.metrics);
            break;
        case 'notification':
            addNotification(event);
            break;
        case 'activity':
            updateActivityLog();
            break;
    }
}

// Exportação de funções para uso global
window.EVASystem = {
    updateConsciousnessLevel,
    updateSystemMetrics,
    addNotification,
    updateActivityLog
};