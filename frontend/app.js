/**
 * Sentiment Analyzer - Frontend Logic v2.0
 * Soporta clasificación de rubros e historial
 */

// ============== Configuración ==============
const API_BASE_URL = 'http://localhost:8000';
let historyData = [];
let currentBusiness = null;
let currentCategory = 'all';
let sentimentChart = null;
let comparisonChart = null;

// ============== Inicialización ==============
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await loadHistory();
    setupEventListeners();
    updateCategoryCounts();
}

// ============== Carga de Datos ==============
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        if (response.ok) {
            const data = await response.json();
            historyData = data.businesses || [];
        } else {
            throw new Error('Backend no disponible');
        }
    } catch (error) {
        console.log('Usando datos locales:', error.message);
        // Cargar datos mock si backend no disponible
        try {
            const mockResponse = await fetch(`${API_BASE_URL}/mock-analysis`);
            if (mockResponse.ok) {
                const mockData = await mockResponse.json();
                historyData = mockData.businesses || [];
            }
        } catch {
            historyData = [];
        }
    }

    populateBusinessSelect();
    renderCategoryChart();
}

function populateBusinessSelect() {
    const select = document.getElementById('businessSelect');
    const filtered = currentCategory === 'all'
        ? historyData
        : historyData.filter(b => b.category?.category_id === currentCategory);

    select.innerHTML = '<option value="">-- Selecciona un negocio --</option>' +
        filtered.map((business, index) => {
            const icon = business.category?.icon || '📍';
            return `<option value="${index}">${icon} ${business.name}</option>`;
        }).join('');
}

function updateCategoryCounts() {
    const counts = {
        all: historyData.length,
        salud: 0,
        gastronomia: 0,
        hospedaje: 0,
        retail: 0,
        educacion: 0
    };

    historyData.forEach(b => {
        const catId = b.category?.category_id;
        if (catId && counts[catId] !== undefined) {
            counts[catId]++;
        }
    });

    document.getElementById('countAll').textContent = counts.all;
    document.getElementById('countSalud').textContent = counts.salud;
    document.getElementById('countGastronomia').textContent = counts.gastronomia;
    document.getElementById('countHospedaje').textContent = counts.hospedaje;
    document.getElementById('countRetail').textContent = counts.retail;
    document.getElementById('countEducacion').textContent = counts.educacion;
}

// ============== Event Listeners ==============
function setupEventListeners() {
    // Analizar URL
    document.getElementById('analyzeUrlBtn').addEventListener('click', analyzeUrl);
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeUrl();
    });

    // Seleccionar negocio
    document.getElementById('businessSelect').addEventListener('change', (e) => {
        const index = parseInt(e.target.value);
        if (!isNaN(index)) {
            const filtered = currentCategory === 'all'
                ? historyData
                : historyData.filter(b => b.category?.category_id === currentCategory);
            selectBusiness(filtered[index]);
        }
    });

    // Refresh
    document.getElementById('refreshBtn').addEventListener('click', loadHistory);

    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategory = e.currentTarget.dataset.category;
            populateBusinessSelect();
            filterByCategory(currentCategory);
        });
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filterReviews(e.target.dataset.filter);
        });
    });
}

// ============== Analizar URL ==============
async function analyzeUrl() {
    const urlInput = document.getElementById('urlInput');
    const nameInput = document.getElementById('businessNameInput');
    const url = urlInput.value.trim();

    if (!url) {
        alert('Por favor ingresa una URL de Google Maps');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                business_name: nameInput.value.trim() || null
            })
        });

        if (response.ok) {
            const result = await response.json();
            historyData.push(result);
            updateCategoryCounts();
            populateBusinessSelect();
            selectBusiness(result);

            // Limpiar inputs
            urlInput.value = '';
            nameInput.value = '';

            // Mostrar notificación
            showToast(`✅ ${result.name} analizado (${result.category?.category_name})`);
        } else {
            throw new Error('Error al analizar');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al analizar la URL. Verifica que el backend esté corriendo.');
    } finally {
        showLoading(false);
    }
}

// ============== Selección de Negocio ==============
function selectBusiness(business) {
    currentBusiness = business;
    updateStats();
    updateBotStats();
    renderSentimentChart();
    renderReviews(currentBusiness.reviews || []);
}

