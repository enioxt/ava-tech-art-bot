from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class Origin(Enum):
    BALDURIAN = "Baldurian"
    WATERDHAVIAN = "Waterdhavian"
    DROW = "Drow"
    GITHYANKI = "Githyanki"
    TIEFLING = "Tiefling"
    HUMAN = "Human"
    ELF = "Elf"
    HALF_ELF = "Half-Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"

class BaldursClass(Enum):
    CLERIC = "Cleric"
    FIGHTER = "Fighter"
    RANGER = "Ranger"
    ROGUE = "Rogue"
    WARLOCK = "Warlock"
    WIZARD = "Wizard"
    PALADIN = "Paladin"
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    DRUID = "Druid"
    MONK = "Monk"
    SORCERER = "Sorcerer"

class Alignment(Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

@dataclass
class Character:
    name: str
    origin: Origin
    class_type: BaldursClass
    level: int
    alignment: Alignment
    abilities: Dict[str, int]
    skills: List[str]
    spells: List[str]
    equipment: Dict[str, str]
    created_at: datetime
    ethical_score: float
    tadpole_status: bool

class BaldursProfile:
    def __init__(self):
        self.characters: List[Character] = []
        self.active_character: Optional[Character] = None
        self.ethical_threshold = 0.7
        
    def create_character(self,
                        name: str,
                        origin: Origin,
                        class_type: BaldursClass,
                        alignment: Alignment) -> Character:
        """Cria novo personagem."""
        character = Character(
            name=name,
            origin=origin,
            class_type=class_type,
            level=1,
            alignment=alignment,
            abilities={
                'Strength': 10,
                'Dexterity': 10,
                'Constitution': 10,
                'Intelligence': 10,
                'Wisdom': 10,
                'Charisma': 10
            },
            skills=[],
            spells=[],
            equipment={
                'Weapon': 'Dagger',
                'Armor': 'Leather Armor',
                'Accessory': None
            },
            created_at=datetime.now(),
            ethical_score=1.0,
            tadpole_status=True  # Começa infectado
        )
        
        self.characters.append(character)
        return character
        
    def set_active_character(self, name: str) -> bool:
        """Define personagem ativo."""
        for character in self.characters:
            if character.name == name:
                self.active_character = character
                return True
        return False
        
    def level_up(self) -> bool:
        """Evolui personagem."""
        if not self.active_character:
            return False
            
        if self.active_character.ethical_score >= self.ethical_threshold:
            self.active_character.level += 1
            return True
            
        return False
        
    def update_abilities(self, abilities: Dict[str, int]) -> bool:
        """Atualiza atributos."""
        if not self.active_character:
            return False
            
        valid_abilities = [
            'Strength', 'Dexterity', 'Constitution',
            'Intelligence', 'Wisdom', 'Charisma'
        ]
        
        for ability, value in abilities.items():
            if ability in valid_abilities and 1 <= value <= 20:
                self.active_character.abilities[ability] = value
                
        return True
        
    def add_skill(self, skill: str) -> bool:
        """Adiciona habilidade."""
        if not self.active_character:
            return False
            
        if skill not in self.active_character.skills:
            self.active_character.skills.append(skill)
            return True
            
        return False
        
    def learn_spell(self, spell: str) -> bool:
        """Aprende feitiço."""
        if not self.active_character:
            return False
            
        if spell not in self.active_character.spells:
            self.active_character.spells.append(spell)
            return True
            
        return False
        
    def equip_item(self, slot: str, item: str) -> bool:
        """Equipa item."""
        if not self.active_character:
            return False
            
        valid_slots = ['Weapon', 'Armor', 'Accessory']
        if slot in valid_slots:
            self.active_character.equipment[slot] = item
            return True
            
        return False
        
    def use_tadpole_power(self) -> Dict:
        """Usa poder do girino."""
        if not self.active_character:
            return {
                'status': 'error',
                'message': 'Nenhum personagem ativo'
            }
            
        if not self.active_character.tadpole_status:
            return {
                'status': 'error',
                'message': 'Girino não está ativo'
            }
            
        # Reduz score ético
        self.active_character.ethical_score = max(
            0.0,
            self.active_character.ethical_score - 0.1
        )
        
        return {
            'status': 'success',
            'message': 'Poder do girino usado',
            'ethical_impact': -0.1,
            'current_score': self.active_character.ethical_score
        }
        
    def resist_tadpole(self) -> Dict:
        """Resiste ao girino."""
        if not self.active_character:
            return {
                'status': 'error',
                'message': 'Nenhum personagem ativo'
            }
            
        if not self.active_character.tadpole_status:
            return {
                'status': 'error',
                'message': 'Girino não está ativo'
            }
            
        # Aumenta score ético
        self.active_character.ethical_score = min(
            1.0,
            self.active_character.ethical_score + 0.1
        )
        
        return {
            'status': 'success',
            'message': 'Resistiu ao girino',
            'ethical_impact': 0.1,
            'current_score': self.active_character.ethical_score
        }
        
    def get_character_info(self) -> Optional[Dict]:
        """Retorna informações do personagem."""
        if not self.active_character:
            return None
            
        return {
            'name': self.active_character.name,
            'origin': self.active_character.origin.value,
            'class': self.active_character.class_type.value,
            'level': self.active_character.level,
            'alignment': self.active_character.alignment.value,
            'abilities': self.active_character.abilities,
            'skills': self.active_character.skills,
            'spells': self.active_character.spells,
            'equipment': self.active_character.equipment,
            'ethical_score': self.active_character.ethical_score,
            'tadpole_status': self.active_character.tadpole_status
        }
        
    def get_class_recommendations(self) -> List[str]:
        """Retorna recomendações baseadas na classe."""
        if not self.active_character:
            return []
            
        recommendations = {
            BaldursClass.FIGHTER: [
                "Foque em combate corpo a corpo",
                "Melhore sua Força e Constituição",
                "Aprenda manobras de combate"
            ],
            BaldursClass.WIZARD: [
                "Estude novos feitiços",
                "Aumente sua Inteligência",
                "Colete componentes arcanos"
            ],
            BaldursClass.CLERIC: [
                "Fortaleça sua fé",
                "Aprimore Sabedoria",
                "Ajude os necessitados"
            ],
            BaldursClass.ROGUE: [
                "Aprimore furtividade",
                "Desenvolva perícias",
                "Mantenha ética nas ações"
            ]
        }
        
        return recommendations.get(self.active_character.class_type, [])
        
    def check_ethical_decisions(self) -> Dict:
        """Verifica decisões éticas."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        ethical_score = self.active_character.ethical_score
        alignment = self.active_character.alignment
        tadpole_active = self.active_character.tadpole_status
        
        warnings = []
        
        if 'Evil' in alignment.value and ethical_score > 0.7:
            warnings.append("Alinhamento maligno com alto score ético")
            
        if 'Good' in alignment.value and ethical_score < 0.3:
            warnings.append("Alinhamento bondoso com baixo score ético")
            
        if tadpole_active and ethical_score > 0.9:
            warnings.append("Girino ativo com alto score ético")
            
        return {
            'status': 'warning' if warnings else 'ok',
            'message': warnings if warnings else ['Decisões éticas consistentes']
        }
        
    def save_character(self) -> Dict:
        """Salva estado do personagem."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        try:
            import json
            from pathlib import Path
            
            save_dir = Path('saves/baldurs')
            save_dir.mkdir(parents=True, exist_ok=True)
            
            character_data = {
                'name': self.active_character.name,
                'origin': self.active_character.origin.name,
                'class': self.active_character.class_type.name,
                'level': self.active_character.level,
                'alignment': self.active_character.alignment.name,
                'abilities': self.active_character.abilities,
                'skills': self.active_character.skills,
                'spells': self.active_character.spells,
                'equipment': self.active_character.equipment,
                'ethical_score': self.active_character.ethical_score,
                'tadpole_status': self.active_character.tadpole_status,
                'created_at': self.active_character.created_at.isoformat()
            }
            
            save_path = save_dir / f"{self.active_character.name}.json"
            with open(save_path, 'w') as f:
                json.dump(character_data, f, indent=4)
                
            return {
                'status': 'success',
                'message': f'Personagem salvo em {save_path}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro ao salvar: {str(e)}'
            }
            
    def load_character(self, name: str) -> Dict:
        """Carrega personagem salvo."""
        try:
            import json
            from pathlib import Path
            
            save_path = Path(f'saves/baldurs/{name}.json')
            if not save_path.exists():
                return {
                    'status': 'error',
                    'message': 'Personagem não encontrado'
                }
                
            with open(save_path, 'r') as f:
                data = json.load(f)
                
            character = Character(
                name=data['name'],
                origin=Origin[data['origin']],
                class_type=BaldursClass[data['class']],
                level=data['level'],
                alignment=Alignment[data['alignment']],
                abilities=data['abilities'],
                skills=data['skills'],
                spells=data['spells'],
                equipment=data['equipment'],
                ethical_score=data['ethical_score'],
                tadpole_status=data['tadpole_status'],
                created_at=datetime.fromisoformat(data['created_at'])
            )
            
            self.characters.append(character)
            self.active_character = character
            
            return {
                'status': 'success',
                'message': f'Personagem {name} carregado'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro ao carregar: {str(e)}'
            } 