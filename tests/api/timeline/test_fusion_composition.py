"""Fusion Dynamic Composition Tests

Tests for planning and executing Fusion compositions with
effect chains, transitions, and nested compositions.
"""
import pytest
# FIXME: src.agent removed
# FIXME: src.agent removed


class TestFusionCompositionPlanning:
    """Tests for Fusion composition planning"""
    
    def test_plan_basic_fusion_composition(self):
        """Plan basic Fusion composition from shots"""
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 2.0, 'shot_type': 'wide'},
            {'id': 's2', 'in': 2.0, 'out': 4.0, 'shot_type': 'close'},
        ]
        
        plan = plan_fusion_composition(
            'Test scene',
            shots,
            style='cinematic'
        )
        
        assert plan['summary'] is not None
        assert plan['style'] == 'cinematic'
        assert len(plan['layers']) == 2
        assert plan['total_duration'] == 4.0
        assert 'transitions' in plan
        assert 'metadata' in plan
    
    def test_plan_with_3d_effects(self):
        """Plan composition with 3D effects enabled"""
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 3.0, 'shot_type': 'title'},
        ]
        
        plan = plan_fusion_composition(
            'Title animation',
            shots,
            style='modern',
            enable_3d=True
        )
        
        assert plan['enable_3d'] is True
        assert len(plan['layers']) == 1
        # Layer should have 3D transform with z-axis
        layer = plan['layers'][0]
        assert layer['transform']['position']['z'] is not None
    
    def test_effect_presets_available(self):
        """Verify all effect presets are available"""
        for preset_name in EFFECT_PRESETS:
            preset = EFFECT_PRESETS[preset_name]
            assert 'description' in preset
            assert 'effects' in preset
            assert 'duration' in preset
    
    def test_plan_different_styles(self):
        """Test planning with different composition styles"""
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 2.0, 'shot_type': 'generic'},
        ]
        
        for style in ['modern', 'cinematic', 'abstract', 'minimal']:
            plan = plan_fusion_composition(
                'Test',
                shots,
                style=style
            )
            
            assert plan['style'] == style
            assert len(plan['layers']) > 0
            layer = plan['layers'][0]
            # Should have effects for each style
            assert len(layer['effects']) > 0 or style == 'minimal'
    
    def test_transition_generation(self):
        """Test automatic transition generation between layers"""
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'wide'},
            {'id': 's2', 'in': 1.0, 'out': 2.0, 'shot_type': 'close'},
            {'id': 's3', 'in': 2.0, 'out': 3.0, 'shot_type': 'action'},
        ]
        
        plan = plan_fusion_composition('Test', shots)
        
        # Should have n-1 transitions for n layers
        assert len(plan['transitions']) == 2
        
        # Check transition structure
        for trans in plan['transitions']:
            assert 'from_layer' in trans
            assert 'to_layer' in trans
            assert 'type' in trans
            assert 'duration' in trans
    
    def test_effect_intensity_impact(self):
        """Test effect intensity parameter impact"""
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'generic'},
        ]
        
        plan_low = plan_fusion_composition(
            'Test',
            shots,
            effect_intensity=0.3
        )
        
        plan_high = plan_fusion_composition(
            'Test',
            shots,
            effect_intensity=0.9
        )
        
        # Transitions should have different durations based on intensity
        trans_low = plan_low['transitions'][0] if plan_low['transitions'] else {}
        trans_high = plan_high['transitions'][0] if plan_high['transitions'] else {}
        
        if trans_low and trans_high:
            assert trans_low['duration'] < trans_high['duration']
    
    def test_nested_composition_identification(self):
        """Test identification of shots that should be nested comps"""
        # Many shots of same type should be grouped
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'action'},
            {'id': 's2', 'in': 1.0, 'out': 2.0, 'shot_type': 'action'},
            {'id': 's3', 'in': 2.0, 'out': 3.0, 'shot_type': 'action'},
            {'id': 's4', 'in': 3.0, 'out': 4.0, 'shot_type': 'title'},
        ]
        
        plan = plan_fusion_composition('Test', shots)
        
        # Should identify action shots as nested comp
        assert len(plan['nested_comps']) > 0
    
    def test_composition_metadata(self):
        """Test composition metadata generation"""
        shots = [
            {'id': f's{i}', 'in': float(i), 'out': float(i + 1), 'shot_type': 'generic'}
            for i in range(5)
        ]
        
        plan = plan_fusion_composition('Test', shots, enable_3d=True)
        
        metadata = plan['metadata']
        assert metadata['shot_count'] == 5
        assert metadata['layer_count'] == 5
        assert 'estimated_complexity' in metadata
        assert metadata['estimated_complexity'] in ['low', 'medium', 'high', 'very_high']


