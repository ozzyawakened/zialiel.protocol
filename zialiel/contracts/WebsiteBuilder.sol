// WebsiteBuilder.sol – Forbedret versjon
pragma solidity ^0.8.0;

contract WebsiteBuilder {
    address public owner;
    mapping(uint => Request) public requests;
    uint public requestCount;
    
    // Nytt: Flere autoriserte AI-agenter
    mapping(address => bool) public authorizedAgents;
    
    // Nytt: Gebyr for å opprette forespørsel
    uint public fee = 0.01 ether; // Kan justeres av eier
    
    // Nytt: Tidsavbrudd (7 dager)
    uint public constant TIMEOUT = 7 days;
    
    struct Request {
        string description;
        string generatedCode;
        address requester;
        bool completed;
        uint timestamp;
        bool cancelled; // Nytt: Spor om den er kansellert
    }
    
    event RequestCreated(uint id, string description, address requester, uint amount);
    event RequestCompleted(uint id, string code, address completedBy);
    event RequestCancelled(uint id, address cancelledBy);
    event AgentAuthorized(address agent, bool status);
    event FeeUpdated(uint newFee);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedAgents[msg.sender], "Not authorized agent");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedAgents[msg.sender] = true; // Owner er også agent
    }
    
    // Administrasjon av autoriserte AI-agenter
    function authorizeAgent(address _agent, bool _status) public onlyOwner {
        authorizedAgents[_agent] = _status;
        emit AgentAuthorized(_agent, _status);
    }
    
    // Juster gebyr (hvis nødvendig)
    function updateFee(uint _newFee) public onlyOwner {
        fee = _newFee;
        emit FeeUpdated(_newFee);
    }
    
    // Opprett ny forespørsel (med betaling)
    function createRequest(string memory _description) public payable {
        require(msg.value >= fee, "Insufficient payment");
        
        requestCount++;
        requests[requestCount] = Request({
            description: _description,
            generatedCode: "",
            requester: msg.sender,
            completed: false,
            timestamp: block.timestamp,
            cancelled: false
        });
        
        // Overskytende ether refunderes
        if (msg.value > fee) {
            payable(msg.sender).transfer(msg.value - fee);
        }
        
        emit RequestCreated(requestCount, _description, msg.sender, fee);
    }
    
    // Fullfør forespørsel (kun autoriserte AI-agenter)
    function fulfillRequest(uint _id, string memory _code) public onlyAuthorized {
        Request storage req = requests[_id];
        require(!req.completed, "Already completed");
        require(!req.cancelled, "Request was cancelled");
        require(req.requester != address(0), "Request does not exist");
        
        req.generatedCode = _code;
        req.completed = true;
        
        emit RequestCompleted(_id, _code, msg.sender);
        
        // Her kan man legge til logikk for å betale AI-agenten
        // For eksempel: overfør en del av gebyret til agenten
    }
    
    // Kanseller utgått forespørsel (hvem som helst kan kalle)
    function cancelExpiredRequest(uint _id) public {
        Request storage req = requests[_id];
        require(!req.completed, "Already completed");
        require(!req.cancelled, "Already cancelled");
        require(block.timestamp > req.timestamp + TIMEOUT, "Not expired");
        
        req.cancelled = true;
        emit RequestCancelled(_id, msg.sender);
        
        // Refunder betaling til requester? Evt. send til treasury
        // payable(req.requester).transfer(fee); // hvis fee lagres
    }
    
    // Hent alle aktive forespørsler (for frontend)
    function getActiveRequests() public view returns (uint[] memory) {
        uint[] memory active = new uint[](requestCount);
        uint counter = 0;
        
        for (uint i = 1; i <= requestCount; i++) {
            if (!requests[i].completed && !requests[i].cancelled) {
                active[counter] = i;
                counter++;
            }
        }
        
        // Trim array til faktisk lengde
        assembly {
            mstore(active, counter)
        }
        return active;
    }
    
    // Hent forespørsler laget av en bestemt adresse
    function getRequestsByAddress(address _requester) public view returns (uint[] memory) {
        uint[] memory userRequests = new uint[](requestCount);
        uint counter = 0;
        
        for (uint i = 1; i <= requestCount; i++) {
            if (requests[i].requester == _requester) {
                userRequests[counter] = i;
                counter++;
            }
        }
        
        assembly {
            mstore(userRequests, counter)
        }
        return userRequests;
    }
}