function filterByCategory(categoryId) {
    const filtered = categoryId === 'all'
        ? historyData
        : historyData.filter(b => b.category?.category_id === categoryId);

    if (filtered.length > 0) {
        // Mostrar estadísticas agregadas del rubro
        const aggregated = aggregateStats(filtered);
        updateStatsFromAggregated(aggregated);
        renderCategoryChart();
    }
}

function aggregateStats(businesses) {
    const result = {
        total_reviews: 0,
        sentiment: { positive: 0, neutral: 0, negative: 0 },
        bots: { real: 0, suspicious: 0, bot: 0 },
        reviews: []
    };

    businesses.forEach(b => {
        result.total_reviews += b.total_reviews || 0;
        result.sentiment.positive += b.sentiment_summary?.positive || 0;
        result.sentiment.neutral += b.sentiment_summary?.neutral || 0;
        result.sentiment.negative += b.sentiment_summary?.negative || 0;
        result.bots.real += b.bot_stats?.real || 0;
        result.bots.suspicious += b.bot_stats?.suspicious || 0;
        result.bots.bot += b.bot_stats?.bot || 0;
        result.reviews = result.reviews.concat(b.reviews || []);
    });

    return result;
}

function updateStatsFromAggregated(stats) {
    animateNumber('totalReviews', stats.total_reviews);
    animateNumber('positiveCount', stats.sentiment.positive);
    animateNumber('neutralCount', stats.sentiment.neutral);
    animateNumber('negativeCount', stats.sentiment.negative);

    animateNumber('realCount', stats.bots.real);
    animateNumber('suspiciousCount', stats.bots.suspicious);
    animateNumber('botCount', stats.bots.bot);

    const total = stats.total_reviews || 1;
    document.getElementById('realPercentage').textContent = `${Math.round((stats.bots.real / total) * 100)}%`;
    document.getElementById('suspiciousPercentage').textContent = `${Math.round((stats.bots.suspicious / total) * 100)}%`;
    document.getElementById('botPercentage').textContent = `${Math.round((stats.bots.bot / total) * 100)}%`;

    renderReviews(stats.reviews);
}

function updateStats() {
    const { sentiment_summary, total_reviews } = currentBusiness;

    animateNumber('totalReviews', total_reviews || 0);
    animateNumber('positiveCount', sentiment_summary?.positive || 0);
    animateNumber('neutralCount', sentiment_summary?.neutral || 0);
    animateNumber('negativeCount', sentiment_summary?.negative || 0);
}

function updateBotStats() {
    const { bot_stats, total_reviews } = currentBusiness;
    const stats = bot_stats || { real: 0, suspicious: 0, bot: 0 };
    const total = total_reviews || 1;

    animateNumber('realCount', stats.real);
    animateNumber('suspiciousCount', stats.suspicious);
    animateNumber('botCount', stats.bot);

    document.getElementById('realPercentage').textContent = `${Math.round((stats.real / total) * 100)}%`;
    document.getElementById('suspiciousPercentage').textContent = `${Math.round((stats.suspicious / total) * 100)}%`;
    document.getElementById('botPercentage').textContent = `${Math.round((stats.bot / total) * 100)}%`;
}

function animateNumber(elementId, target) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const duration = 500;
    const start = parseInt(element.textContent) || 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.round(start + (target - start) * easeOutQuart(progress));
        element.textContent = current;

        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

function easeOutQuart(x) {
    return 1 - Math.pow(1 - x, 4);
}

// ============== Gráficos ==============
function renderSentimentChart() {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    const sentiment = currentBusiness?.sentiment_summary || { positive: 0, neutral: 0, negative: 0 };

    if (sentimentChart) sentimentChart.destroy();

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positivas', 'Neutrales', 'Negativas'],
            datasets: [{
                data: [sentiment.positive, sentiment.neutral, sentiment.negative],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderColor: 'transparent'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#475569', padding: 20 }
                }
            },
            cutout: '65%'
        }
    });
}