class TestFusionExecutor:
    """Tests for Fusion composition executor"""
    
    def test_create_fusion_page(self):
        """Test Fusion page creation/initialization"""
        result = create_fusion_page()
        
        assert 'success' in result
        assert 'page' in result
    
    def test_create_effect_chain(self):
        """Test effect chain creation"""
        effects = [
            {'name': 'Curves', 'params': {'curve_type': 'S-curve'}},
            {'name': 'Blur', 'params': {'radius': 3.0}},
        ]
        
        result = create_effect_chain(effects, 'test_layer')
        
        assert result['success'] is True
        assert result['effects_added'] == 2
        assert 'chain_id' in result
    
    def test_add_transition_between_layers(self):
        """Test adding transition between layers"""
        result = add_transition(
            transition_type='dissolve',
            duration=0.5,
            from_layer=0,
            to_layer=1
        )
        
        assert result['success'] is True
        assert result['type'] == 'dissolve'
        assert result['duration'] == 0.5
        assert 'transition_id' in result
    
    def test_add_different_transition_types(self):
        """Test different transition types"""
        transition_types = [
            'dissolve', 'wipe', 'blur', 'fade', 'zoom'
        ]
        
        for trans_type in transition_types:
            result = add_transition(
                transition_type=trans_type,
                duration=0.3
            )
            
            assert result['success'] is True
            assert result['type'] == trans_type
    
    def test_create_nested_composition(self):
        """Test nested composition creation"""
        result = create_nested_composition(
            'nested_comp_1',
            [0, 1, 2]
        )
        
        assert result['success'] is True
        assert result['comp_name'] == 'nested_comp_1'
        assert result['layers'] == [0, 1, 2]
        assert 'comp_id' in result
    
    def test_get_fusion_status(self):
        """Test getting Fusion composition status"""
        result = get_fusion_composition_status()
        
        assert 'success' in result
        assert 'status' in result


class TestEffectOptimization:
    """Tests for effect chain optimization"""
    
    def test_optimize_for_performance(self):
        """Test effect optimization for performance"""
        effects = [
            {'name': 'Curves', 'params': {'value': 1.0}},
            {'name': 'Curves', 'params': {'value': 0.8}},
            {'name': 'Blur', 'params': {'radius': 5.0}},
        ]
        
        optimized = optimize_effect_chain(effects, 'performance')
        
        # Should remove duplicates in performance mode
        effect_names = [e['name'] for e in optimized]
        assert effect_names.count('Curves') == 1
    
    def test_optimize_for_quality(self):
        """Test effect optimization for quality"""
        effects = [
            {'name': 'Levels', 'params': {'value': 1.0}},
            {'name': 'Curves', 'params': {'value': 1.0}},
        ]
        
        optimized = optimize_effect_chain(effects, 'quality')
        
        # Should keep all effects in quality mode
        assert len(optimized) == 2
    
    def test_optimize_balanced_mode(self):
        """Test balanced optimization"""
        effects = [
            {'name': 'Blur', 'params': {'radius': 3.0}},
            {'name': 'Levels', 'params': {'balance': 0.5}},
            {'name': 'Transform', 'params': {'scale': 1.0}},
        ]
        
        optimized = optimize_effect_chain(effects, 'balanced')
        
        # Should reorder effects by efficiency
        assert len(optimized) == 3
        # Levels should come before Blur in GPU efficiency order
        level_idx = next(i for i, e in enumerate(optimized) if e['name'] == 'Levels')
        blur_idx = next(i for i, e in enumerate(optimized) if e['name'] == 'Blur')
        assert level_idx < blur_idx


class TestFusionIntegration:
    """Integration tests for Fusion composition pipeline"""
    
    def test_full_composition_pipeline(self):
        """Test full Fusion composition creation pipeline"""
        # 1. Plan composition
        shots = [
            {'id': 's1', 'in': 0.0, 'out': 2.0, 'shot_type': 'wide'},
            {'id': 's2', 'in': 2.0, 'out': 4.0, 'shot_type': 'close'},
        ]
        
        plan = plan_fusion_composition('Integration test', shots, style='cinematic')
        assert plan['summary'] is not None
        
        # 2. Create Fusion page
        page_result = create_fusion_page()
        assert 'page' in page_result
        
        # 3. Create effect chains
        for layer in plan['layers']:
            if layer['effects']:
                chain_result = create_effect_chain(
                    layer['effects'],
                    layer['name']
                )
                assert chain_result['success'] is True
        
        # 4. Add transitions
        for trans in plan['transitions']:
            trans_result = add_transition(
                transition_type=trans['type'],
                duration=trans['duration'],
                from_layer=trans['from_layer'],
                to_layer=trans['to_layer'],
                parameters=trans['parameters']
            )
            assert trans_result['success'] is True
    
    def test_complex_composition_with_nested_comps(self):
        """Test complex composition with nested compositions"""
        # Create many shots of same type to trigger nesting
        shots = [
            {
                'id': f's{i}',
                'in': float(i),
                'out': float(i + 1),
                'shot_type': 'action' if i < 5 else 'title'
            }
            for i in range(10)
        ]
        
        plan = plan_fusion_composition(
            'Complex scene',
            shots,
            style='modern',
            enable_3d=True
        )
        
        # Should have nested compositions
        assert len(plan['nested_comps']) > 0
        
        # Create nested comps
        for nested in plan['nested_comps']:
            result = create_nested_composition(
                nested['name'],
                list(range(len(nested['shots'])))
            )
            assert result['success'] is True
