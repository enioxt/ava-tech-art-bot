from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class CharacterClass(Enum):
    WARRIOR = "Guerreiro"
    MAGE = "Mago"
    ROGUE = "Ladino"
    CLERIC = "Clérigo"
    PALADIN = "Paladino"
    RANGER = "Patrulheiro"
    BARD = "Bardo"
    DRUID = "Druida"
    WARLOCK = "Bruxo"
    SORCERER = "Feiticeiro"

class Alignment(Enum):
    LAWFUL_GOOD = "Leal e Bom"
    NEUTRAL_GOOD = "Neutro e Bom"
    CHAOTIC_GOOD = "Caótico e Bom"
    LAWFUL_NEUTRAL = "Leal e Neutro"
    TRUE_NEUTRAL = "Neutro"
    CHAOTIC_NEUTRAL = "Caótico e Neutro"
    LAWFUL_EVIL = "Leal e Mau"
    NEUTRAL_EVIL = "Neutro e Mau"
    CHAOTIC_EVIL = "Caótico e Mau"

@dataclass
class Character:
    name: str
    class_type: CharacterClass
    level: int
    alignment: Alignment
    attributes: Dict[str, int]
    skills: List[str]
    background: str
    created_at: datetime
    ethical_score: float

class DNDProfile:
    def __init__(self):
        self.characters: List[Character] = []
        self.active_character: Optional[Character] = None
        self.ethical_threshold = 0.7
        
    def create_character(self, 
                        name: str,
                        class_type: CharacterClass,
                        alignment: Alignment,
                        background: str) -> Character:
        """Cria um novo personagem."""
        character = Character(
            name=name,
            class_type=class_type,
            level=1,
            alignment=alignment,
            attributes={
                'Força': 10,
                'Destreza': 10,
                'Constituição': 10,
                'Inteligência': 10,
                'Sabedoria': 10,
                'Carisma': 10
            },
            skills=[],
            background=background,
            created_at=datetime.now(),
            ethical_score=1.0
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
        """Evolui personagem ativo."""
        if not self.active_character:
            return False
            
        if self.active_character.ethical_score >= self.ethical_threshold:
            self.active_character.level += 1
            return True
            
        return False
        
    def add_skill(self, skill: str) -> bool:
        """Adiciona habilidade ao personagem ativo."""
        if not self.active_character:
            return False
            
        if skill not in self.active_character.skills:
            self.active_character.skills.append(skill)
            return True
            
        return False
        
    def update_attributes(self, attributes: Dict[str, int]) -> bool:
        """Atualiza atributos do personagem ativo."""
        if not self.active_character:
            return False
            
        valid_attributes = [
            'Força', 'Destreza', 'Constituição',
            'Inteligência', 'Sabedoria', 'Carisma'
        ]
        
        for attr, value in attributes.items():
            if attr in valid_attributes and 1 <= value <= 20:
                self.active_character.attributes[attr] = value
                
        return True
        
    def get_character_info(self) -> Optional[Dict]:
        """Retorna informações do personagem ativo."""
        if not self.active_character:
            return None
            
        return {
            'name': self.active_character.name,
            'class': self.active_character.class_type.value,
            'level': self.active_character.level,
            'alignment': self.active_character.alignment.value,
            'attributes': self.active_character.attributes,
            'skills': self.active_character.skills,
            'background': self.active_character.background,
            'ethical_score': self.active_character.ethical_score
        }
        
    def check_alignment_ethics(self) -> Dict:
        """Verifica ética do alinhamento."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        alignment = self.active_character.alignment
        ethical_score = self.active_character.ethical_score
        
        if 'Evil' in alignment.value and ethical_score > 0.7:
            return {
                'status': 'warning',
                'message': 'Alinhamento maligno com alto score ético'
            }
            
        if 'Good' in alignment.value and ethical_score < 0.3:
            return {
                'status': 'warning',
                'message': 'Alinhamento bondoso com baixo score ético'
            }
            
        return {
            'status': 'ok',
            'message': 'Alinhamento e ética consistentes'
        }
        
    def get_class_recommendations(self) -> List[str]:
        """Retorna recomendações baseadas na classe."""
        if not self.active_character:
            return []
            
        recommendations = {
            CharacterClass.WARRIOR: [
                "Foque em atributos físicos",
                "Treine combate corpo a corpo",
                "Desenvolva liderança"
            ],
            CharacterClass.MAGE: [
                "Estude magias arcanas",
                "Aprimore inteligência",
                "Colete componentes mágicos"
            ],
            CharacterClass.CLERIC: [
                "Fortaleça sua fé",
                "Cure os necessitados",
                "Combata o mal"
            ],
            CharacterClass.ROGUE: [
                "Aprimore furtividade",
                "Desenvolva perícias",
                "Mantenha ética nas ações"
            ]
        }
        
        return recommendations.get(self.active_character.class_type, [])
        
    def save_character(self) -> Dict:
        """Salva estado do personagem."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        try:
            import json
            from pathlib import Path
            
            save_dir = Path('saves/characters')
            save_dir.mkdir(parents=True, exist_ok=True)
            
            character_data = {
                'name': self.active_character.name,
                'class': self.active_character.class_type.name,
                'level': self.active_character.level,
                'alignment': self.active_character.alignment.name,
                'attributes': self.active_character.attributes,
                'skills': self.active_character.skills,
                'background': self.active_character.background,
                'ethical_score': self.active_character.ethical_score,
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
            
            save_path = Path(f'saves/characters/{name}.json')
            if not save_path.exists():
                return {
                    'status': 'error',
                    'message': 'Personagem não encontrado'
                }
                
            with open(save_path, 'r') as f:
                data = json.load(f)
                
            character = Character(
                name=data['name'],
                class_type=CharacterClass[data['class']],
                level=data['level'],
                alignment=Alignment[data['alignment']],
                attributes=data['attributes'],
                skills=data['skills'],
                background=data['background'],
                ethical_score=data['ethical_score'],
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