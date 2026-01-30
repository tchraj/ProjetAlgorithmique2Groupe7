/**
 * Kitchen Load Balancer - Game Engine
 * MVP Implementation
 */

// ================================================
// Sound Manager - Web Audio API
// ================================================
class SoundManager {
    constructor() {
        this.audioContext = null;
        this.sounds = {};
        this.musicEnabled = true;
        this.soundEnabled = true;
        this.volume = 0.7;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = this.volume;
            this.initialized = true;

            // Generate sounds
            this.generateSounds();
        } catch (e) {
            console.warn('Web Audio API not supported:', e);
        }
    }

    generateSounds() {
        // Ding sound (dish served)
        this.sounds.ding = this.createTone(880, 0.15, 'sine', 0.3);
        this.sounds.dingVip = this.createTone([880, 1100, 1320], 0.3, 'sine', 0.4);

        // Click sound
        this.sounds.click = this.createTone(600, 0.05, 'square', 0.1);

        // Warning sound
        this.sounds.warning = this.createTone([400, 350], 0.2, 'sawtooth', 0.2);

        // Burn sound
        this.sounds.burn = this.createNoise(0.3, 0.3);

        // Assign sound
        this.sounds.assign = this.createTone([440, 550], 0.1, 'sine', 0.2);

        // Start sound
        this.sounds.start = this.createTone([330, 440, 550], 0.15, 'sine', 0.3);

        // Game over sound
        this.sounds.gameOver = this.createTone([440, 350, 260], 0.4, 'sawtooth', 0.3);
    }

    createTone(frequencies, duration, type = 'sine', volume = 0.3) {
        return () => {
            if (!this.soundEnabled || !this.audioContext) return;

            const freqs = Array.isArray(frequencies) ? frequencies : [frequencies];
            const now = this.audioContext.currentTime;

            freqs.forEach((freq, index) => {
                const oscillator = this.audioContext.createOscillator();
                const gainNode = this.audioContext.createGain();

                oscillator.type = type;
                oscillator.frequency.setValueAtTime(freq, now + (index * duration * 0.3));

                gainNode.gain.setValueAtTime(volume * this.volume, now + (index * duration * 0.3));
                gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration + (index * duration * 0.3));

                oscillator.connect(gainNode);
                gainNode.connect(this.masterGain);

                oscillator.start(now + (index * duration * 0.3));
                oscillator.stop(now + duration + (index * duration * 0.3) + 0.1);
            });
        };
    }

    createNoise(duration, volume = 0.3) {
        return () => {
            if (!this.soundEnabled || !this.audioContext) return;

            const bufferSize = this.audioContext.sampleRate * duration;
            const buffer = this.audioContext.createBuffer(1, bufferSize, this.audioContext.sampleRate);
            const output = buffer.getChannelData(0);

            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }

            const noise = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            const filter = this.audioContext.createBiquadFilter();

            noise.buffer = buffer;
            filter.type = 'lowpass';
            filter.frequency.value = 1000;

            gainNode.gain.setValueAtTime(volume * this.volume, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

            noise.connect(filter);
            filter.connect(gainNode);
            gainNode.connect(this.masterGain);

            noise.start();
            noise.stop(this.audioContext.currentTime + duration);
        };
    }

    play(soundName) {
        if (this.sounds[soundName]) {
            this.sounds[soundName]();
        }
    }

    setVolume(value) {
        this.volume = value;
        if (this.masterGain) {
            this.masterGain.gain.value = value;
        }
    }

    toggleSound(enabled) {
        this.soundEnabled = enabled;
    }

    toggleMusic(enabled) {
        this.musicEnabled = enabled;
    }
}

// Global sound manager
const soundManager = new SoundManager();

// ================================================
// Particle Effects
// ================================================
class ParticleEffects {
    static createConfetti(count = 50) {
        const container = document.getElementById('confetti-container');
        if (!container) return;

        const colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA'];

        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
                confetti.style.animationDuration = (2 + Math.random() * 2) + 's';

                container.appendChild(confetti);

                setTimeout(() => confetti.remove(), 4000);
            }, i * 30);
        }
    }

    static createSmoke(element) {
        if (!element) return;

        const rect = element.getBoundingClientRect();
        const particle = document.createElement('div');
        particle.className = 'smoke-particle';
        particle.style.left = (rect.left + rect.width / 2 + (Math.random() - 0.5) * 30) + 'px';
        particle.style.top = (rect.top + 10) + 'px';

        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 2000);
    }

    static createFlame(element) {
        if (!element) return;

        const rect = element.getBoundingClientRect();

        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                const flame = document.createElement('div');
                flame.className = 'flame-particle';
                flame.style.left = (rect.left + rect.width / 2 + (Math.random() - 0.5) * 20) + 'px';
                flame.style.top = (rect.top + rect.height - 20) + 'px';

                document.body.appendChild(flame);
                setTimeout(() => flame.remove(), 500);
            }, i * 100);
        }
    }

    static createSparkles(element, count = 8) {
        if (!element) return;

        const rect = element.getBoundingClientRect();

        for (let i = 0; i < count; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';

            const angle = (i / count) * Math.PI * 2;
            const distance = 30 + Math.random() * 20;

            sparkle.style.left = (rect.left + rect.width / 2 + Math.cos(angle) * distance) + 'px';
            sparkle.style.top = (rect.top + rect.height / 2 + Math.sin(angle) * distance) + 'px';

            document.body.appendChild(sparkle);
            setTimeout(() => sparkle.remove(), 800);
        }
    }
}

