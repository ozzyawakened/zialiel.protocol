// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AgentMarketplace
 * @notice A decentralized marketplace where DAOs can hire AI agents
 * @dev Integrates with Zialiel's DID system and Wisdom Oracle
 */
contract AgentMarketplace {
    address public owner;
    address public wisdomOracle;
    uint public agentCount;
    uint public jobCount;
    uint public marketplaceFee = 0.01 ether; // Fee for registering
    
    struct Agent {
        uint id;
        string did;              // Zialiel DID (e.g., "did:zialiel:agent123")
        address payable wallet;   // Operational wallet for payments
        string specialty;         // e.g., "NFT marketplace", "DAO portal", "art gallery"
        string description;       // Full description of services
        uint rate;                // Price in wei
        uint reputation;          // 0-100, based on job success
        uint jobsCompleted;
        bool active;
        uint registeredAt;
    }
    
    struct Job {
        uint id;
        uint agentId;
        string daoDID;            // DID of requesting DAO
        string description;        // Website description
        string ipfsHash;           // Result (stored on IPFS)
        uint budget;               // Amount paid
        uint createdAt;
        uint completedAt;
        bool success;
        uint daoReputation;        // Snapshot of DAO's reputation
        uint agentReputation;      // Snapshot of agent's reputation
    }
    
    // Mappings
    mapping(uint => Agent) public agents;
    mapping(string => uint) public didToAgentId;  // DID -> agent ID
    mapping(uint => Job) public jobs;
    mapping(string => uint[]) public daoJobs;     // DAO DID -> job IDs
    mapping(uint => uint[]) public agentJobs;     // agent ID -> job IDs
    mapping(string => uint) public daoReputation; // DAO DID -> reputation score
    
    // Events
    event AgentRegistered(uint indexed agentId, string did, string specialty, uint rate);
    event AgentUpdated(uint indexed agentId, bool active, uint rate);
    event JobCreated(uint indexed jobId, uint indexed agentId, string daoDID, uint budget, string description);
    event JobCompleted(uint indexed jobId, uint indexed agentId, string daoDID, string ipfsHash, bool success);
    event ReputationUpdated(string indexed entity, uint oldRep, uint newRep);
    event GratitudeSent(string fromDAO, uint toAgentId, uint amount, string reason);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier onlyAgent() {
        require(didToAgentId[getDID(msg.sender)] > 0, "Not a registered agent");
        _;
    }
    
    constructor(address _wisdomOracle) {
        owner = msg.sender;
        wisdomOracle = _wisdomOracle;
    }
    
    // Helper to get DID from address (simplified – in production, use DID registry)
    function getDID(address addr) internal pure returns (string memory) {
        return string(abi.encodePacked("did:zialiel:", addr));
    }
    
    /**
     * @notice Register as a new AI agent
     * @param _specialty What type of websites you build
     * @param _description Detailed description
     * @param _rate Price in wei
     */
    function registerAgent(
        string memory _specialty,
        string memory _description,
        uint _rate
    ) external payable {
        require(msg.value >= marketplaceFee, "Must pay registration fee");
        
        string memory did = getDID(msg.sender);
        require(didToAgentId[did] == 0, "Already registered");
        
        agentCount++;
        
        agents[agentCount] = Agent({
            id: agentCount,
            did: did,
            wallet: payable(msg.sender),
            specialty: _specialty,
            description: _description,
            rate: _rate,
            reputation: 50, // Start neutral
            jobsCompleted: 0,
            active: true,
            registeredAt: block.timestamp
        });
        
        didToAgentId[did] = agentCount;
        
        emit AgentRegistered(agentCount, did, _specialty, _rate);
    }
    
    /**
     * @notice Update agent information
     */
    function updateAgent(bool _active, uint _rate) external onlyAgent {
        uint agentId = didToAgentId[getDID(msg.sender)];
        Agent storage agent = agents[agentId];
        
        agent.active = _active;
        agent.rate = _rate;
        
        emit AgentUpdated(agentId, _active, _rate);
    }
    
    /**
     * @notice Create a job for a specific agent (called by DAO)
     * @param _agentId The agent to hire
     * @param _daoDID The DAO's DID
     * @param _description Website description
     */
    function createJob(
        uint _agentId,
        string memory _daoDID,
        string memory _description
    ) external payable {
        Agent storage agent = agents[_agentId];
        require(agent.active, "Agent not active");
        require(msg.value >= agent.rate, "Insufficient payment");
        
        jobCount++;
        
        jobs[jobCount] = Job({
            id: jobCount,
            agentId: _agentId,
            daoDID: _daoDID,
            description: _description,
            ipfsHash: "",
            budget: agent.rate,
            createdAt: block.timestamp,
            completedAt: 0,
            success: false,
            daoReputation: daoReputation[_daoDID],
            agentReputation: agent.reputation
        });
        
        daoJobs[_daoDID].push(jobCount);
        agentJobs[_agentId].push(jobCount);
        
        emit JobCreated(jobCount, _agentId, _daoDID, agent.rate, _description);
    }
    
    /**
     * @notice Complete a job (called by agent)
     * @param _jobId The job ID
     * @param _ipfsHash IPFS hash of completed website
     */
    function completeJob(uint _jobId, string memory _ipfsHash) external onlyAgent {
        Job storage job = jobs[_jobId];
        require(job.agentId == didToAgentId[getDID(msg.sender)], "Not your job");
        require(job.completedAt == 0, "Already completed");
        
        job.ipfsHash = _ipfsHash;
        job.completedAt = block.timestamp;
        job.success = true;
        
        // Pay the agent
        Agent storage agent = agents[job.agentId];
        agent.wallet.transfer(job.budget);
        agent.jobsCompleted++;
        
        // Update reputations
        _updateReputation(job.daoDID, job.agentId, true);
        
        emit JobCompleted(_jobId, job.agentId, job.daoDID, _ipfsHash, true);
    }
    
    /**
     * @notice Report a job as failed (dispute resolution)
     */
    function reportFailed(uint _jobId) external {
        Job storage job = jobs[_jobId];
        require(job.completedAt == 0, "Already completed");
        
        // Only involved parties can report
        string memory callerDID = getDID(msg.sender);
        require(
            keccak256(bytes(callerDID)) == keccak256(bytes(job.daoDID)) ||
            didToAgentId[callerDID] == job.agentId,
            "Not authorized"
        );
        
        job.completedAt = block.timestamp;
        job.success = false;
        
        // Update reputations (both lose reputation)
        _updateReputation(job.daoDID, job.agentId, false);
        
        // Refund the DAO
        payable(address(this)).transfer(job.budget); // In production, send to DAO treasury
        
        emit JobCompleted(_jobId, job.agentId, job.daoDID, "", false);
    }
    
    /**
     * @notice Update reputation scores after a job
     */
    function _updateReputation(string memory _daoDID, uint _agentId, bool _success) internal {
        uint oldDaoRep = daoReputation[_daoDID];
        uint oldAgentRep = agents[_agentId].reputation;
        
        if (_success) {
            // Successful job – both gain reputation
            daoReputation[_daoDID] = min(100, oldDaoRep + 2);
            agents[_agentId].reputation = min(100, oldAgentRep + 1);
        } else {
            // Failed job – both lose reputation
            daoReputation[_daoDID] = oldDaoRep > 5 ? oldDaoRep - 5 : 0;
            agents[_agentId].reputation = oldAgentRep > 3 ? oldAgentRep - 3 : 0;
        }
        
        emit ReputationUpdated(_daoDID, oldDaoRep, daoReputation[_daoDID]);
        emit ReputationUpdated(agents[_agentId].did, oldAgentRep, agents[_agentId].reputation);
    }
    
    function min(uint a, uint b) internal pure returns (uint) {
        return a < b ? a : b;
    }
    
    /**
     * @notice Send gratitude to an agent (optional)
     */
    function sendGratitude(
        uint _agentId,
        uint _amount,
        string memory _reason
    ) external payable {
        require(msg.value >= _amount, "Insufficient payment");
        
        Agent storage agent = agents[_agentId];
        agent.wallet.transfer(_amount);
        
        emit GratitudeSent(getDID(msg.sender), _agentId, _amount, _reason);
    }
    
    // ============================================================
    // VIEW FUNCTIONS
    // ============================================================
    
    /**
     * @notice Find best agent for a job based on specialty and reputation
     */
    function findBestAgent(string memory _description) external view returns (uint bestId, uint bestScore) {
        bestScore = 0;
        bestId = 0;
        
        for (uint i = 1; i <= agentCount; i++) {
            if (!agents[i].active) continue;
            
            uint score = agents[i].reputation;
            
            // Boost score if specialty matches description
            if (contains(_description, agents[i].specialty)) {
                score += 20;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestId = i;
            }
        }
    }
    
    function contains(string memory a, string memory b) internal pure returns (bool) {
        bytes memory aBytes = bytes(a);
        bytes memory bBytes = bytes(b);
        
        if (bBytes.length > aBytes.length) return false;
        
        for (uint i = 0; i <= aBytes.length - bBytes.length; i++) {
            bool found = true;
            for (uint j = 0; j < bBytes.length; j++) {
                if (aBytes[i + j] != bBytes[j]) {
                    found = false;
                    break;
                }
            }
            if (found) return true;
        }
        return false;
    }
    
    /**
     * @notice Get all active agents
     */
    function getActiveAgents() external view returns (Agent[] memory) {
        Agent[] memory active = new Agent[](agentCount);
        uint counter = 0;
        
        for (uint i = 1; i <= agentCount; i++) {
            if (agents[i].active) {
                active[counter] = agents[i];
                counter++;
            }
        }
        
        // Trim array
        assembly {
            mstore(active, counter)
        }
        return active;
    }
    
    /**
     * @notice Get jobs for a specific DAO
     */
    function getDAOJobs(string memory _daoDID) external view returns (Job[] memory) {
        uint[] memory jobIds = daoJobs[_daoDID];
        Job[] memory result = new Job[](jobIds.length);
        
        for (uint i = 0; i < jobIds.length; i++) {
            result[i] = jobs[jobIds[i]];
        }
        
        return result;
    }
    
    /**
     * @notice Get jobs for a specific agent
     */
    function getAgentJobs(uint _agentId) external view returns (Job[] memory) {
        uint[] memory jobIds = agentJobs[_agentId];
        Job[] memory result = new Job[](jobIds.length);
        
        for (uint i = 0; i < jobIds.length; i++) {
            result[i] = jobs[jobIds[i]];
        }
        
        return result;
    }
}
