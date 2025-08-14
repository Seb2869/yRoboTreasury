interface Factory:
    def deploy(_from: address, _to: address) -> address: nonpayable

factory: address
is_bucket: public(HashMap[address, bool])

@external
def deploy_converter(_from: address, _to: address) -> address:
    return Factory(self.factory).deploy(_from, _to)

@external
def set_factory(_factory: address):
    self.factory = _factory

@external
def set_bucket(_bucket: address, _flag: bool):
    self.is_bucket[_bucket] = _flag

@external
def pull(_token: address, _amount: uint256) -> address:
    return empty(address)