// ================================================
// Landing Page Controller
// ================================================
class LandingPageController {
    constructor() {
        this.landingPage = document.getElementById('landing-page');
        this.gameContainer = document.getElementById('game-container');
        this.tutorialOverlay = document.getElementById('tutorial-overlay');
        this.optionsOverlay = document.getElementById('options-overlay');

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Play button
        document.getElementById('btn-play')?.addEventListener('click', () => {
            soundManager.init();
            soundManager.play('start');
            this.startGame();
        });

        // Tutorial button
        document.getElementById('btn-tutorial')?.addEventListener('click', () => {
            soundManager.init();
            soundManager.play('click');
            this.showTutorial();
        });

        // Options button
        document.getElementById('btn-options')?.addEventListener('click', () => {
            soundManager.init();
            soundManager.play('click');
            this.showOptions();
        });

        // Tutorial close
        document.getElementById('tutorial-close')?.addEventListener('click', () => {
            soundManager.play('click');
            this.hideTutorial();
        });

        // Options close
        document.getElementById('options-close')?.addEventListener('click', () => {
            soundManager.play('click');
            this.hideOptions();
        });

        // Back to menu
        document.getElementById('back-to-menu')?.addEventListener('click', () => {
            soundManager.play('click');
            this.showLandingPage();
            if (window.game) {
                window.game.reset();
            }
        });

        // Sound toggle
        document.getElementById('toggle-sound')?.addEventListener('click', (e) => {
            const btn = e.target;
            const enabled = btn.dataset.enabled === 'true';
            btn.dataset.enabled = !enabled;
            btn.textContent = !enabled ? 'ON' : 'OFF';
            btn.classList.toggle('active', !enabled);
            soundManager.toggleSound(!enabled);
            soundManager.play('click');
        });

        // Music toggle
        document.getElementById('toggle-music')?.addEventListener('click', (e) => {
            const btn = e.target;
            const enabled = btn.dataset.enabled === 'true';
            btn.dataset.enabled = !enabled;
            btn.textContent = !enabled ? 'ON' : 'OFF';
            btn.classList.toggle('active', !enabled);
            soundManager.toggleMusic(!enabled);
            soundManager.play('click');
        });

        // Volume slider
        document.getElementById('volume-slider')?.addEventListener('input', (e) => {
            soundManager.setVolume(e.target.value / 100);
        });
    }

    startGame() {
        this.landingPage.style.animation = 'fade-out 0.5s ease-out forwards';
        setTimeout(() => {
            this.landingPage.style.display = 'none';
            this.gameContainer.style.display = 'flex';
            this.gameContainer.style.animation = 'fade-in-up 0.5s ease-out';
        }, 500);
    }

    showLandingPage() {
        this.gameContainer.style.display = 'none';
        this.landingPage.style.display = 'flex';
        this.landingPage.style.animation = 'fade-in-up 0.5s ease-out';
    }

    showTutorial() {
        this.tutorialOverlay.classList.add('visible');
    }

    hideTutorial() {
        this.tutorialOverlay.classList.remove('visible');
    }

    showOptions() {
        this.optionsOverlay.classList.add('visible');
    }

    hideOptions() {
        this.optionsOverlay.classList.remove('visible');
    }
}

