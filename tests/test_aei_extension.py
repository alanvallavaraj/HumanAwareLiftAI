import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from simulator import Passenger,Lift,Scenario
from aei_extension import Policy,simulate,pickup,selection,POLICIES
class Checks(unittest.TestCase):
 def test_dwell_completion_and_no_movement_before_boarding(self):
  sc=Scenario(2,1,200,'mixed',.1,.2,.08,duration=20)
  p=Passenger(0,0,1,0,True,False);r,ps=simulate(sc,Policy('dwell',fixed_dwell=5,transfer_dwell=1),0,{0:[p]})
  self.assertEqual(p.boarded_time,6);self.assertEqual(p.alighted_time,13);self.assertEqual(r['all_restricted_wait_900'],6)
 def test_zero_delay_and_served_target_cleared(self):
  p=Passenger(0,0,1,0,True,False);r,_=simulate(Scenario(2,1,200,'mixed',.1,.2,.08,duration=20),Policy('ref'),0,{0:[p]})
  self.assertEqual((p.boarded_time,p.alighted_time),(0,1));self.assertEqual(r['distance'],1)
 def test_priority_boarding_is_independent(self):
  general=Passenger(0,0,1,0,False,False);priority=Passenger(1,0,1,1,True,False);l=Lift(0)
  self.assertEqual(selection(l,[],[general,priority],Policy('r'))[0].pid,0)
  self.assertEqual(selection(l,[],[general,priority],Policy('b',boarding=True))[0].pid,1)
 def test_pickup_exception(self):
  load=[object() for _ in range(12)];q=[Passenger(0,0,1,0,True,False)]
  self.assertFalse(pickup(load,q,Policy('r')));self.assertTrue(pickup(load,q,Policy('e',exception=True)))
 def test_last_horizon_events_are_censored(self):
  sc=Scenario(2,1,200,'mixed',.1,.2,.08,duration=20);p=Passenger(0,0,1,19,True,False)
  r,_=simulate(sc,Policy('slow',fixed_dwell=1000,transfer_dwell=1),0,{19:[p]})
  self.assertIsNone(p.boarded_time);self.assertEqual(r['all_restricted_wait_900'],900)
 def test_full_grid(self):self.assertEqual(len(POLICIES)*108*12,16848)
if __name__=='__main__':unittest.main()
