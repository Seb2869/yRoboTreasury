# pragma version 0.3.10
# pragma optimize gas
# pragma evm-version cancun
"""
@title Guard
@author Yearn Finance
@license GNU AGPLv3
@notice
    Temporary guardrail for the RoboTreasury system. This contract queries a 
    whitelist of tokens that can be pulled from the ingress into RoboTreasury
    by the operator. Each token has a configurable limit of tokens that can be 
    pulled at once, as well as a cooldown in between pulls of the same token.
"""

interface Robo:
    def pull(_token: address, _amount: uint256) -> address: nonpayable

interface Whitelist:
    def whitelist(_token: address) -> bool: view

robo: public(immutable(Robo))
whitelist: public(immutable(Whitelist))
management: public(immutable(address))
operator: public(address)
cooldown: public(uint256)
limits: public(HashMap[address, uint256])
last: public(HashMap[address, uint256])

implements: Robo

@external
def __init__(_robo: address, _whitelist: address, _management: address):
    robo = Robo(_robo)
    whitelist = Whitelist(_whitelist)
    management = _management
    self.operator = _management

@external
def set_cooldown(_cooldown: uint256):
    assert msg.sender == management
    self.cooldown = _cooldown

@external
def set_limit(_token: address, _amount: uint256):
    assert msg.sender == management
    self.limits[_token] = _amount

@external
def set_operator(_operator: address):
    assert msg.sender == management
    self.operator = _operator

@external
def pull(_token: address, _amount: uint256 = max_value(uint256)) -> address:
    assert msg.sender == self.operator
    assert whitelist.whitelist(_token)
    assert _amount <= self.limits[_token]
    assert block.timestamp >= self.last[_token] + self.cooldown

    self.last[_token] = block.timestamp
    return robo.pull(_token, _amount)
