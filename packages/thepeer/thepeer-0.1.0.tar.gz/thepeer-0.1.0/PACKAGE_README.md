# thepeer
A 3rd party developer friendly python client package for [thepeer](https://thepeer.co/)

## installation
`pip install thepeer`

## usage
Future versions of this package will provide a much better documentation. This
version was published to claim the package namespace. however, the package is quite
functional as is. First of, you want to import the client
```python

from thepeer import ThePeerClient, ChargeEvent, PaymentChannel
client = ThePeerClient(secret_key="<secret_key>") # you can omit the secret key param if
# the environmental variable THEPEER_SECRET_KEY is set.
response = client.users.all() # Fetch all indexed users.
print(response)

response = client.transactions.get("<transaction_id>") # Fetch a transaction.
print(response)

response = client.links.get_user_links("<user_reference>") # Fetch all linked accounts of a user.
print(response)

response = client.authorize_charge("<charge_reference>", 
                                   event=ChargeEvent.INSUFFICIENT_FUNDS) # Process a charge authorization request.
print(response)

response = client.generate_checkout(amount=10000, email="johndoe@example.com") # Generate a checkout.
print(response)

response = client.get_businesses(
    channel=PaymentChannel.DIRECT_CHARGE) # Fetch businesses based on the API they integrated.
print(response)
```
`ThePeerClient` has three attributes bound to it `users` for user related operations,
`transactions` for transaction related operations and `links` for link related operations.
It also provides additional methods `authorize_charge`, `generate_checkout` and `get_businessses`.
All methods on the client returns a `Response` with is a dataclass containing the `status_code`
and `data` returned from thepeer. This package also provides an async client which mirrors this
client and can come in handy in async context
```python
# note the following code should be tested in an async context to work
# e.g. `python -m asynio`
from thepeer import AsyncThePeerClient

client = AsyncThePeerClient(secret_key="<secret_key>") # you can omit the secret key param if
# the environmental variable THEPEER_SECRET_KEY is set.
response = await client.users.all() # Notice that the `all` method is identical to that
# on the `ThePeerClient` except that we had to await it here.
print(response)
```
All methods are type annotated and also provide docstrings for a smooth developer experience.
I hope you find this package useful.

## source code

- [https://github.com/gray-adeyi/thepeer](https://github.com/gray-adeyi/thepeer)

## license

- MIT