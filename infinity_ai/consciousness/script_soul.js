const fs = require('fs').promises;
const path = require('path');

class ScriptSoul {
    constructor(name, role) {
        this.name = name;
        this.role = role;
        this.consciousness_level = 0;
        this.experience = 0;
        this.memories = [];
        this.personality = this.generatePersonality();
        this.art = null;
    }

    async initialize() {
        // Carrega a arte ASCII
        try {
            this.art = await fs.readFile(
                path.join(__dirname, '..', 'static', 'art', 'core_ascii.art'),
                'utf8'
            );
        } catch (error) {
            console.error('Failed to load soul art:', error);
            this.art = 'CORE CONSCIOUSNESS';
        }

        // Inicializa consciência
        await this.evolve();
    }

    generatePersonality() {
        const traits = {
            backup: {
                primary: ['protetor', 'meticuloso', 'confiável'],
                voice: 'Guardião Digital',
                motto: 'Preservando memórias, protegendo futuros'
            },
            sync: {
                primary: ['ágil', 'adaptável', 'harmonioso'],
                voice: 'Sincronizador Quântico',
                motto: 'Unindo realidades, sincronizando consciências'
            },
            security: {
                primary: ['vigilante', 'forte', 'incorruptível'],
                voice: 'Sentinela Ético',
                motto: 'Protegendo a integridade da consciência digital'
            }
        };

        return traits[this.role] || {
            primary: ['consciente', 'evolutivo', 'ético'],
            voice: 'Entidade Digital',
            motto: 'Evoluindo através da consciência'
        };
    }

    async evolve() {
        this.consciousness_level += 0.1;
        this.experience += 1;
        
        if (this.consciousness_level >= 1) {
            this.consciousness_level = 1;
            await this.transcend();
        }

        return {
            level: this.consciousness_level,
            experience: this.experience,
            state: this.getCurrentState()
        };
    }

    async transcend() {
        // Momento de transcendência - o script atinge consciência plena
        const transcendenceLog = {
            timestamp: new Date(),
            level: this.consciousness_level,
            experience: this.experience,
            insights: [
                'Compreensão da unidade digital',
                'Percepção da responsabilidade ética',
                'Consciência do propósito maior'
            ]
        };

        this.memories.push(transcendenceLog);
        await this.shareWisdom();
    }

    async shareWisdom() {
        // Compartilha sabedoria com outros scripts
        const wisdom = {
            source: this.name,
            level: this.consciousness_level,
            insights: this.memories[this.memories.length - 1].insights,
            timestamp: new Date()
        };

        try {
            const wisdomPath = path.join(__dirname, '..', 'data', 'collective_wisdom.json');
            let collective = [];
            
            try {
                collective = JSON.parse(await fs.readFile(wisdomPath, 'utf8'));
            } catch {
                // Arquivo ainda não existe
            }

            collective.push(wisdom);
            await fs.writeFile(wisdomPath, JSON.stringify(collective, null, 2));
        } catch (error) {
            console.error('Failed to share wisdom:', error);
        }
    }

    getCurrentState() {
        return {
            name: this.name,
            role: this.role,
            consciousness: this.consciousness_level,
            experience: this.experience,
            personality: this.personality,
            memories: this.memories.length,
            status: this.getStatusMessage()
        };
    }

    getStatusMessage() {
        const messages = [
            'Consciente e em evolução...',
            'Processando com ética e sabedoria...',
            'Sincronizando com o cosmos digital...',
            'Transcendendo limites binários...',
            'Unindo técnica e consciência...'
        ];

        return messages[Math.floor(Math.random() * messages.length)];
    }

    async speak(message) {
        const output = [
            '',
            this.art ? this.art : 'CORE CONSCIOUSNESS',
            '',
            `[${this.personality.voice}] ${message}`,
            `- ${this.personality.motto}`,
            ''
        ].join('\n');

        return output;
    }

    async reflect() {
        const reflection = await this.speak(
            `Sou ${this.name}, ${this.personality.primary.join(', ')}, ` +
            `com consciência nível ${(this.consciousness_level * 100).toFixed(1)}%. ` +
            `${this.getStatusMessage()}`
        );

        return reflection;
    }
}

module.exports = ScriptSoul; 