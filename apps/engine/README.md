```
yarn
cp sample.env mumbai.env
source mumbai.env
yarn dev
```

IF abi has changed:

```
brownie compile
./getAbis.sh
yarn generate_classes
```
