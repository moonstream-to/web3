/* Autogenerated file. Do not edit manually. */
/* tslint:disable */
/* eslint-disable */
import { Signer, utils, Contract, ContractFactory, Overrides } from "ethers"
import type { Provider, TransactionRequest } from "@ethersproject/providers"
import type { PromiseOrValue } from "../common"
import type { CraftingFacet, CraftingFacetInterface } from "../CraftingFacet"

const _abi = [
    {
        inputs: [
            {
                components: [
                    {
                        components: [
                            {
                                internalType: "uint256",
                                name: "tokenType",
                                type: "uint256",
                            },
                            {
                                internalType: "address",
                                name: "tokenAddress",
                                type: "address",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenId",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "amount",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenAction",
                                type: "uint256",
                            },
                        ],
                        internalType: "struct CraftingInputItem[]",
                        name: "inputs",
                        type: "tuple[]",
                    },
                    {
                        components: [
                            {
                                internalType: "uint256",
                                name: "tokenType",
                                type: "uint256",
                            },
                            {
                                internalType: "address",
                                name: "tokenAddress",
                                type: "address",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenId",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "amount",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenAction",
                                type: "uint256",
                            },
                        ],
                        internalType: "struct CraftingOutputItem[]",
                        name: "outputs",
                        type: "tuple[]",
                    },
                    {
                        internalType: "bool",
                        name: "isActive",
                        type: "bool",
                    },
                ],
                internalType: "struct Recipe",
                name: "recipe",
                type: "tuple",
            },
        ],
        name: "addRecipe",
        outputs: [],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "uint256",
                name: "recipeId",
                type: "uint256",
            },
        ],
        name: "craft",
        outputs: [],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "uint256",
                name: "recipeId",
                type: "uint256",
            },
        ],
        name: "getRecipe",
        outputs: [
            {
                components: [
                    {
                        components: [
                            {
                                internalType: "uint256",
                                name: "tokenType",
                                type: "uint256",
                            },
                            {
                                internalType: "address",
                                name: "tokenAddress",
                                type: "address",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenId",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "amount",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenAction",
                                type: "uint256",
                            },
                        ],
                        internalType: "struct CraftingInputItem[]",
                        name: "inputs",
                        type: "tuple[]",
                    },
                    {
                        components: [
                            {
                                internalType: "uint256",
                                name: "tokenType",
                                type: "uint256",
                            },
                            {
                                internalType: "address",
                                name: "tokenAddress",
                                type: "address",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenId",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "amount",
                                type: "uint256",
                            },
                            {
                                internalType: "uint256",
                                name: "tokenAction",
                                type: "uint256",
                            },
                        ],
                        internalType: "struct CraftingOutputItem[]",
                        name: "outputs",
                        type: "tuple[]",
                    },
                    {
                        internalType: "bool",
                        name: "isActive",
                        type: "bool",
                    },
                ],
                internalType: "struct Recipe",
                name: "",
                type: "tuple",
            },
        ],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [],
        name: "numRecipes",
        outputs: [
            {
                internalType: "uint256",
                name: "",
                type: "uint256",
            },
        ],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "uint256[]",
                name: "",
                type: "uint256[]",
            },
            {
                internalType: "uint256[]",
                name: "",
                type: "uint256[]",
            },
            {
                internalType: "bytes",
                name: "",
                type: "bytes",
            },
        ],
        name: "onERC1155BatchReceived",
        outputs: [
            {
                internalType: "bytes4",
                name: "",
                type: "bytes4",
            },
        ],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "uint256",
                name: "",
                type: "uint256",
            },
            {
                internalType: "uint256",
                name: "",
                type: "uint256",
            },
            {
                internalType: "bytes",
                name: "",
                type: "bytes",
            },
        ],
        name: "onERC1155Received",
        outputs: [
            {
                internalType: "bytes4",
                name: "",
                type: "bytes4",
            },
        ],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "address",
                name: "",
                type: "address",
            },
            {
                internalType: "uint256",
                name: "",
                type: "uint256",
            },
            {
                internalType: "bytes",
                name: "",
                type: "bytes",
            },
        ],
        name: "onERC721Received",
        outputs: [
            {
                internalType: "bytes4",
                name: "",
                type: "bytes4",
            },
        ],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "address",
                name: "terminusAddress",
                type: "address",
            },
            {
                internalType: "uint256",
                name: "tokenId",
                type: "uint256",
            },
        ],
        name: "setTerminusAuth",
        outputs: [],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            {
                internalType: "bytes4",
                name: "interfaceId",
                type: "bytes4",
            },
        ],
        name: "supportsInterface",
        outputs: [
            {
                internalType: "bool",
                name: "",
                type: "bool",
            },
        ],
        stateMutability: "view",
        type: "function",
    },
]