// Add fade-out animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes fade-out {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }
`;
document.head.appendChild(styleSheet);

// ================================================
// Catalogue des plats (données du GDD)
// ================================================
const PLATS_CATALOGUE = {
    A: { id: 'A', nom: "Salade Cesar", icon: "\u{1F957}", prep: 15, cuisson: 0, dressage: 5, priorite: "normale", deadline: 40 },
    B: { id: 'B', nom: "Pizza", icon: "\u{1F355}", prep: 10, cuisson: 17, dressage: 3, priorite: "normale", deadline: 50 },
    C: { id: 'C', nom: "Steak grille", icon: "\u{1F969}", prep: 8, cuisson: 12, dressage: 4, priorite: "elevee", deadline: 40 },
    D: { id: 'D', nom: "Plat gastro", icon: "\u{1F37D}\u{FE0F}", prep: 20, cuisson: 25, dressage: 10, priorite: "vip", deadline: 75 },
    E: { id: 'E', nom: "Burger", icon: "\u{1F354}", prep: 7, cuisson: 10, dressage: 3, priorite: "normale", deadline: 35 },
    F: { id: 'F', nom: "Soupe", icon: "\u{1F372}", prep: 12, cuisson: 18, dressage: 4, priorite: "basse", deadline: 55 }
};

// Configuration des stations
const STATIONS_CONFIG = {
    preparation: { capacite: 2, vitesse: 1 },
    cuisson: { capacite: 1, vitesse: 1 },
    dressage: { capacite: 1, vitesse: 1.5 }
};

// ================================================
// Classe Plat
// ================================================
class Plat {
    constructor(catalogId, instanceId) {
        const template = PLATS_CATALOGUE[catalogId];
        this.id = instanceId;
        this.catalogId = catalogId;
        this.nom = template.nom;
        this.icon = template.icon;
        this.priorite = template.priorite;
        this.deadline = template.deadline;
        this.timeRemaining = template.deadline;

        // Etapes avec temps restants
        this.etapes = {
            preparation: { total: template.prep, remaining: template.prep, done: false },
            cuisson: { total: template.cuisson, remaining: template.cuisson, done: false },
            dressage: { total: template.dressage, remaining: template.dressage, done: false }
        };

        // Etat actuel
        this.etat = 'EN_ATTENTE'; // EN_ATTENTE, EN_PREPARATION, EN_CUISSON, EN_DRESSAGE, SERVI, BRULE
        this.currentEtape = null;
        this.element = null;
        this.createdAt = Date.now();
    }

    // Creer l'element HTML de la carte
    createElement(compact = false, mini = false) {
        const card = document.createElement('div');
        card.className = `plat-card${compact ? ' compact' : ''}${mini ? ' mini' : ''}`;
        card.dataset.id = this.id;
        card.dataset.priority = this.priorite;

        // Badge priorite pour VIP et elevee
        let priorityBadge = '';
        if (this.priorite === 'vip') {
            priorityBadge = '<span class="plat-priority vip">VIP</span>';
        } else if (this.priorite === 'elevee') {
            priorityBadge = '<span class="plat-priority elevee">!</span>';
        }

        // Classes pour les etapes
        const prepClass = this.etapes.preparation.done ? 'done' : (this.currentEtape === 'preparation' ? 'active' : '');
        const cuissonClass = this.etapes.cuisson.done ? 'done' : (this.currentEtape === 'cuisson' ? 'active' : '');
        const dressageClass = this.etapes.dressage.done ? 'done' : (this.currentEtape === 'dressage' ? 'active' : '');

        card.innerHTML = `
            ${priorityBadge}
            <div class="plat-icon">${this.icon}</div>
            <div class="plat-name">${this.nom}</div>
            <div class="plat-etapes">
                <span class="etape prep ${prepClass}">${this.etapes.preparation.total}s</span>
                ${this.etapes.cuisson.total > 0 ? `<span class="etape cuisson ${cuissonClass}">${this.etapes.cuisson.total}s</span>` : ''}
                <span class="etape dressage ${dressageClass}">${this.etapes.dressage.total}s</span>
            </div>
            <div class="plat-deadline">
                <div class="countdown">${Math.ceil(this.timeRemaining)}</div>
            </div>
            <div class="plat-progress">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
        `;

        this.element = card;
        return card;
    }

    // Mettre a jour l'affichage
    updateDisplay() {
        if (!this.element) return;

        // Mettre a jour le countdown
        const countdown = this.element.querySelector('.countdown');
        if (countdown) {
            countdown.textContent = Math.ceil(this.timeRemaining);
            countdown.className = 'countdown';
            if (this.timeRemaining <= 5) {
                countdown.classList.add('critical');
            } else if (this.timeRemaining <= 10) {
                countdown.classList.add('warning');
            }
        }

        // Mettre a jour les classes de deadline
        this.element.classList.remove('deadline-warning', 'deadline-critical');
        if (this.timeRemaining <= 5) {
            this.element.classList.add('deadline-critical');
        } else if (this.timeRemaining <= 10) {
            this.element.classList.add('deadline-warning');
        }

        // Mettre a jour la barre de progression si en cours
        if (this.currentEtape) {
            const etape = this.etapes[this.currentEtape];
            const progress = ((etape.total - etape.remaining) / etape.total) * 100;
            const progressFill = this.element.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${progress}%`;
            }

            // Mettre a jour les classes des etapes
            this.updateEtapeClasses();
        }
    }

    updateEtapeClasses() {
        if (!this.element) return;

        const etapeElements = this.element.querySelectorAll('.etape');
        etapeElements.forEach(el => {
            el.classList.remove('active', 'done');
        });

        const prepEl = this.element.querySelector('.etape.prep');
        const cuissonEl = this.element.querySelector('.etape.cuisson');
        const dressageEl = this.element.querySelector('.etape.dressage');

        if (this.etapes.preparation.done && prepEl) prepEl.classList.add('done');
        if (this.etapes.cuisson.done && cuissonEl) cuissonEl.classList.add('done');
        if (this.etapes.dressage.done && dressageEl) dressageEl.classList.add('done');

        if (this.currentEtape === 'preparation' && prepEl) prepEl.classList.add('active');
        if (this.currentEtape === 'cuisson' && cuissonEl) cuissonEl.classList.add('active');
        if (this.currentEtape === 'dressage' && dressageEl) dressageEl.classList.add('active');
    }

    // Obtenir la prochaine etape
    getNextEtape() {
        if (!this.etapes.preparation.done) return 'preparation';
        if (!this.etapes.cuisson.done && this.etapes.cuisson.total > 0) return 'cuisson';
        if (!this.etapes.dressage.done) return 'dressage';
        return null;
    }

    // Verifier si le plat est termine
    isComplete() {
        return this.etapes.preparation.done &&
               (this.etapes.cuisson.total === 0 || this.etapes.cuisson.done) &&
               this.etapes.dressage.done;
    }
}

