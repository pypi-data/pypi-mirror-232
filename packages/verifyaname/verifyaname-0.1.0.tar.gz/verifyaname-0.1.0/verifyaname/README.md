Example how to generate verification string for your domain

```python
from verifyaname.verification_string import generate_verification_string
from cosmpy.aerial.wallet import LocalWallet

DOMAIN = "fetch-ai.com"

alice_wallet = LocalWallet.from_unsafe_seed("Alice seed")

# Generate verification string for Alice
verification_string = generate_verification_string(
    wallet=alice_wallet, domain=DOMAIN, address=str(alice_wallet.address())
)
```

This string needs to be stored to domain DNS TXT record under key `fetch-ans-token=`