const _bytecode =
    "0x608060405234801561001057600080fd5b50611c41806100206000396000f3fe608060405234801561001057600080fd5b50600436106100935760003560e01c8063bc197c8111610066578063bc197c811461013c578063e74738d91461015b578063f23a6e611461016e578063f3917bd21461018d578063f8d12a41146101a057600080fd5b806301ffc9a714610098578063150b7a02146100c05780638935b14e146100f7578063953633b91461010c575b600080fd5b6100ab6100a6366004611366565b6101c0565b60405190151581526020015b60405180910390f35b6100de6100ce366004611466565b630a85bd0160e11b949350505050565b6040516001600160e01b031990911681526020016100b7565b61010a6101053660046114d2565b6101f7565b005b7fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf0546040519081526020016100b7565b6100de61014a36600461158d565b63bc197c8160e01b95945050505050565b61010a61016936600461163b565b610367565b6100de61017c366004611667565b63f23a6e6160e01b95945050505050565b61010a61019b3660046116d0565b6103d3565b6101b36101ae3660046116d0565b6110d2565b6040516100b791906116e9565b60006001600160e01b03198216630271189760e51b14806101f157506301ffc9a760e01b6001600160e01b03198316145b92915050565b7fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf1547fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf254610250916001600160a01b031690600161125e565b6102ed5760405162461bcd60e51b815260206004820152605c60248201527f4372616674696e6746616365742e6f6e6c79417574686f72697a65644164647260448201527f6573733a205468652061646472657373206973206e6f7420617574686f72697a60648201527f656420746f20706572666f726d2074686973206f7065726174696f6e00000000608482015260a4015b60405180910390fd5b7fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf080547fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bef91600061033d8361180a565b909155505060018101546000908152602082905260409020829061036182826119d9565b50505050565b61036f6112dd565b7fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf180546001600160a01b0319166001600160a01b0393909316929092179091557fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bf255565b7ff25566827f1ecffd3a8194c09082ce7cc925254b0665695b1181ab01362ea1cf805460ff16156104525760405162461bcd60e51b815260206004820152602360248201527f4c69625265656e7472616e637947756172643a207265656e7472616e742063616044820152626c6c2160e81b60648201526084016102e4565b805460ff1916600117815560006104867fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bef90565b600084815260209182526040808220815181546080958102820186019093526060810183815290949193859391928592919085015b828210156105225760008481526020908190206040805160a08101825260058602909201805483526001808201546001600160a01b0316848601526002820154928401929092526003810154606084015260040154608083015290835290920191016104bb565b50505050815260200160018201805480602002602001604051908101604052809291908181526020016000905b828210156105b65760008481526020908190206040805160a08101825260058602909201805483526001808201546001600160a01b03168486015260028201549284019290925260038101546060840152600401546080830152908352909201910161054f565b505050908252506002919091015460ff161515602090910152905060005b815151811015610c27576014826000015182815181106105f6576105f6611b20565b602002602001015160000151036109235760008260000151828151811061061f5761061f611b20565b602002602001015160200151905060008360000151838151811061064557610645611b20565b60200260200101516080015103610781576000816001600160a01b03166323b872dd33308760000151878151811061067f5761067f611b20565b6020908102919091010151606001516040516001600160e01b031960e086901b1681526001600160a01b03938416600482015292909116602483015260448201526064016020604051808303816000875af11580156106e2573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906107069190611b36565b90508061077b5760405162461bcd60e51b815260206004820152603760248201527f4372616674696e6746616365742e63726166743a207472616e73666572206f6660448201527f206572633230496e707574546f6b656e206661696c656400000000000000000060648201526084016102e4565b5061091d565b60018360000151838151811061079957610799611b20565b6020026020010151608001510361084457806001600160a01b03166379cc679033856000015185815181106107d0576107d0611b20565b6020026020010151606001516040518363ffffffff1660e01b815260040161080d9291906001600160a01b03929092168252602082015260400190565b600060405180830381600087803b15801561082757600080fd5b505af115801561083b573d6000803e3d6000fd5b5050505061091d565b60028360000151838151811061085c5761085c611b20565b6020026020010151608001510361091d576040516370a0823160e01b81523360048201526000906001600160a01b038316906370a0823190602401602060405180830381865afa1580156108b4573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906108d89190611b53565b9050836000015183815181106108f0576108f0611b20565b60200260200101516060015181101561091b5760405162461bcd60e51b81526004016102e490611b6c565b505b50610c15565b6104838260000151828151811061093c5761093c611b20565b60200260200101516000015103610c155760008260000151828151811061096557610965611b20565b602002602001015160200151905060008360000151838151811061098b5761098b611b20565b60200260200101516080015103610a4757806001600160a01b031663f242432a3330866000015186815181106109c3576109c3611b20565b602002602001015160400151876000015187815181106109e5576109e5611b20565b6020026020010151606001516040518563ffffffff1660e01b8152600401610a109493929190611bd3565b600060405180830381600087803b158015610a2a57600080fd5b505af1158015610a3e573d6000803e3d6000fd5b50505050610c13565b600183600001518381518110610a5f57610a5f611b20565b60200260200101516080015103610b0057806001600160a01b031663f5298aca3385600001518581518110610a9657610a96611b20565b60200260200101516040015186600001518681518110610ab857610ab8611b20565b6020908102919091010151606001516040516001600160e01b031960e086901b1681526001600160a01b03909316600484015260248301919091526044820152606401610a10565b600283600001518381518110610b1857610b18611b20565b60200260200101516080015103610c13576000816001600160a01b031662fdd58e3386600001518681518110610b5057610b50611b20565b6020026020010151604001516040518363ffffffff1660e01b8152600401610b8d9291906001600160a01b03929092168252602082015260400190565b602060405180830381865afa158015610baa573d6000803e3d6000fd5b505050506040513d601f19601f82011682018060405250810190610bce9190611b53565b905083600001518381518110610be657610be6611b20565b602002602001015160600151811015610c115760405162461bcd60e51b81526004016102e490611b6c565b505b505b80610c1f8161180a565b9150506105d4565b5060005b8160200151518110156110c557601482602001518281518110610c5057610c50611b20565b60200260200101516000015103610e9857600082602001518281518110610c7957610c79611b20565b6020026020010151602001519050600083602001518381518110610c9f57610c9f611b20565b60200260200101516080015103610dd3576000816001600160a01b031663a9059cbb3386602001518681518110610cd857610cd8611b20565b6020026020010151606001516040518363ffffffff1660e01b8152600401610d159291906001600160a01b03929092168252602082015260400190565b6020604051808303816000875af1158015610d34573d6000803e3d6000fd5b505050506040513d601f19601f82011682018060405250810190610d589190611b36565b905080610dcd5760405162461bcd60e51b815260206004820152603860248201527f4372616674696e6746616365742e63726166743a207472616e73666572206f6660448201527f2065726332304f7574707574546f6b656e206661696c6564000000000000000060648201526084016102e4565b50610e92565b600183602001518381518110610deb57610deb611b20565b60200260200101516080015103610e9257806001600160a01b03166340c10f193385602001518581518110610e2257610e22611b20565b6020026020010151606001516040518363ffffffff1660e01b8152600401610e5f9291906001600160a01b03929092168252602082015260400190565b600060405180830381600087803b158015610e7957600080fd5b505af1158015610e8d573d6000803e3d6000fd5b505050505b506110b3565b61048382602001518281518110610eb157610eb1611b20565b602002602001015160000151036110b357600082602001518281518110610eda57610eda611b20565b6020026020010151602001519050600083602001518381518110610f0057610f00611b20565b60200260200101516080015103610fbc57806001600160a01b031663f242432a303386602001518681518110610f3857610f38611b20565b60200260200101516040015187602001518781518110610f5a57610f5a611b20565b6020026020010151606001516040518563ffffffff1660e01b8152600401610f859493929190611bd3565b600060405180830381600087803b158015610f9f57600080fd5b505af1158015610fb3573d6000803e3d6000fd5b505050506110b1565b600183602001518381518110610fd457610fd4611b20565b602002602001015160800151036110b157806001600160a01b031663731133e9338560200151858151811061100b5761100b611b20565b6020026020010151604001518660200151868151811061102d5761102d611b20565b6020908102919091010151606001516040516001600160e01b031960e086901b1681526001600160a01b03909316600484015260248301919091526044820152608060648201526000608482015260a401600060405180830381600087803b15801561109857600080fd5b505af11580156110ac573d6000803e3d6000fd5b505050505b505b806110bd8161180a565b915050610c2b565b5050805460ff1916905550565b604080516060808201835280825260208201526000918101919091527fbfa4432d33b2086a2543ca74d1134d1d129bd97e9219fa5b64f94e78346e2bef600083815260209182526040808220815181546080958102820186019093526060810183815290949193859391928592919085015b828210156111ab5760008481526020908190206040805160a08101825260058602909201805483526001808201546001600160a01b031684860152600282015492840192909252600381015460608401526004015460808301529083529092019101611144565b50505050815260200160018201805480602002602001604051908101604052809291908181526020016000905b8282101561123f5760008481526020908190206040805160a08101825260058602909201805483526001808201546001600160a01b0316848601526002820154928401929092526003810154606084015260040154608083015290835290920191016111d8565b505050908252506002919091015460ff16151560209091015292915050565b604051627eeac760e11b815233600482015260248101839052600090849083906001600160a01b0383169062fdd58e90604401602060405180830381865afa1580156112ae573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906112d29190611b53565b101595945050505050565b7fc8fcad8db84d3cc18b4c41d551ea0ee66dd599cde068d998e57d5e09332c131c600401546001600160a01b031633146113645760405162461bcd60e51b815260206004820152602260248201527f4c69624469616d6f6e643a204d75737420626520636f6e7472616374206f776e60448201526132b960f11b60648201526084016102e4565b565b60006020828403121561137857600080fd5b81356001600160e01b03198116811461139057600080fd5b9392505050565b6001600160a01b03811681146113ac57600080fd5b50565b634e487b7160e01b600052604160045260246000fd5b604051601f8201601f1916810167ffffffffffffffff811182821017156113ee576113ee6113af565b604052919050565b600082601f83011261140757600080fd5b813567ffffffffffffffff811115611421576114216113af565b611434601f8201601f19166020016113c5565b81815284602083860101111561144957600080fd5b816020850160208301376000918101602001919091529392505050565b6000806000806080858703121561147c57600080fd5b843561148781611397565b9350602085013561149781611397565b925060408501359150606085013567ffffffffffffffff8111156114ba57600080fd5b6114c6878288016113f6565b91505092959194509250565b6000602082840312156114e457600080fd5b813567ffffffffffffffff8111156114fb57600080fd5b82016060818503121561139057600080fd5b600082601f83011261151e57600080fd5b8135602067ffffffffffffffff82111561153a5761153a6113af565b8160051b6115498282016113c5565b928352848101820192828101908785111561156357600080fd5b83870192505b8483101561158257823582529183019190830190611569565b979650505050505050565b600080600080600060a086880312156115a557600080fd5b85356115b081611397565b945060208601356115c081611397565b9350604086013567ffffffffffffffff808211156115dd57600080fd5b6115e989838a0161150d565b945060608801359150808211156115ff57600080fd5b61160b89838a0161150d565b9350608088013591508082111561162157600080fd5b5061162e888289016113f6565b9150509295509295909350565b6000806040838503121561164e57600080fd5b823561165981611397565b946020939093013593505050565b600080600080600060a0868803121561167f57600080fd5b853561168a81611397565b9450602086013561169a81611397565b93506040860135925060608601359150608086013567ffffffffffffffff8111156116c457600080fd5b61162e888289016113f6565b6000602082840312156116e257600080fd5b5035919050565b602080825282516060838301528051608084018190526000929160a0919083019082860190855b8181101561176457611754838551805182526020808201516001600160a01b0316908301526040808201519083015260608082015190830152608090810151910152565b9285019291840191600101611710565b505086840151868203601f19016040880152805180835290850192506000918501905b808310156117df576117cb828551805182526020808201516001600160a01b0316908301526040808201519083015260608082015190830152608090810151910152565b928501926001929092019190840190611787565b50604088015180151560608901529450611582565b634e487b7160e01b600052601160045260246000fd5b60006001820161181c5761181c6117f4565b5060010190565b6000808335601e1984360301811261183a57600080fd5b83018035915067ffffffffffffffff82111561185557600080fd5b602001915060a08102360382131561186c57600080fd5b9250929050565b8135815560018101602083013561188981611397565b81546001600160a01b0319166001600160a01b03919091161790556040820135600282015560608201356003820155608090910135600490910155565b600160401b8311156118da576118da6113af565b805483825580841015611981577f33333333333333333333333333333333333333333333333333333333333333338082116001161561191b5761191b6117f4565b600581861160011615611930576119306117f4565b60008481526020902086820281019250818402015b8083101561197d5761197483600081556000600182015560006002820155600060038201556000600482015550565b91810191611945565b5050505b5060008181526020812083915b858110156119b6576119a08383611873565b60a092909201916005919091019060010161198e565b505050505050565b80151581146113ac57600080fd5b600081356101f1816119be565b6119e38283611823565b600160401b8111156119f7576119f76113af565b825481845580821015611a9e577f333333333333333333333333333333333333333333333333333333333333333380821160011615611a3857611a386117f4565b600581841160011615611a4d57611a4d6117f4565b60008681526020902084820281019250818402015b80831015611a9a57611a9183600081556000600182015560006002820155600060038201556000600482015550565b91810191611a62565b5050505b5060008381526020902060005b82811015611ad357611abd8483611873565b60a0939093019260059190910190600101611aab565b50505050611ae46020830183611823565b611af28183600186016118c6565b5050611b1c611b03604084016119cc565b6002830160ff1981541660ff8315151681178255505050565b5050565b634e487b7160e01b600052603260045260246000fd5b600060208284031215611b4857600080fd5b8151611390816119be565b600060208284031215611b6557600080fd5b5051919050565b60208082526041908201527f4372616674696e6746616365742e63726166743a205573657220646f65736e2760408201527f7420686f6c6420656e6f75676820746f6b656e7320666f72206372616674696e6060820152606760f81b608082015260a00190565b6001600160a01b0394851681529290931660208301526040820152606081019190915260a06080820181905260009082015260c0019056fea2646970667358221220c1f9bd6817b7d2d42e619cc3636defcbc8001461687560699fe89db0caa4a71664736f6c63430008100033"

