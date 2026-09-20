from conftest import CONTRACT
NODES=['database','api','checkout'];EDGES=[[0,1],[1,2]]
def setup(vm,deploy,a,b):
 vm.warp('2035-01-01T00:00:00+00:00');vm.sender=a;c=deploy(CONTRACT);c.register_topology('shop-2','0x'+b.hex(),'Checkout service graph',NODES,EDGES,600);return c
def plan(vm,order='[2,1,0]'):
 vm.mock_web(r'incident\.example',{'status':200,'body':'database, api and checkout affected'});vm.mock_web(r'runbook\.example',{'status':200,'body':'rollback checkout then api then database'});vm.mock_llm(r'.*RollbackTopology plan extraction.*','{"impacted_indexes":[0,1,2],"rollback_order":'+order+',"note":"Rollback proceeds from dependent edge to dependency."}')
def test_safe_reverse_dependency_plan(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;plan(direct_vm);c.propose_rollback('shop-2','https://incident.example/42','https://runbook.example/42');r=c.get_topology('shop-2');assert r['state']=='PLANNED' and r['unsafe_edges']==[]
def test_dependency_first_plan_is_blocked(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;plan(direct_vm,'[0,1,2]');c.propose_rollback('shop-2','https://incident.example/42','https://runbook.example/42');assert c.get_topology('shop-2')['unsafe_edges']==[[0,1],[1,2]]
def test_execution_partitions_all_impacted_nodes(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;plan(direct_vm);c.propose_rollback('shop-2','https://incident.example/42','https://runbook.example/42');direct_vm.clear_mocks();direct_vm.mock_web(r'evidence\.example',{'status':200,'body':'all three rollback checks passed'});direct_vm.mock_llm(r'.*RollbackTopology execution audit.*','{"completed_indexes":[0,1,2],"failed_indexes":[]}');c.record_execution('shop-2','https://evidence.example/final');assert c.get_topology('shop-2')['state']=='RESTORED'
def test_validator_rejects_omitted_node(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);plan(direct_vm);x=c.maps['SHOP-2'];r=c._plan(x,'https://incident.example/42','https://runbook.example/42');assert direct_vm.run_validator(leader_result=r) is True;f=dict(r);f['rollback_order']=[2,1];assert direct_vm.run_validator(leader_result=f) is False
def test_responder_and_origins_enforced(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);plan(direct_vm)
 with direct_vm.expect_revert('responder'):c.propose_rollback('shop-2','https://incident.example/42','https://runbook.example/42')
 direct_vm.sender=direct_bob
 with direct_vm.expect_revert('independent'):c.propose_rollback('shop-2','https://incident.example/42','https://incident.example/runbook')