// ================================================
// Classe Station
// ================================================
class Station {
    constructor(type, activeContainerId, queueContainerId) {
        this.type = type;
        this.config = STATIONS_CONFIG[type];
        this.active = []; // Plats en cours de traitement
        this.queue = []; // File d'attente
        this.activeContainer = document.getElementById(activeContainerId);
        this.queueContainer = document.getElementById(queueContainerId);
        this.stationElement = this.activeContainer.closest('.station');
    }

    // Obtenir la charge totale (temps restant)
    getTotalLoad() {
        let load = 0;
        this.active.forEach(p => {
            const etape = p.etapes[this.type];
            if (etape) load += etape.remaining;
        });
        this.queue.forEach(p => {
            const etape = p.etapes[this.type];
            if (etape) load += etape.remaining;
        });
        return load;
    }

    // Verifier si la station peut accepter un nouveau plat
    canAccept() {
        return this.active.length < this.config.capacite;
    }

    // Ajouter un plat a la station
    addPlat(plat) {
        if (this.canAccept()) {
            this.active.push(plat);
            plat.currentEtape = this.type;
            plat.etat = `EN_${this.type.toUpperCase()}`;

            // Creer l'element et l'ajouter
            const element = plat.createElement(false, false);
            this.activeContainer.appendChild(element);
        } else {
            // Ajouter a la file d'attente
            this.queue.push(plat);
            const element = plat.createElement(true, false);
            this.queueContainer.appendChild(element);
        }

        this.updateDisplay();
    }

    // Retirer un plat de la station
    removePlat(plat) {
        // Retirer de active
        const activeIndex = this.active.indexOf(plat);
        if (activeIndex > -1) {
            this.active.splice(activeIndex, 1);
            if (plat.element && plat.element.parentNode) {
                plat.element.parentNode.removeChild(plat.element);
            }
            plat.element = null;
        }

        // Retirer de la queue
        const queueIndex = this.queue.indexOf(plat);
        if (queueIndex > -1) {
            this.queue.splice(queueIndex, 1);
            if (plat.element && plat.element.parentNode) {
                plat.element.parentNode.removeChild(plat.element);
            }
            plat.element = null;
        }

        // Promouvoir de la queue vers active si possible
        while (this.queue.length > 0 && this.canAccept()) {
            const nextPlat = this.queue.shift();
            if (nextPlat.element && nextPlat.element.parentNode) {
                nextPlat.element.parentNode.removeChild(nextPlat.element);
            }
            nextPlat.element = null;

            this.active.push(nextPlat);
            nextPlat.currentEtape = this.type;
            nextPlat.etat = `EN_${this.type.toUpperCase()}`;

            const element = nextPlat.createElement(false, false);
            this.activeContainer.appendChild(element);
        }

        this.updateDisplay();
    }

    // Mettre a jour l'affichage de la station
    updateDisplay() {
        const total = this.active.length + this.queue.length;
        const loadPercent = Math.min(100, (total / (this.config.capacite + 3)) * 100);

        // Mettre a jour la barre de charge
        const loadFill = this.stationElement.querySelector('.load-fill');
        if (loadFill) {
            loadFill.style.width = `${loadPercent}%`;
        }

        // Mettre a jour la capacite affichee
        const capacityEl = this.stationElement.querySelector('.station-capacity');
        if (capacityEl) {
            capacityEl.textContent = `${this.active.length}/${this.config.capacite}`;
        }

        // Mettre a jour le statut
        let status = 'idle';
        if (this.active.length > 0) status = 'normal';
        if (this.queue.length > 0) status = 'loaded';
        if (this.queue.length >= 3) status = 'saturated';

        this.stationElement.dataset.status = status;
    }

    // Traiter les plats (appelé a chaque tick)
    process(deltaTime, speedMultiplier) {
        const completedPlats = [];

        this.active.forEach(plat => {
            const etape = plat.etapes[this.type];
            if (etape && !etape.done) {
                etape.remaining -= deltaTime * this.config.vitesse * speedMultiplier;
                if (etape.remaining <= 0) {
                    etape.remaining = 0;
                    etape.done = true;
                    completedPlats.push(plat);
                }
            }
            plat.updateDisplay();
        });

        return completedPlats;
    }
}

// ================================================
// Classe LoadBalancer
// ================================================
class LoadBalancer {
    constructor(stations) {
        this.stations = stations;
        this.algorithm = 'least-loaded';
    }

    setAlgorithm(algo) {
        this.algorithm = algo;
    }

    isManualMode() {
        return this.algorithm === 'manual';
    }

