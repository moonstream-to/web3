# Moonstream web3 auth

## This tool helps to generate accesss tokens for moonstream.to

token is stored as base64 encoded string of an object of following interface:

```ts
interface TokenInterface {
  address: string;
  deadline: number;
  signed_message: string;
}
```

Deadline is stored as number (in seconds).

usage:
`yarn add @moonstream/web3auth`

```js
import { signAccessToken, parseToken, isOutdated } from "@moonstream/web3auth";
```

Generate access token:

```js
const _getSignature = async () => {
  const token = await signAccessToken(address, window.ethereum, 60 * 60 * 24);
  // Do stuff..
};
```

Read data conained in token:

```js
const objectToken = parseToken(token);
```

check if deadline expired:

```js
isOutdated(objectToken?.deadline);
```
