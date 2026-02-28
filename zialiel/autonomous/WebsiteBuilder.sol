// WebsiteBuilder.sol
pragma solidity ^0.8.0;

contract WebsiteBuilder {
    address public owner;
    mapping(uint => Request) public requests;
    uint public requestCount;
    
    struct Request {
        string description;
        string generatedCode;
        address requester;
        bool completed;
        uint timestamp;
    }
    
    event RequestCreated(uint id, string description, address requester);
    event RequestCompleted(uint id, string code);
    
    constructor() {
        owner = msg.sender;
    }
    
    function createRequest(string memory _description) public {
        requestCount++;
        requests[requestCount] = Request({
            description: _description,
            generatedCode: "",
            requester: msg.sender,
            completed: false,
            timestamp: block.timestamp
        });
        emit RequestCreated(requestCount, _description, msg.sender);
    }
    
    // Called by the AI agent (must be authorized)
    function fulfillRequest(uint _id, string memory _code) public {
        require(msg.sender == owner, "Only owner can fulfill");
        require(!requests[_id].completed, "Already completed");
        
        requests[_id].generatedCode = _code;
        requests[_id].completed = true;
        emit RequestCompleted(_id, _code);
    }
}
