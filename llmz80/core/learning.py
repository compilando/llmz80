"""
Sistema de aprendizaje para LLMZ80.
Guarda ejemplos exitosos, errores comunes y permite mejorar con el tiempo.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SuccessfulExample:
    """Representa un ejemplo exitoso de generación."""
    
    prompt: str
    code: str
    platform: str
    timestamp: str
    compilation_attempts: int
    rating: Optional[int] = None  # 1-5 estrellas, None si no ha sido calificado
    tags: Optional[List[str]] = None  # Tags para búsqueda (e.g., "game", "graphics", "sound")
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SuccessfulExample':
        """Crea instancia desde diccionario."""
        return cls(**data)
    
    def get_hash(self) -> str:
        """Genera hash único basado en prompt y plataforma."""
        content = f"{self.prompt}:{self.platform}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class CommonError:
    """Representa un error común y su solución."""
    
    error_pattern: str  # Patrón del error (para matching)
    error_description: str  # Descripción del error
    solution: str  # Solución aplicada
    platform: str
    occurrences: int  # Número de veces que ha ocurrido
    last_seen: str  # Última vez que se vio
    success_rate: float  # Tasa de éxito de la solución (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommonError':
        """Crea instancia desde diccionario."""
        return cls(**data)
    
    def get_hash(self) -> str:
        """Genera hash único basado en patrón de error."""
        content = f"{self.error_pattern}:{self.platform}"
        return hashlib.md5(content.encode()).hexdigest()


class LearningSystem:
    """Sistema de aprendizaje principal."""
    
    def __init__(self, platform: str, learning_dir: str = "local/learning"):
        """
        Args:
            platform: Plataforma objetivo (spectrum, amstrad_cpc)
            learning_dir: Directorio donde guardar datos de aprendizaje
        """
        self.platform = platform.lower()
        self.learning_dir = Path(learning_dir)
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de datos
        self.successful_examples_file = self.learning_dir / f"{self.platform}_successful_examples.json"
        self.common_errors_file = self.learning_dir / f"{self.platform}_common_errors.json"
        self.stats_file = self.learning_dir / f"{self.platform}_stats.json"
        
        # Cargar datos existentes
        self.successful_examples: Dict[str, SuccessfulExample] = {}
        self.common_errors: Dict[str, CommonError] = {}
        self.stats: Dict[str, Any] = {}
        
        self._load_data()
        
        logger.info(f"✅ Sistema de aprendizaje inicializado para {platform}")
        logger.info(f"  📊 {len(self.successful_examples)} ejemplos exitosos cargados")
        logger.info(f"  📊 {len(self.common_errors)} errores comunes cargados")
    
    def _load_data(self):
        """Carga datos existentes desde archivos JSON."""
        # Cargar ejemplos exitosos
        if self.successful_examples_file.exists():
            try:
                with open(self.successful_examples_file, 'r') as f:
                    data = json.load(f)
                    for hash_key, example_data in data.items():
                        self.successful_examples[hash_key] = SuccessfulExample.from_dict(example_data)
                logger.debug(f"Cargados {len(self.successful_examples)} ejemplos exitosos")
            except Exception as e:
                logger.error(f"Error cargando ejemplos exitosos: {e}")
        
        # Cargar errores comunes
        if self.common_errors_file.exists():
            try:
                with open(self.common_errors_file, 'r') as f:
                    data = json.load(f)
                    for hash_key, error_data in data.items():
                        self.common_errors[hash_key] = CommonError.from_dict(error_data)
                logger.debug(f"Cargados {len(self.common_errors)} errores comunes")
            except Exception as e:
                logger.error(f"Error cargando errores comunes: {e}")
        
        # Cargar estadísticas
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                logger.error(f"Error cargando estadísticas: {e}")
                self.stats = self._init_stats()
        else:
            self.stats = self._init_stats()
    
    def _init_stats(self) -> Dict[str, Any]:
        """Inicializa estructura de estadísticas."""
        return {
            'total_generations': 0,
            'successful_compilations': 0,
            'failed_compilations': 0,
            'average_attempts': 0.0,
            'average_rating': 0.0,
            'total_ratings': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Guarda datos a archivos JSON."""
        try:
            # Guardar ejemplos exitosos
            with open(self.successful_examples_file, 'w') as f:
                data = {k: v.to_dict() for k, v in self.successful_examples.items()}
                json.dump(data, f, indent=2)
            
            # Guardar errores comunes
            with open(self.common_errors_file, 'w') as f:
                data = {k: v.to_dict() for k, v in self.common_errors.items()}
                json.dump(data, f, indent=2)
            
            # Guardar estadísticas
            self.stats['last_updated'] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            
            logger.debug("Datos de aprendizaje guardados correctamente")
        except Exception as e:
            logger.error(f"Error guardando datos de aprendizaje: {e}")
    
    def add_successful_example(self, prompt: str, code: str, compilation_attempts: int = 1, 
                              tags: Optional[List[str]] = None) -> str:
        """
        Añade un ejemplo exitoso a la base de datos.
        
        Args:
            prompt: Prompt del usuario
            code: Código generado exitosamente
            compilation_attempts: Número de intentos hasta compilar
            tags: Tags opcionales para clasificación
            
        Returns:
            Hash del ejemplo añadido
        """
        example = SuccessfulExample(
            prompt=prompt,
            code=code,
            platform=self.platform,
            timestamp=datetime.now().isoformat(),
            compilation_attempts=compilation_attempts,
            tags=tags or []
        )
        
        hash_key = example.get_hash()
        
        # Si ya existe, actualizar
        if hash_key in self.successful_examples:
            existing = self.successful_examples[hash_key]
            # Mantener rating si existe
            if existing.rating is not None:
                example.rating = existing.rating
            logger.info(f"📝 Actualizando ejemplo exitoso existente: {hash_key[:8]}")
        else:
            logger.info(f"✨ Nuevo ejemplo exitoso añadido: {hash_key[:8]}")
        
        self.successful_examples[hash_key] = example
        
        # Actualizar estadísticas
        self.stats['total_generations'] += 1
        self.stats['successful_compilations'] += 1
        
        # Actualizar promedio de intentos
        total_attempts = sum(e.compilation_attempts for e in self.successful_examples.values())
        self.stats['average_attempts'] = total_attempts / len(self.successful_examples)
        
        self._save_data()
        return hash_key
    
    def add_common_error(self, error_pattern: str, error_description: str, 
                        solution: str, success: bool = True):
        """
        Añade o actualiza un error común.
        
        Args:
            error_pattern: Patrón del error para matching
            error_description: Descripción del error
            solution: Solución aplicada
            success: Si la solución fue exitosa
        """
        # Crear objeto temporal para obtener hash
        temp_error = CommonError(
            error_pattern=error_pattern,
            error_description=error_description,
            solution=solution,
            platform=self.platform,
            occurrences=1,
            last_seen=datetime.now().isoformat(),
            success_rate=1.0 if success else 0.0
        )
        
        hash_key = temp_error.get_hash()
        
        if hash_key in self.common_errors:
            # Actualizar error existente
            existing = self.common_errors[hash_key]
            existing.occurrences += 1
            existing.last_seen = datetime.now().isoformat()
            
            # Actualizar tasa de éxito
            total_successes = existing.success_rate * (existing.occurrences - 1)
            if success:
                total_successes += 1
            existing.success_rate = total_successes / existing.occurrences
            
            # Actualizar solución si es mejor
            if success and existing.success_rate < 0.8:
                existing.solution = solution
                logger.info(f"📝 Solución actualizada para error: {hash_key[:8]}")
            
            logger.info(f"📊 Error común actualizado: {hash_key[:8]} (ocurrencias: {existing.occurrences}, éxito: {existing.success_rate:.1%})")
        else:
            # Nuevo error
            self.common_errors[hash_key] = temp_error
            logger.info(f"✨ Nuevo error común registrado: {hash_key[:8]}")
        
        # Actualizar estadísticas
        if not success:
            self.stats['failed_compilations'] += 1
        
        self._save_data()
    
    def rate_example(self, prompt: str, rating: int) -> bool:
        """
        Califica un ejemplo exitoso.
        
        Args:
            prompt: Prompt del ejemplo a calificar
            rating: Calificación de 1-5 estrellas
            
        Returns:
            True si se calificó exitosamente, False si no se encontró el ejemplo
        """
        if not 1 <= rating <= 5:
            logger.warning(f"Rating inválido: {rating}. Debe ser 1-5")
            return False
        
        # Buscar ejemplo por prompt
        for example in self.successful_examples.values():
            if example.prompt == prompt and example.platform == self.platform:
                old_rating = example.rating
                example.rating = rating
                
                # Actualizar estadísticas
                if old_rating is not None:
                    # Re-calcular promedio quitando el rating anterior
                    total = self.stats['average_rating'] * self.stats['total_ratings']
                    total = total - old_rating + rating
                    self.stats['average_rating'] = total / self.stats['total_ratings']
                else:
                    # Nuevo rating
                    total = self.stats['average_rating'] * self.stats['total_ratings']
                    self.stats['total_ratings'] += 1
                    self.stats['average_rating'] = (total + rating) / self.stats['total_ratings']
                
                self._save_data()
                logger.info(f"⭐ Ejemplo calificado con {rating} estrellas")
                return True
        
        logger.warning(f"No se encontró ejemplo para calificar con prompt: '{prompt[:50]}...'")
        return False
    
    def get_best_examples(self, limit: int = 10, min_rating: int = 3) -> List[SuccessfulExample]:
        """
        Obtiene los mejores ejemplos basado en ratings.
        
        Args:
            limit: Número máximo de ejemplos a devolver
            min_rating: Rating mínimo (default: 3)
            
        Returns:
            Lista de ejemplos ordenados por rating
        """
        rated_examples = [e for e in self.successful_examples.values() 
                         if e.rating is not None and e.rating >= min_rating]
        
        # Ordenar por rating (descendente) y luego por intentos (ascendente)
        sorted_examples = sorted(
            rated_examples,
            key=lambda x: (x.rating, -x.compilation_attempts),
            reverse=True
        )
        
        return sorted_examples[:limit]
    
    def get_similar_errors(self, error_text: str, limit: int = 5) -> List[CommonError]:
        """
        Busca errores similares en la base de datos.
        
        Args:
            error_text: Texto del error a buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de errores comunes ordenados por relevancia
        """
        matches = []
        
        for error in self.common_errors.values():
            # Búsqueda simple por substring (puede mejorarse con fuzzy matching)
            if error.error_pattern.lower() in error_text.lower():
                matches.append(error)
        
        # Ordenar por tasa de éxito y frecuencia
        sorted_matches = sorted(
            matches,
            key=lambda x: (x.success_rate, x.occurrences),
            reverse=True
        )
        
        return sorted_matches[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de aprendizaje."""
        return self.stats.copy()

    def get_top_errors(self, limit: int = 5, min_occurrences: int = 2) -> List[CommonError]:
        """Top recurring errors for prompt injection.

        Ranks by occurrences (descending), filters out one-offs and errors
        with no recorded successful fix.
        """
        candidates = [
            e for e in self.common_errors.values()
            if e.occurrences >= min_occurrences and e.success_rate > 0
        ]
        return sorted(
            candidates,
            key=lambda x: (x.occurrences, x.success_rate),
            reverse=True,
        )[:limit]

    def build_avoid_block(self, limit: int = 5) -> str:
        """Format top errors as 'AVOID' block for system prompt.

        Returns empty string if no recurring errors recorded yet.
        """
        top = self.get_top_errors(limit=limit)
        if not top:
            return ""
        lines = [
            "",
            "## RECURRING MISTAKES TO AVOID (from prior failed compilations)",
            "",
        ]
        for i, err in enumerate(top, 1):
            desc = err.error_description.strip().replace('\n', ' ')[:200]
            sol = err.solution.strip().replace('\n', ' ')[:200]
            lines.append(f"{i}. ERROR ({err.occurrences}x): {desc}")
            lines.append(f"   FIX: {sol}")
        lines.append("")
        return "\n".join(lines)
    
    def export_report(self, output_path: Optional[Path] = None) -> str:
        """
        Genera un reporte completo del sistema de aprendizaje.
        
        Args:
            output_path: Ruta donde guardar el reporte (opcional)
            
        Returns:
            Contenido del reporte como string
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"REPORTE DE SISTEMA DE APRENDIZAJE - {self.platform.upper()}")
        lines.append("=" * 70)
        lines.append("")
        
        # Estadísticas generales
        lines.append("ESTADÍSTICAS GENERALES")
        lines.append("-" * 70)
        lines.append(f"Total de generaciones: {self.stats['total_generations']}")
        lines.append(f"Compilaciones exitosas: {self.stats['successful_compilations']}")
        lines.append(f"Compilaciones fallidas: {self.stats['failed_compilations']}")
        
        if self.stats['total_generations'] > 0:
            success_rate = self.stats['successful_compilations'] / self.stats['total_generations'] * 100
            lines.append(f"Tasa de éxito: {success_rate:.1f}%")
        
        lines.append(f"Promedio de intentos: {self.stats['average_attempts']:.1f}")
        
        if self.stats['total_ratings'] > 0:
            lines.append(f"Rating promedio: {self.stats['average_rating']:.1f}/5.0 ({self.stats['total_ratings']} ratings)")
        
        lines.append("")
        
        # Mejores ejemplos
        best_examples = self.get_best_examples(limit=5)
        if best_examples:
            lines.append("TOP 5 EJEMPLOS MEJOR CALIFICADOS")
            lines.append("-" * 70)
            for i, example in enumerate(best_examples, 1):
                lines.append(f"{i}. Rating: {example.rating}⭐ | Intentos: {example.compilation_attempts}")
                lines.append(f"   Prompt: {example.prompt[:60]}...")
                lines.append("")
        
        # Errores más comunes
        top_errors = sorted(self.common_errors.values(), key=lambda x: x.occurrences, reverse=True)[:5]
        if top_errors:
            lines.append("TOP 5 ERRORES MÁS COMUNES")
            lines.append("-" * 70)
            for i, error in enumerate(top_errors, 1):
                lines.append(f"{i}. {error.error_description}")
                lines.append(f"   Ocurrencias: {error.occurrences} | Tasa de éxito: {error.success_rate:.1%}")
                lines.append(f"   Solución: {error.solution[:60]}...")
                lines.append("")
        
        lines.append("=" * 70)
        lines.append(f"Última actualización: {self.stats['last_updated']}")
        lines.append("=" * 70)
        
        report = "\n".join(lines)
        
        # Guardar si se especificó ruta
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write(report)
                logger.info(f"📄 Reporte guardado en: {output_path}")
            except Exception as e:
                logger.error(f"Error guardando reporte: {e}")
        
        return report
