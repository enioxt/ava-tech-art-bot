from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class Race(Enum):
    NORD = "Nord"
    IMPERIAL = "Imperial"
    BRETON = "Breton"
    REDGUARD = "Redguard"
    ALTMER = "High Elf"
    BOSMER = "Wood Elf"
    DUNMER = "Dark Elf"
    ORSIMER = "Orc"
    KHAJIIT = "Khajiit"
    ARGONIAN = "Argonian"

class SkillTree(Enum):
    # Guerreiro
    ONE_HANDED = "One-Handed"
    TWO_HANDED = "Two-Handed"
    ARCHERY = "Archery"
    BLOCK = "Block"
    HEAVY_ARMOR = "Heavy Armor"
    
    # Ladrão
    LIGHT_ARMOR = "Light Armor"
    SNEAK = "Sneak"
    LOCKPICKING = "Lockpicking"
    PICKPOCKET = "Pickpocket"
    SPEECH = "Speech"
    
    # Mago
    DESTRUCTION = "Destruction"
    CONJURATION = "Conjuration"
    RESTORATION = "Restoration"
    ALTERATION = "Alteration"
    ENCHANTING = "Enchanting"
    ILLUSION = "Illusion"

@dataclass
class Character:
    name: str
    race: Race
    level: int
    skills: Dict[SkillTree, int]
    perks: List[str]
    equipment: Dict[str, str]
    created_at: datetime
    ethical_score: float
    dragon_souls: int

class SkyrimProfile:
    def __init__(self):
        self.characters: List[Character] = []
        self.active_character: Optional[Character] = None
        self.ethical_threshold = 0.7
        
    def create_character(self,
                        name: str,
                        race: Race) -> Character:
        """Cria novo personagem."""
        character = Character(
            name=name,
            race=race,
            level=1,
            skills={skill: 15 for skill in SkillTree},
            perks=[],
            equipment={
                'Weapon': 'Iron Dagger',
                'Armor': 'Ragged Robes',
                'Amulet': None,
                'Ring': None
            },
            created_at=datetime.now(),
            ethical_score=1.0,
            dragon_souls=0
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
        
    def improve_skill(self, skill: SkillTree, amount: int = 1) -> bool:
        """Melhora habilidade."""
        if not self.active_character:
            return False
            
        current = self.active_character.skills[skill]
        if current < 100:  # Max skill level
            self.active_character.skills[skill] = min(100, current + amount)
            return True
            
        return False
        
    def add_perk(self, perk: str) -> bool:
        """Adiciona vantagem."""
        if not self.active_character:
            return False
            
        if perk not in self.active_character.perks:
            self.active_character.perks.append(perk)
            return True
            
        return False
        
    def equip_item(self, slot: str, item: str) -> bool:
        """Equipa item."""
        if not self.active_character:
            return False
            
        valid_slots = ['Weapon', 'Armor', 'Amulet', 'Ring']
        if slot in valid_slots:
            self.active_character.equipment[slot] = item
            return True
            
        return False
        
    def add_dragon_soul(self) -> bool:
        """Adiciona alma de dragão."""
        if not self.active_character:
            return False
            
        self.active_character.dragon_souls += 1
        return True
        
    def get_character_info(self) -> Optional[Dict]:
        """Retorna informações do personagem."""
        if not self.active_character:
            return None
            
        return {
            'name': self.active_character.name,
            'race': self.active_character.race.value,
            'level': self.active_character.level,
            'skills': {k.value: v for k, v in self.active_character.skills.items()},
            'perks': self.active_character.perks,
            'equipment': self.active_character.equipment,
            'ethical_score': self.active_character.ethical_score,
            'dragon_souls': self.active_character.dragon_souls
        }
        
    def get_skill_recommendations(self) -> List[str]:
        """Retorna recomendações de habilidades."""
        if not self.active_character:
            return []
            
        recommendations = []
        skills = self.active_character.skills
        
        # Guerreiro
        warrior_skills = [
            SkillTree.ONE_HANDED,
            SkillTree.TWO_HANDED,
            SkillTree.HEAVY_ARMOR
        ]
        
        # Mago
        mage_skills = [
            SkillTree.DESTRUCTION,
            SkillTree.CONJURATION,
            SkillTree.RESTORATION
        ]
        
        # Ladrão
        thief_skills = [
            SkillTree.SNEAK,
            SkillTree.LOCKPICKING,
            SkillTree.LIGHT_ARMOR
        ]
        
        # Analisa tendências
        warrior_avg = sum(skills[s] for s in warrior_skills) / len(warrior_skills)
        mage_avg = sum(skills[s] for s in mage_skills) / len(mage_skills)
        thief_avg = sum(skills[s] for s in thief_skills) / len(thief_skills)
        
        # Gera recomendações
        if warrior_avg > mage_avg and warrior_avg > thief_avg:
            recommendations.extend([
                "Foque em combate corpo a corpo",
                "Melhore sua armadura pesada",
                "Treine bloqueio com escudo"
            ])
        elif mage_avg > warrior_avg and mage_avg > thief_avg:
            recommendations.extend([
                "Estude novos feitiços",
                "Aprimore encantamentos",
                "Pratique restauração"
            ])
        else:
            recommendations.extend([
                "Aprimore furtividade",
                "Pratique arrombamento",
                "Melhore armadura leve"
            ])
            
        return recommendations
        
    def check_ethical_actions(self) -> Dict:
        """Verifica ações éticas."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        ethical_score = self.active_character.ethical_score
        
        # Analisa equipamento
        has_daedric = any('Daedric' in item 
                         for item in self.active_character.equipment.values() 
                         if item)
                         
        # Analisa habilidades
        high_sneak = self.active_character.skills[SkillTree.SNEAK] > 75
        high_pickpocket = self.active_character.skills[SkillTree.PICKPOCKET] > 75
        
        warnings = []
        if has_daedric and ethical_score > 0.8:
            warnings.append("Uso de itens daédricos com alto score ético")
        if (high_sneak or high_pickpocket) and ethical_score > 0.9:
            warnings.append("Habilidades furtivas com alto score ético")
            
        return {
            'status': 'warning' if warnings else 'ok',
            'message': warnings if warnings else ['Ações consistentes com ética']
        }
        
    def save_character(self) -> Dict:
        """Salva estado do personagem."""
        if not self.active_character:
            return {'status': 'error', 'message': 'Nenhum personagem ativo'}
            
        try:
            import json
            from pathlib import Path
            
            save_dir = Path('saves/skyrim')
            save_dir.mkdir(parents=True, exist_ok=True)
            
            character_data = {
                'name': self.active_character.name,
                'race': self.active_character.race.name,
                'level': self.active_character.level,
                'skills': {k.name: v for k, v in self.active_character.skills.items()},
                'perks': self.active_character.perks,
                'equipment': self.active_character.equipment,
                'ethical_score': self.active_character.ethical_score,
                'dragon_souls': self.active_character.dragon_souls,
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
            
            save_path = Path(f'saves/skyrim/{name}.json')
            if not save_path.exists():
                return {
                    'status': 'error',
                    'message': 'Personagem não encontrado'
                }
                
            with open(save_path, 'r') as f:
                data = json.load(f)
                
            character = Character(
                name=data['name'],
                race=Race[data['race']],
                level=data['level'],
                skills={SkillTree[k]: v for k, v in data['skills'].items()},
                perks=data['perks'],
                equipment=data['equipment'],
                ethical_score=data['ethical_score'],
                dragon_souls=data['dragon_souls'],
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