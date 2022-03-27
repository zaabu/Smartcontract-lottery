from brownie import( 
    Contract,
    accounts,
    config,
    network,
    interface,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken
)


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local2"]



def get_account(index=None, id=None):
    #ways of adding accounts
    #accounts[0]: use account automatically created by brownie
    #accounts.add("env"): use wallet account derived from private key
    #accounts.load("id"): Use stored account inside brownie by stating it's id e.g "freecodecamp"
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

#Contract to mock
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken, 
}

#Mock VRF coordinator for testing purposes


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config if defined
    Otherwise it will deploy a mock version of that contract and return that mock
    contract.

    Args:
        contract_name: string

    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version of
        this contract
        MockAggregator[-1]
    """
    #contract to mock = MockV3Aggregator
    contract_type = contract_to_mock[contract_name]
    #If we are dealing with a local blockchain 
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        #If we haven't deployed the contract yet, deploy it.
        if len(contract_type) <= 0:
            deploy_mocks()
        #MockV3Aggregator[-1]
        #Get last deployed contract
        contract = contract_type[-1]
    else:
        #If we are on a real network, get contract address 
        contract_address = config["networks"][network.show_active()][contract_name]
        #Create a new mock contract from ABI(MockV3Aggregator.abi) and return it
        #Contracts to mock are stored inside the contracts folder
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        ) 
    return contract

DECIMALS = 8
#set default value that is equal to 0.025 eth
INITIAL_VALUE = 200000000000

#Deploy mock price feed giving it initial value to convert(in WEI) as well as decimal places to return(8)
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    #Deploy MockV3Aggregator contract that returns exchange rate of ETH/USD
    #Since we need 50USD to participate in lottery the aggregator will let us know how much that is in wei
    MockV3Aggregator.deploy(
        decimals,
        initial_value,
        { "from": account }
    )
    #Deploy link token address
    link_token = LinkToken.deploy({"from": account})
    """
    VRFCoordinatorMock

    Provides us with a random number. Requires link_token address with link token that will be used as a payment
    to the service that provides the random number
    """
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")

def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
    ): #0.1 LINK
    #if account is provided on function call use it else call get_account()
    account = account if account else get_account()
    #if link_token is provided use it else call get_contract()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account })
    # #Alternative method for transferring funds 
    # #Create instance of LinkToken interface
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # #transfer link to contract responsible for calling a random number
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx
    




    