function renderCategoryChart() {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    if (comparisonChart) comparisonChart.destroy();

    // Agrupar por categoría
    const categories = {};
    historyData.forEach(b => {
        const catId = b.category?.category_id || 'otros';
        if (!categories[catId]) {
            categories[catId] = {
                name: b.category?.category_name || 'Otros',
                positive: 0, neutral: 0, negative: 0
            };
        }
        categories[catId].positive += b.sentiment_summary?.positive || 0;
        categories[catId].neutral += b.sentiment_summary?.neutral || 0;
        categories[catId].negative += b.sentiment_summary?.negative || 0;
    });

    const labels = Object.values(categories).map(c => c.name);
    const positiveData = Object.values(categories).map(c => c.positive);
    const neutralData = Object.values(categories).map(c => c.neutral);
    const negativeData = Object.values(categories).map(c => c.negative);

    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Positivas', data: positiveData, backgroundColor: '#10b981' },
                { label: 'Neutrales', data: neutralData, backgroundColor: '#f59e0b' },
                { label: 'Negativas', data: negativeData, backgroundColor: '#ef4444' }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#475569', padding: 15 }
                }
            },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(0,0,0,0.05)' } },
                y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(0,0,0,0.05)' } }
            }
        }
    });
}

// ============== Renderizado de Reseñas ==============
function renderReviews(reviews) {
    const container = document.getElementById('reviewsContainer');

    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<p class="loading-text">No hay reseñas disponibles</p>';
        return;
    }

    container.innerHTML = reviews.map(review => createReviewCard(review)).join('');
}

function createReviewCard(review) {
    const initials = (review.author || 'U').substring(0, 2).toUpperCase();
    const isBot = review.bot_classification === 'bot';
    const isSuspicious = review.bot_classification === 'suspicious';
    const botScore = review.bot_score || 0;

    const botScoreColor = botScore <= 30 ? '#10b981' : botScore <= 60 ? '#f59e0b' : '#ef4444';

    const indicatorsHtml = (review.bot_indicators || []).length > 0 ? `
        <div class="bot-indicators">
            ${review.bot_indicators.map(ind => `<span class="indicator-tag">${formatIndicator(ind)}</span>`).join('')}
        </div>
    ` : '';

    return `
        <div class="review-card ${isBot ? 'is-bot' : ''}" 
             data-sentiment="${review.sentiment}" 
             data-bot="${review.bot_classification}">
            <div class="review-header">
                <div class="review-author">
                    <div class="author-avatar">${initials}</div>
                    <span class="author-name">${review.author}</span>
                </div>
                <div class="review-badges">
                    <span class="badge ${review.sentiment}">${formatSentiment(review.sentiment)}</span>
                    ${isBot ? '<span class="badge bot">🤖 Bot</span>' : ''}
                    ${isSuspicious ? '<span class="badge suspicious">⚠️ Sospechoso</span>' : ''}
                </div>
            </div>
            <p class="review-text">"${review.text}"</p>
            <div class="review-footer">
                <span class="review-rating">${'★'.repeat(review.rating || 0)}${'☆'.repeat(5 - (review.rating || 0))}</span>
                <div class="review-bot-score">
                    <span>Bot Score: ${botScore}%</span>
                    <div class="bot-score-bar">
                        <div class="bot-score-fill" style="width: ${botScore}%; background: ${botScoreColor}"></div>
                    </div>
                </div>
            </div>
            ${indicatorsHtml}
        </div>
    `;
}

function formatSentiment(sentiment) {
    return { 'positive': '😊 Positivo', 'neutral': '😐 Neutral', 'negative': '😞 Negativo' }[sentiment] || sentiment;
}

function formatIndicator(indicator) {
    return { 'single_review': '1 reseña', 'short_text': 'Texto corto', 'generic_phrases': 'Frase genérica', 'no_details': 'Sin detalles', 'extreme_rating': 'Rating extremo' }[indicator] || indicator;
}

function filterReviews(filter) {
    document.querySelectorAll('.review-card').forEach(card => {
        const sentiment = card.dataset.sentiment;
        const botClass = card.dataset.bot;
        const show = filter === 'all' || (filter === 'bot' ? botClass === 'bot' : sentiment === filter);
        card.style.display = show ? 'block' : 'none';
    });
}

// ============== UI Helpers ==============
function showLoading(show) {
    document.getElementById('loadingOverlay').classList.toggle('active', show);
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#10b981;color:white;padding:1rem 1.5rem;border-radius:8px;z-index:1001;animation:slideIn 0.3s ease';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
