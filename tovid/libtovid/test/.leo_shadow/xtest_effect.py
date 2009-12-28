#@+leo-ver=4-thin
#@+node:eric.20090722212922.3362:@shadow test_effect.py
#@+others
#@+node:eric.20090722212922.3363:test_effect declarations
import unittest
import math
# Fetch in subdir
import sys
sys.path.insert(0, '..')
# Get modules to test
from render.drawing import Drawing
from libtovid.render import effect
from libtovid.render.animation import Keyframe

#@-node:eric.20090722212922.3363:test_effect declarations
#@+node:eric.20090722212922.3364:class TestEffect
class TestEffect(unittest.TestCase):
    """Test the Effect class"""
    #@    @+others
    #@+node:eric.20090722212922.3365:test_effect
    def test_effect(self):
        pass


    #@-node:eric.20090722212922.3365:test_effect
    #@+node:eric.20090722212922.3366:test_instantiate_effects
    def test_instantiate_effects(self):
        e1 = effect.Effect(0, 10)
        e2 = effect.Movement(0, 10, (10, 10), (20, 20))
        e3 = effect.Translate(0, 10, (-10, -10))
        e4 = effect.FadeInOut(0, 10, 2)
        k = [Keyframe(0, 0.0),
             Keyframe(10, 1.0),
             Keyframe(30, 0.0)]
        e5 = effect.Fade(k, method='cosine')


    #@-node:eric.20090722212922.3366:test_instantiate_effects
    #@-others
#@-node:eric.20090722212922.3364:class TestEffect
#@-others
if __name__ == '__main__':
    unittest.main()

#@-node:eric.20090722212922.3362:@shadow test_effect.py
#@-leo