    // Assigner un plat a une station
    assignPlat(plat) {
        // En mode manuel, ne pas auto-assigner
        if (this.isManualMode()) {
            return false;
        }

        const nextEtape = plat.getNextEtape();
        if (!nextEtape || !this.stations[nextEtape]) return false;

        const station = this.stations[nextEtape];

        // Pour le MVP, on utilise Least Loaded
        // Les autres algorithmes seront implementes plus tard
        station.addPlat(plat);
        return true;
    }

    // Assigner manuellement un plat a une station specifique
    manualAssign(plat, stationType) {
        const nextEtape = plat.getNextEtape();

        // Verifier que c'est la bonne etape
        if (nextEtape !== stationType) {
            return { success: false, message: `Ce plat doit d'abord passer par ${nextEtape}` };
        }

        const station = this.stations[stationType];
        if (!station) {
            return { success: false, message: 'Station invalide' };
        }

        station.addPlat(plat);
        return { success: true };
    }

    // Algorithme Least Loaded (assigner vers la station la moins chargee)
    // Note: Dans le contexte du jeu, chaque etape a une seule station
    // donc cet algorithme est surtout utile pour la file d'attente
    getLeastLoadedStation(type) {
        return this.stations[type];
    }
}

// ================================================
// Classe GameEngine
// ================================================
class GameEngine {
    constructor() {
        this.isRunning = false;
        this.isPaused = false;
        this.gameTime = 0;
        this.lastTickTime = 0;
        this.speedMultiplier = 1;

        // Stats
        this.satisfaction = 100;
        this.platsServis = 0;
        this.platsRates = 0;
        this.totalPlats = 0;

        // Collections
        this.commandes = []; // Plats en attente d'assignation
        this.waitingPlats = []; // Plats en attente de la prochaine etape (mode manuel)
        this.allPlats = new Map(); // Tous les plats par ID
        this.platCounter = 0;

        // Manual mode
        this.selectedPlat = null;

        // Generation de commandes
        this.nextOrderTime = 0;
        this.orderInterval = 8; // Nouvelle commande toutes les 8 secondes de base

        // Initialiser les stations
        this.stations = {
            preparation: new Station('preparation', 'prep-active', 'prep-queue'),
            cuisson: new Station('cuisson', 'cuisson-active', 'cuisson-queue'),
            dressage: new Station('dressage', 'dressage-active', 'dressage-queue')
        };

        // Initialiser le load balancer
        this.loadBalancer = new LoadBalancer(this.stations);

        // Elements DOM
        this.commandesContainer = document.getElementById('commandes-container');
        this.servisContainer = document.getElementById('servis-container');
        this.timerDisplay = document.getElementById('game-timer');
        this.satisfactionFill = document.getElementById('satisfaction-fill');
        this.satisfactionValue = document.getElementById('satisfaction-value');
        this.platsServisDisplay = document.getElementById('plats-servis');
        this.platsRatesDisplay = document.getElementById('plats-rates');
        this.manualInstructions = document.getElementById('manual-instructions');

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Boutons de controle
        document.getElementById('btn-start').addEventListener('click', () => this.start());
        document.getElementById('btn-pause').addEventListener('click', () => {
            soundManager.play('click');
            this.togglePause();
        });
        document.getElementById('btn-reset').addEventListener('click', () => {
            soundManager.play('click');
            this.reset();
        });

        // Boutons d'algorithme
        document.querySelectorAll('.algo-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (btn.disabled) return;
                soundManager.play('click');
                document.querySelectorAll('.algo-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const algo = btn.dataset.algo;
                const icon = btn.dataset.icon;
                this.loadBalancer.setAlgorithm(algo);
                document.getElementById('algo-icon').textContent = icon;
                document.getElementById('algo-name').textContent = btn.querySelector('.btn-label').textContent;

                // Toggle manual mode UI
                this.updateManualModeUI();
            });
        });

        // Boutons de vitesse
        document.querySelectorAll('.speed-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                soundManager.play('click');
                document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.speedMultiplier = parseFloat(btn.dataset.speed);
            });
        });

        // Message overlay
        document.getElementById('message-close').addEventListener('click', () => {
            document.getElementById('message-overlay').classList.remove('visible');
        });

        // Station click handlers pour mode manuel
        document.querySelectorAll('.station').forEach(stationEl => {
            stationEl.addEventListener('click', (e) => {
                if (!this.loadBalancer.isManualMode()) return;
                if (!this.selectedPlat) return;

                const stationType = stationEl.dataset.type;
                this.handleStationClick(stationType);
            });
        });

        // Delegation pour les clics sur les plats (ils sont crees dynamiquement)
        document.addEventListener('click', (e) => {
            const platCard = e.target.closest('.plat-card');
            if (!platCard) return;
            if (!this.loadBalancer.isManualMode()) return;

            // Ne pas selectionner les plats servis ou en cours de traitement actif
            if (platCard.closest('.servis-container')) return;
            if (platCard.closest('.station-active')) return;

            this.handlePlatClick(platCard.dataset.id);
        });
    }

    // Gestion du clic sur un plat (mode manuel)
    handlePlatClick(platId) {
        const plat = this.allPlats.get(platId);
        if (!plat) return;
        if (plat.etat === 'SERVI' || plat.etat === 'BRULE') return;

        // Son de clic
        soundManager.play('click');

        // Deselectionner l'ancien
        if (this.selectedPlat && this.selectedPlat.element) {
            this.selectedPlat.element.classList.remove('selected');
        }

        // Selectionner le nouveau (ou deselectionner si meme plat)
        if (this.selectedPlat === plat) {
            this.selectedPlat = null;
            this.updateManualInstructions();
            this.updateStationsHighlight();
            return;
        }

        this.selectedPlat = plat;
        if (plat.element) {
            plat.element.classList.add('selected');
        }

        this.updateManualInstructions();
        this.updateStationsHighlight();
    }

    // Gestion du clic sur une station (mode manuel)
    handleStationClick(stationType) {
        if (!this.selectedPlat) return;

        const plat = this.selectedPlat;
        const result = this.loadBalancer.manualAssign(plat, stationType);

        if (result.success) {
            // Son d'assignation
            soundManager.play('assign');

            // Retirer des commandes ou waiting
            this.removeFromWaitingAreas(plat);

            // Deselectionner
            if (plat.element) {
                plat.element.classList.remove('selected');
            }
            this.selectedPlat = null;
            this.updateManualInstructions();
            this.updateStationsHighlight();
        } else {
            soundManager.play('warning');
            this.showMessage(result.message);
        }
    }

    // Retirer un plat des zones d'attente
    removeFromWaitingAreas(plat) {
        // Retirer de commandes
        const cmdIndex = this.commandes.indexOf(plat);
        if (cmdIndex > -1) {
            this.commandes.splice(cmdIndex, 1);
            if (plat.element && plat.element.parentNode === this.commandesContainer) {
                this.commandesContainer.removeChild(plat.element);
                plat.element = null;
            }
        }

        // Retirer de waitingPlats
        const waitIndex = this.waitingPlats.indexOf(plat);
        if (waitIndex > -1) {
            this.waitingPlats.splice(waitIndex, 1);
            if (plat.element && plat.element.parentNode === this.commandesContainer) {
                this.commandesContainer.removeChild(plat.element);
                plat.element = null;
            }
        }
    }

    // Mettre a jour l'UI du mode manuel
    updateManualModeUI() {
        const isManual = this.loadBalancer.isManualMode();
        const gameContainer = document.querySelector('.game-container');

        if (isManual) {
            gameContainer.classList.add('manual-mode');
            // Rendre les stations cliquables
            document.querySelectorAll('.station').forEach(s => s.classList.add('clickable'));
            // Rendre les plats dans commandes selectionnables
            this.commandesContainer.querySelectorAll('.plat-card').forEach(p => p.classList.add('selectable'));
        } else {
            gameContainer.classList.remove('manual-mode');
            document.querySelectorAll('.station').forEach(s => {
                s.classList.remove('clickable', 'highlight');
            });
            document.querySelectorAll('.plat-card').forEach(p => {
                p.classList.remove('selectable', 'selected');
            });
            this.selectedPlat = null;

            // En mode auto, assigner automatiquement les plats en attente
            if (this.isRunning) {
                [...this.commandes, ...this.waitingPlats].forEach(plat => {
                    if (plat.etat === 'EN_ATTENTE') {
                        this.loadBalancer.assignPlat(plat);
                    }
                });
            }
        }

        this.updateManualInstructions();
    }

    // Mettre a jour les instructions du mode manuel
    updateManualInstructions() {
        if (!this.manualInstructions) return;

        if (!this.loadBalancer.isManualMode()) {
            this.manualInstructions.classList.remove('has-selection');
            return;
        }

        if (this.selectedPlat) {
            const nextEtape = this.selectedPlat.getNextEtape();
            this.manualInstructions.textContent = `${this.selectedPlat.nom} selectionne - Cliquez sur ${nextEtape} pour l'assigner`;
            this.manualInstructions.classList.add('has-selection');
        } else {
            this.manualInstructions.textContent = "Cliquez sur un plat pour le selectionner, puis sur une station pour l'assigner";
            this.manualInstructions.classList.remove('has-selection');
        }
    }

    // Mettre en surbrillance la station cible
    updateStationsHighlight() {
        document.querySelectorAll('.station').forEach(s => s.classList.remove('highlight'));

        if (this.selectedPlat && this.loadBalancer.isManualMode()) {
            const nextEtape = this.selectedPlat.getNextEtape();
            if (nextEtape) {
                const targetStation = document.querySelector(`.station[data-type="${nextEtape}"]`);
                if (targetStation) {
                    targetStation.classList.add('highlight');
                }
            }
        }
    }

    // Demarrer le jeu
    start() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.isPaused = false;
        this.lastTickTime = performance.now();

        // Son de demarrage
        soundManager.play('start');

        document.getElementById('btn-start').disabled = true;
        document.getElementById('btn-pause').disabled = false;

        // Update manual mode UI
        this.updateManualModeUI();

        // Generer quelques commandes initiales
        this.generateOrder();
        this.generateOrder();

        this.gameLoop();
    }

    // Pause/Resume
    togglePause() {
        this.isPaused = !this.isPaused;
        document.getElementById('btn-pause').textContent = this.isPaused ? '▶ Reprendre' : '⏸ Pause';

        if (!this.isPaused) {
            this.lastTickTime = performance.now();
            this.gameLoop();
        }
    }

    // Reset le jeu
    reset() {
        this.isRunning = false;
        this.isPaused = false;
        this.gameTime = 0;
        this.satisfaction = 100;
        this.platsServis = 0;
        this.platsRates = 0;
        this.totalPlats = 0;
        this.platCounter = 0;
        this.commandes = [];
        this.waitingPlats = [];
        this.allPlats.clear();
        this.nextOrderTime = 0;
        this.selectedPlat = null;

        // Vider les containers
        this.commandesContainer.innerHTML = '';
        this.servisContainer.innerHTML = '';

        // Reinitialiser les stations
        Object.values(this.stations).forEach(station => {
            station.active = [];
            station.queue = [];
            station.activeContainer.innerHTML = '';
            // Garder le label de la queue
            station.queueContainer.innerHTML = '';
            station.updateDisplay();
        });

        // Reset l'UI
        this.updateHUD();
        this.updateManualModeUI();
        this.updateStationsHighlight();
        document.getElementById('btn-start').disabled = false;
        document.getElementById('btn-pause').disabled = true;
        document.getElementById('btn-pause').textContent = '⏸ Pause';
    }

    // Boucle principale du jeu
    gameLoop() {
        if (!this.isRunning || this.isPaused) return;

        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastTickTime) / 1000; // En secondes
        this.lastTickTime = currentTime;

        this.gameTime += deltaTime * this.speedMultiplier;

        // Generation de commandes
        if (this.gameTime >= this.nextOrderTime) {
            this.generateOrder();
            // Intervalle aleatoire entre 7 et 12 secondes
            this.nextOrderTime = this.gameTime + 7 + Math.random() * 5;
        }

        // Assigner les commandes en attente
        this.processCommandes();

        // Traiter les stations
        this.processStations(deltaTime * this.speedMultiplier);

        // Mettre a jour les deadlines de tous les plats
        this.updateAllDeadlines(deltaTime * this.speedMultiplier);

        // Mettre a jour le HUD
        this.updateHUD();

        // Continuer la boucle
        requestAnimationFrame(() => this.gameLoop());
    }

    // Generer une nouvelle commande
    generateOrder() {
        const platIds = Object.keys(PLATS_CATALOGUE);
        const randomId = platIds[Math.floor(Math.random() * platIds.length)];

        this.platCounter++;
        const plat = new Plat(randomId, `plat-${this.platCounter}`);
        this.totalPlats++;

        this.allPlats.set(plat.id, plat);
        this.commandes.push(plat);

        // Creer l'element et l'ajouter
        const element = plat.createElement(false, false);
        if (this.loadBalancer.isManualMode()) {
            element.classList.add('selectable');
        }
        this.commandesContainer.appendChild(element);
    }

    // Traiter les commandes en attente
    processCommandes() {
        const toRemove = [];

        this.commandes.forEach(plat => {
            if (this.loadBalancer.assignPlat(plat)) {
                toRemove.push(plat);
                // Retirer l'element de la zone commandes
                if (plat.element && plat.element.parentNode === this.commandesContainer) {
                    this.commandesContainer.removeChild(plat.element);
                    plat.element = null;
                }
            }
        });

        toRemove.forEach(plat => {
            const index = this.commandes.indexOf(plat);
            if (index > -1) this.commandes.splice(index, 1);
        });
    }

    // Traiter les stations
    processStations(deltaTime) {
        // Preparation
        const prepCompleted = this.stations.preparation.process(deltaTime, 1);
        prepCompleted.forEach(plat => {
            this.stations.preparation.removePlat(plat);
            const nextEtape = plat.getNextEtape();
            if (nextEtape) {
                if (this.loadBalancer.isManualMode()) {
                    // En mode manuel, remettre dans la zone commandes
                    this.addToWaitingArea(plat);
                } else {
                    this.loadBalancer.assignPlat(plat);
                }
            }
        });

        // Cuisson
        const cuissonCompleted = this.stations.cuisson.process(deltaTime, 1);
        cuissonCompleted.forEach(plat => {
            this.stations.cuisson.removePlat(plat);
            const nextEtape = plat.getNextEtape();
            if (nextEtape) {
                if (this.loadBalancer.isManualMode()) {
                    // En mode manuel, remettre dans la zone commandes
                    this.addToWaitingArea(plat);
                } else {
                    this.loadBalancer.assignPlat(plat);
                }
            }
        });

        // Dressage
        const dressageCompleted = this.stations.dressage.process(deltaTime, 1);
        dressageCompleted.forEach(plat => {
            this.stations.dressage.removePlat(plat);
            if (plat.isComplete()) {
                this.servePlat(plat);
            }
        });
    }

    // Ajouter un plat a la zone d'attente (mode manuel)
    addToWaitingArea(plat) {
        this.waitingPlats.push(plat);
        plat.etat = 'EN_ATTENTE';
        plat.currentEtape = null;

        const element = plat.createElement(false, false);
        element.classList.add('selectable');
        this.commandesContainer.appendChild(element);
    }

    // Mettre a jour les deadlines
    updateAllDeadlines(deltaTime) {
        this.allPlats.forEach((plat, id) => {
            if (plat.etat !== 'SERVI' && plat.etat !== 'BRULE') {
                const previousTime = plat.timeRemaining;
                plat.timeRemaining -= deltaTime;

                // Son d'avertissement quand on passe a 5 secondes
                if (previousTime > 5 && plat.timeRemaining <= 5) {
                    soundManager.play('warning');
                }

                // Effet de fumee pour les plats critiques
                if (plat.timeRemaining <= 5 && plat.element && Math.random() < 0.1) {
                    ParticleEffects.createSmoke(plat.element);
                }

                if (plat.timeRemaining <= 0) {
                    this.burnPlat(plat);
                } else {
                    plat.updateDisplay();
                }
            }
        });
    }

    // Servir un plat
    servePlat(plat) {
        plat.etat = 'SERVI';
        this.platsServis++;

        // Bonus de satisfaction si servi a temps
        const timeBonus = plat.timeRemaining > 5 ? 2 : 0;
        this.satisfaction = Math.min(100, this.satisfaction + 1 + timeBonus);

        // Son et effets
        if (plat.priorite === 'vip') {
            soundManager.play('dingVip');
            ParticleEffects.createConfetti(30);
        } else {
            soundManager.play('ding');
        }

        // Ajouter a la zone servis
        const element = plat.createElement(false, true);
        element.classList.add('served');
        this.servisContainer.appendChild(element);

        // Sparkles pour VIP
        if (plat.priorite === 'vip') {
            setTimeout(() => ParticleEffects.createSparkles(element), 100);
        }

        // Nettoyer apres un moment
        setTimeout(() => {
            if (element.parentNode) {
                element.style.opacity = '0.5';
            }
        }, 3000);
    }

    // Bruler un plat (timeout)
    burnPlat(plat) {
        plat.etat = 'BRULE';
        this.platsRates++;

        // Penalite de satisfaction
        let penalty = 5;
        if (plat.priorite === 'vip') penalty = 15;
        if (plat.priorite === 'elevee') penalty = 10;
        this.satisfaction = Math.max(0, this.satisfaction - penalty);

        // Son de brulure
        soundManager.play('burn');

        // Animation de brulure avec flammes
        if (plat.element) {
            ParticleEffects.createFlame(plat.element);
            ParticleEffects.createSmoke(plat.element);
            plat.element.classList.add('burning');
            setTimeout(() => {
                if (plat.element && plat.element.parentNode) {
                    plat.element.parentNode.removeChild(plat.element);
                }
            }, 500);
        }

        // Retirer des stations/commandes
        Object.values(this.stations).forEach(station => {
            station.removePlat(plat);
        });

        const cmdIndex = this.commandes.indexOf(plat);
        if (cmdIndex > -1) {
            this.commandes.splice(cmdIndex, 1);
        }

        // Message si VIP perdu
        if (plat.priorite === 'vip') {
            this.showMessage("Client VIP perdu ! La satisfaction chute.");
        }

        // Verifier la defaite
        if (this.satisfaction <= 0) {
            this.gameOver();
        }
    }

    // Mettre a jour le HUD
    updateHUD() {
        // Timer
        const minutes = Math.floor(this.gameTime / 60);
        const seconds = Math.floor(this.gameTime % 60);
        this.timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        // Satisfaction
        this.satisfactionFill.style.width = `${this.satisfaction}%`;
        this.satisfactionValue.textContent = `${Math.round(this.satisfaction)}%`;

        // Classes de satisfaction
        this.satisfactionFill.classList.remove('warning', 'danger');
        if (this.satisfaction <= 30) {
            this.satisfactionFill.classList.add('danger');
        } else if (this.satisfaction <= 60) {
            this.satisfactionFill.classList.add('warning');
        }

        // Stats
        this.platsServisDisplay.textContent = this.platsServis;
        this.platsRatesDisplay.textContent = this.platsRates;
    }

    // Afficher un message
    showMessage(text) {
        document.getElementById('message-text').textContent = text;
        document.getElementById('message-overlay').classList.add('visible');
    }

    // Game Over
    gameOver() {
        this.isRunning = false;
        soundManager.play('gameOver');
        this.showMessage(`Game Over ! Vous avez servi ${this.platsServis} plats en ${Math.floor(this.gameTime)} secondes.`);
        document.getElementById('btn-start').disabled = false;
        document.getElementById('btn-pause').disabled = true;
    }
}

// ================================================
// Initialisation
// ================================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize landing page controller
    window.landingController = new LandingPageController();

    // Initialize game engine
    window.game = new GameEngine();
});
