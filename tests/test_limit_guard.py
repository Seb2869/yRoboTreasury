from ape import reverts, Contract
from pytest import fixture

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
UNIT = 10**18
MAX = 2**256 - 1

@fixture
def robo(project, deployer):
    return project.MockRobo.deploy(sender=deployer)

@fixture
def whitelist(project, deployer, robo):
    return project.Whitelist.deploy(robo, deployer, ZERO_ADDRESS, sender=deployer)

@fixture
def guard(project, deployer, alice, robo, whitelist):
    guard = project.LimitGuard.deploy(robo, whitelist, deployer, sender=deployer)
    guard.set_operator(alice, sender=deployer)
    return guard

@fixture
def token(project, deployer, whitelist, guard):
    token = project.MockToken.deploy(sender=deployer)
    whitelist.set_whitelist(token, sender=deployer)
    guard.set_limit(token, MAX, sender=deployer)
    return token

def test_pull(deployer, alice, guard, token):
    guard.set_limit(token, MAX, sender=deployer)
    assert guard.pull(token, UNIT, sender=alice).return_value == ZERO_ADDRESS

def test_pull_permission(alice, bob, guard, token):
    with reverts():
        guard.pull(token, UNIT, sender=bob)
    guard.pull(token, UNIT, sender=alice)

def test_pull_whitelisted(alice, bob, guard, token):
    with reverts():
        guard.pull(ZERO_ADDRESS, UNIT, sender=bob)
    guard.pull(token, UNIT, sender=alice)

def test_pull_limit(deployer, alice, guard, token):
    guard.set_limit(token, UNIT, sender=deployer)

    with reverts():
        guard.pull(token, UNIT + 1, sender=alice)
    guard.pull(token, UNIT, sender=alice)

def test_pull_cooldown(chain, deployer, alice, guard, token):
    guard.set_cooldown(100, sender=deployer)

    assert guard.last(token) == 0
    ts = chain.pending_timestamp
    guard.pull(token, UNIT, sender=alice)
    assert guard.last(token) == ts

    chain.pending_timestamp = ts + 99
    with reverts():
        guard.pull(token, UNIT, sender=alice)
    chain.pending_timestamp = ts + 100
    guard.pull(token, UNIT, sender=alice)

def test_set_cooldown(deployer, guard):
    assert guard.cooldown() == 0
    guard.set_cooldown(1, sender=deployer)
    assert guard.cooldown() == 1

def test_set_cooldown_permission(deployer, alice, guard):
    with reverts():
        guard.set_cooldown(1, sender=alice)
    guard.set_cooldown(1, sender=deployer)

def test_set_limit(deployer, guard, token):
    assert guard.limits(token) == MAX
    guard.set_limit(token, UNIT, sender=deployer)
    assert guard.limits(token) == UNIT

def test_set_limit_permission(deployer, alice, guard, token):
    with reverts():
        guard.set_limit(token, UNIT, sender=alice)
    guard.set_limit(token, UNIT, sender=deployer)

def test_set_operator(deployer, guard, alice, bob):
    assert guard.operator() == alice
    guard.set_operator(bob, sender=deployer)
    assert guard.operator() == bob

def test_set_operator_permission(deployer, guard, bob):
    with reverts():
        guard.set_operator(bob, sender=bob)
    guard.set_operator(bob, sender=deployer)
