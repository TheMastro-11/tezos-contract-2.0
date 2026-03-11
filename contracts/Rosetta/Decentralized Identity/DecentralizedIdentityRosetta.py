import smartpy as sp

@sp.module
def main():
    class DecentralizedIdentityRosetta(sp.Contract):
        def __init__(self):
            self.data.owners = sp.cast({}, sp.map[sp.address, sp.address])
            self.data.delegates = sp.cast({}, sp.map[sp.record(identity=sp.address, delegate_type=sp.bytes, delegate=sp.address).layout(
                    ("identity", ("delegate_type", "delegate"))
                ), sp.nat])
            self.data.nonce = sp.cast({}, sp.map[sp.address, sp.nat])
            self.data.changed = sp.cast({}, sp.map[sp.address, sp.nat])

        @sp.offchain_view
        def identityOwner(self, identity):
            identity = sp.cast(identity, sp.address)
            return self.data.owners.get(identity, default=identity)

        def _owner_of(self, identity):
            return self.data.owners.get(identity, default=identity)

        def _only_owner(self, identity, actor):
            sp.verify(actor == self._owner_of(identity), message="bad_actor")

        def _inc_nonce(self, owner):
            current = self.data.nonce.get(owner, default=0)
            self.data.nonce[owner] = current + 1
            return current

        def _check_signature_as_owner(self, identity, signer_key, signature, payload_bytes):
            identity = sp.cast(identity, sp.address)
            signer_key = sp.cast(signer_key, sp.key)
            signature = sp.cast(signature, sp.signature)

            owner_addr = self._owner_of(identity)
            sp.verify(sp.to_address(sp.hash_key(signer_key)) == owner_addr, message="bad_signature_owner")
            sp.verify(sp.check_signature(signer_key, signature, payload_bytes), message="bad_signature")
            return owner_addr

        def _payload(self, owner_nonce, identity, action, params_record):
            return sp.pack(
                sp.record(
                    contract=sp.self_address(),
                    nonce=sp.cast(owner_nonce, sp.nat),
                    identity=sp.cast(identity, sp.address),
                    action=sp.cast(action, sp.string),
                    params=params_record,
                )
            )

        def _change_owner(self, identity, actor, new_owner):
            identity = sp.cast(identity, sp.address)
            actor = sp.cast(actor, sp.address)
            new_owner = sp.cast(new_owner, sp.address)

            self._only_owner(identity, actor)
            self.data.owners[identity] = new_owner
            self.data.changed[identity] = sp.level

        def _add_delegate(self, identity, actor, delegate_type, delegate, validity):
            identity = sp.cast(identity, sp.address)
            actor = sp.cast(actor, sp.address)
            delegate_type = sp.cast(delegate_type, sp.bytes)
            delegate = sp.cast(delegate, sp.address)
            validity = sp.cast(validity, sp.nat)

            self._only_owner(identity, actor)

            expiry = sp.level + validity 
            key = sp.record(identity=identity, delegate_type=delegate_type, delegate=delegate)
            self.data.delegates[key] = expiry
            self.data.changed[identity] = sp.level
            
        @sp.entrypoint
        def changeOwner(self, params):
            params = sp.cast(params, sp.record(identity=sp.address, new_owner=sp.address))
            self._change_owner(params.identity, sp.sender, params.new_owner)

        @sp.entrypoint
        def addDelegate(self, params):
            params = sp.cast(
                params,
                sp.record(
                    identity=sp.address,
                    delegate_type=sp.bytes,
                    delegate=sp.address,
                    validity=sp.nat,
                ),
            )
            self._add_delegate(params.identity, sp.sender, params.delegate_type, params.delegate, params.validity)

        @sp.entrypoint
        def changeOwnerSigned(self, params):
            params = sp.cast(
                params,
                sp.record(
                    identity=sp.address,
                    signer_key=sp.key,
                    signature=sp.signature,
                    new_owner=sp.address,
                ),
            )

            owner = self._owner_of(params.identity)
            owner_nonce = self.data.nonce.get(owner, default=0)

            payload = self._payload(
                owner_nonce,
                params.identity,
                "changeOwner",
                sp.record(new_owner=params.new_owner),
            )

            actor = self._check_signature_as_owner(params.identity, params.signer_key, params.signature, payload)

            self._inc_nonce(actor)
            self._change_owner(params.identity, actor, params.new_owner)

        @sp.entrypoint
        def addDelegateSigned(self, params):
            params = sp.cast(
                params,
                sp.record(
                    identity=sp.address,
                    signer_key=sp.key,
                    signature=sp.signature,
                    delegate_type=sp.bytes,
                    delegate=sp.address,
                    validity=sp.nat,
                ),
            )

            owner = self._owner_of(params.identity)
            owner_nonce = self.data.nonce.get(owner, default=0)

            payload = self._payload(
                owner_nonce,
                params.identity,
                "addDelegate",
                sp.record(
                    delegate_type=params.delegate_type,
                    delegate=params.delegate,
                    validity=params.validity,
                ),
            )

            actor = self._check_signature_as_owner(params.identity, params.signer_key, params.signature, payload)
            self._inc_nonce(actor)
            self._add_delegate(params.identity, actor, params.delegate_type, params.delegate, params.validity)


        @sp.offchain_view
        def validDelegate(self, params):
            params = sp.cast(params, sp.record(identity=sp.address, delegate_type=sp.bytes, delegate=sp.address))
            key = sp.record(identity=params.identity, delegate_type=params.delegate_type, delegate=params.delegate)
            expiry = self.data.delegates.get(key, default=0)
            return expiry > sp.level


@sp.add_test()
def test():
    main_mod = main

    sc = sp.test_scenario("DecentralizedIdentityRosetta (compatible)", main_mod)

    c = main_mod.DecentralizedIdentityRosetta()
    sc += c

    