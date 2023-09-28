# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SolanaWalletMultiButton(Component):
    """A SolanaWalletMultiButton component.
SolanaWalletMultiButton component.
This is a multi-button component for Solana wallets. It allows users to connect
to different types of Solana wallets.ne the SolanaWalletMultiButton compone is a functional component that takes some props and returns a JSX eleme

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    CSS class name(s)  This prop can be used to apply one or more CSS
    classes to the button. This makes it easy to customize the
    appearance of the button using CSS.

- network (a value equal to: 'devnet', 'mainnet', 'testnet'; default 'mainnet'):
    The network for the wallet.  This prop specifies the network for
    the wallet. It can be 'devnet', 'mainnet', or 'testnet'.

- publicKeyState (string; optional):
    The state of the public key.  This prop holds the state of the
    public key. It could be a string representing the public key, or
    None if there is no public key.

- rpcEndpoint (string; optional):
    The custom RPC endpoint for the wallet.  This prop specifies a
    custom RPC endpoint for the wallet. If it's not provided,  the
    default endpoint for the specified network will be used."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_solana_components'
    _type = 'SolanaWalletMultiButton'
    @_explicitize_args
    def __init__(self, network=Component.UNDEFINED, publicKeyState=Component.UNDEFINED, rpcEndpoint=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'network', 'publicKeyState', 'rpcEndpoint']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'network', 'publicKeyState', 'rpcEndpoint']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(SolanaWalletMultiButton, self).__init__(**args)
