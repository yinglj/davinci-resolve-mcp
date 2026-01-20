"""Fusion Dynamic Composition Planning

Intelligent composition of Fusion pages with:
- Multi-layer effect chains
- Dynamic transitions and timing
- Nested comp management
- Auto-layout and parameter optimization
"""
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Effect presets for common composition patterns
EFFECT_PRESETS = {
    'reveal': {
        'description': 'Transition reveal effect with mask animation',
        'effects': ['Mask', 'Transform'],
        'duration': 0.5,
    },
    'blur_transition': {
        'description': 'Gaussian blur with Z-depth transition',
        'effects': ['Blur', 'Transform'],
        'duration': 0.3,
    },
    'color_correction_chain': {
        'description': 'Color grading with curves and levels',
        'effects': ['Curves', 'Levels', 'Hue Shift'],
        'duration': 0.0,
    },
    'particle_burst': {
        'description': 'Particle system burst effect',
        'effects': ['Particle Emitter', 'Motion Blur'],
        'duration': 1.0,
    },
    'morphing_shape': {
        'description': 'Shape morphing with path animation',
        'effects': ['Shape', 'Polygon', 'Transform'],
        'duration': 1.0,
    },
    'depth_of_field': {
        'description': '3D depth-of-field camera effect',
        'effects': ['Camera', 'Defocus'],
        'duration': 0.0,
    },
}


def plan_fusion_composition(
    script_summary: str,
    shot_list: List[Dict[str, Any]],
    style: str = 'modern',
    effect_intensity: float = 0.7,
    enable_3d: bool = False,
) -> Dict[str, Any]:
    """
    Plan a Fusion composition based on script and shots.
    
    Args:
        script_summary: Summary of scene/script for context
        shot_list: List of shots with timing and metadata
        style: Composition style ('modern', 'cinematic', 'abstract', 'minimal')
        effect_intensity: Strength of effects 0.0-1.0
        enable_3d: Whether to enable 3D effects
    
    Returns:
        Composition plan with layers, effects, transitions, and timing
    """
    plan = {
        'summary': f'Fusion composition: {style} style for {len(shot_list)} shots',
        'style': style,
        'effect_intensity': effect_intensity,
        'enable_3d': enable_3d,
        'layers': [],
        'transitions': [],
        'nested_comps': [],
        'total_duration': 0.0,
        'metadata': {},
    }
    
    # Calculate composition duration
    total_duration = 0.0
    for shot in shot_list:
        if 'out' in shot and 'in' in shot:
            total_duration = max(total_duration, shot['out'])
    plan['total_duration'] = total_duration
    
    # Create layers based on shots
    for i, shot in enumerate(shot_list):
        layer = _create_fusion_layer(i, shot, style, enable_3d)
        plan['layers'].append(layer)
    
    # Add transitions between layers
    plan['transitions'] = _generate_transitions(
        len(shot_list),
        style,
        effect_intensity
    )
    
    # Determine which layers should be nested comps
    plan['nested_comps'] = _identify_nested_comps(shot_list, style)
    
    plan['metadata'] = {
        'shot_count': len(shot_list),
        'layer_count': len(plan['layers']),
        'transition_count': len(plan['transitions']),
        'estimated_complexity': _estimate_complexity(
            len(shot_list),
            effect_intensity,
            enable_3d
        ),
    }
    
    return plan


def _create_fusion_layer(
    layer_index: int,
    shot: Dict[str, Any],
    style: str,
    enable_3d: bool,
) -> Dict[str, Any]:
    """Create a single Fusion layer for a shot."""
    shot_type = shot.get('shot_type', 'generic')
    
    # Select effects based on shot type and style
    effects = _select_effects_for_shot(shot_type, style, enable_3d)
    
    layer = {
        'index': layer_index,
        'name': f"Layer_{layer_index:02d}_{shot_type}",
        'in_time': shot.get('in', 0.0),
        'out_time': shot.get('out', 1.0),
        'duration': shot.get('out', 1.0) - shot.get('in', 0.0),
        'effects': effects,
        'transform': {
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0 if enable_3d else None},
            'rotation': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'scale': {'x': 1.0, 'y': 1.0, 'z': 1.0},
        },
        'blend_mode': _select_blend_mode(style),
        'opacity': 1.0,
        'metadata': {
            'shot_id': shot.get('id'),
            'shot_summary': shot.get('summary', ''),
            'effect_intensity': 0.7,
        },
    }
    
    return layer


def _select_effects_for_shot(
    shot_type: str,
    style: str,
    enable_3d: bool,
) -> List[Dict[str, Any]]:
    """Select appropriate effects for a shot type and style."""
    effects = []
    
    # Base effects by style
    if style == 'cinematic':
        effects.append({'name': 'Curves', 'params': {'curve_type': 'S-curve'}})
        effects.append({'name': 'Levels', 'params': {'black_level': 5, 'white_level': 245}})
        
    elif style == 'abstract':
        effects.append({'name': 'Blur', 'params': {'radius': 3.0}})
        if enable_3d:
            effects.append({'name': 'Displace', 'params': {'intensity': 0.5}})
    
    elif style == 'minimal':
        effects.append({'name': 'Levels', 'params': {'auto_balance': True}})
    
    elif style == 'modern':
        effects.append({'name': 'Curves', 'params': {'curve_type': 'linear'}})
        effects.append({'name': 'Hue Shift', 'params': {'hue_rotation': 0.0}})
    
    # Shot-specific effects
    if shot_type == 'action':
        effects.append({'name': 'Motion Blur', 'params': {'samples': 16}})
    elif shot_type == 'text':
        effects.append({'name': 'Glow', 'params': {'radius': 2.0}})
    elif shot_type == 'title':
        effects.append({'name': 'Shadow', 'params': {'angle': 45.0, 'distance': 5.0}})
    
    # 3D effects if enabled
    if enable_3d:
        effects.append({'name': 'Camera', 'params': {'fov': 50.0}})
        effects.append({'name': 'Lighting', 'params': {'ambient': 0.3}})
    
    return effects