type CraftingFacetConstructorParams =
    | [signer?: Signer]
    | ConstructorParameters<typeof ContractFactory>

const isSuperArgs = (
    xs: CraftingFacetConstructorParams
): xs is ConstructorParameters<typeof ContractFactory> => xs.length > 1

export class CraftingFacet__factory extends ContractFactory {
    constructor(...args: CraftingFacetConstructorParams) {
        if (isSuperArgs(args)) {
            super(...args)
        } else {
            super(_abi, _bytecode, args[0])
        }
    }

    override deploy(
        overrides?: Overrides & { from?: PromiseOrValue<string> }
    ): Promise<CraftingFacet> {
        return super.deploy(overrides || {}) as Promise<CraftingFacet>
    }
    override getDeployTransaction(
        overrides?: Overrides & { from?: PromiseOrValue<string> }
    ): TransactionRequest {
        return super.getDeployTransaction(overrides || {})
    }
    override attach(address: string): CraftingFacet {
        return super.attach(address) as CraftingFacet
    }
    override connect(signer: Signer): CraftingFacet__factory {
        return super.connect(signer) as CraftingFacet__factory
    }

    static readonly bytecode = _bytecode
    static readonly abi = _abi
    static createInterface(): CraftingFacetInterface {
        return new utils.Interface(_abi) as CraftingFacetInterface
    }
    static connect(
        address: string,
        signerOrProvider: Signer | Provider
    ): CraftingFacet {
        return new Contract(address, _abi, signerOrProvider) as CraftingFacet
    }
}