def _select_blend_mode(style: str) -> str:
    """Select blend mode based on style."""
    blend_modes = {
        'cinematic': 'Normal',
        'abstract': 'Add',
        'minimal': 'Normal',
        'modern': 'Screen',
    }
    return blend_modes.get(style, 'Normal')


def _generate_transitions(
    layer_count: int,
    style: str,
    effect_intensity: float,
) -> List[Dict[str, Any]]:
    """Generate transitions between layers."""
    transitions = []
    
    for i in range(layer_count - 1):
        transition_type = _select_transition_type(style, i)
        
        transition = {
            'from_layer': i,
            'to_layer': i + 1,
            'type': transition_type,
            'duration': 0.3 + (effect_intensity * 0.2),
            'easing': 'ease-in-out',
            'parameters': _get_transition_parameters(transition_type, effect_intensity),
        }
        transitions.append(transition)
    
    return transitions


def _select_transition_type(style: str, index: int) -> str:
    """Select transition type based on style and index."""
    styles = {
        'cinematic': ['dissolve', 'blur_transition', 'fade'],
        'abstract': ['wipe', 'morph', 'particle_burst'],
        'minimal': ['dissolve', 'fade'],
        'modern': ['wipe', 'zoom_transition', 'slide'],
    }
    
    style_transitions = styles.get(style, ['dissolve', 'fade'])
    return style_transitions[index % len(style_transitions)]


def _get_transition_parameters(
    transition_type: str,
    effect_intensity: float,
) -> Dict[str, Any]:
    """Get parameters for a transition type."""
    params = {
        'dissolve': {'softness': effect_intensity * 0.5},
        'fade': {'easing': 'ease-in-out'},
        'blur_transition': {'blur_amount': effect_intensity * 10.0},
        'wipe': {'angle': 45.0, 'softness': effect_intensity * 0.3},
        'zoom_transition': {'scale_from': 0.5, 'scale_to': 1.0},
        'slide': {'direction': 'right', 'distance': 100.0},
        'morph': {'morphing_intensity': effect_intensity},
        'particle_burst': {'particle_count': int(effect_intensity * 500)},
    }
    return params.get(transition_type, {})


def _identify_nested_comps(
    shot_list: List[Dict[str, Any]],
    style: str,
) -> List[Dict[str, Any]]:
    """
    Identify shots that should be nested into sub-compositions.
    
    Criteria:
    - Complex effect chains (many effects)
    - Long duration requiring temporal organization
    - Similar shot types can be grouped
    """
    nested_comps = []
    
    if len(shot_list) < 2:
        return nested_comps
    
    # Group consecutive shots of same type
    current_group = [shot_list[0]]
    
    for i in range(1, len(shot_list)):
        shot = shot_list[i]
        prev_shot = shot_list[i - 1]
        
        # Start new group if shot type changes or duration > 3s
        duration = shot.get('out', 1.0) - shot.get('in', 0.0)
        if (shot.get('shot_type') != prev_shot.get('shot_type') or
            duration > 3.0):
            if len(current_group) > 1:
                nested_comps.append({
                    'shots': current_group,
                    'name': f"Comp_{current_group[0].get('shot_type', 'group')}",
                    'type': 'grouped',
                })
            current_group = [shot]
        else:
            current_group.append(shot)
    
    # Add final group if needed
    if len(current_group) > 1:
        nested_comps.append({
            'shots': current_group,
            'name': f"Comp_{current_group[0].get('shot_type', 'group')}",
            'type': 'grouped',
        })
    
    return nested_comps


def _estimate_complexity(
    shot_count: int,
    effect_intensity: float,
    enable_3d: bool,
) -> str:
    """Estimate complexity level of composition."""
    complexity_score = (
        shot_count * 0.2 +
        effect_intensity * 30.0 +
        (20.0 if enable_3d else 0.0)
    )
    
    if complexity_score < 15:
        return 'low'
    elif complexity_score < 30:
        return 'medium'
    elif complexity_score < 50:
        return 'high'
    else:
        return 'very_high'


def optimize_effect_chain(
    effects: List[Dict[str, Any]],
    target_performance_tier: str = 'balanced',
) -> List[Dict[str, Any]]:
    """
    Optimize effect chain for performance or quality.
    
    Args:
        effects: List of effects in the chain
        target_performance_tier: 'performance', 'balanced', 'quality'
    
    Returns:
        Optimized effect chain
    """
    optimized = []
    
    # Remove duplicate effects if in performance mode
    if target_performance_tier == 'performance':
        seen_effects = set()
        for effect in effects:
            if effect['name'] not in seen_effects:
                optimized.append(effect)
                seen_effects.add(effect['name'])
        # Reduce quality of remaining effects
        for effect in optimized:
            if 'params' in effect:
                for key, value in effect['params'].items():
                    if isinstance(value, float):
                        effect['params'][key] = value * 0.7
    else:
        # In balanced or quality mode, keep all effects but reorder by GPU efficiency
        effect_order = ['Levels', 'Curves', 'Transform', 'Blur']
        for effect_name in effect_order:
            for effect in effects:
                if effect['name'] == effect_name:
                    optimized.append(effect)
                    break
        
        for effect in effects:
            if effect not in optimized:
                optimized.append(effect)
    
    return optimized
