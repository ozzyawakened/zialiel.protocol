// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EntityStack
 * @notice Bridges traditional legal entities (LLCs, corporations) with DAO governance
 * @dev Allows companies to register on-chain and link to DAOs
 */
contract EntityStack {
    address public owner;
    address public wisdomOracle;
    
    struct Entity {
        string did;                 // e.g., "did:zialiel:company:acme"
        string name;                // Legal name
        string jurisdiction;        // e.g., "Norway", "Wyoming LLC"
        string operatingAgreement;  // IPFS hash of legal docs
        address legalRepresentative; // Person authorized to act legally
        address linkedDAO;          // The DAO that governs this entity
        uint256 registrationDate;
        bool active;
        uint256 reputation;          // 0-100, based on compliance
    }
    
    struct TreasuryUpdate {
        uint256 timestamp;
        string reportHash;           // IPFS hash of financial report
        uint256 totalValue;          // In wei/cents
        string period;               // e.g., "Q1-2026"
    }
    
    mapping(string => Entity) public entities;           // DID -> Entity
    mapping(string => TreasuryUpdate[]) public treasuryHistory; // DID -> updates
    mapping(address => string) public repToEntity;       // Representative -> entity DID
    
    event EntityRegistered(string did, string name, string jurisdiction, address rep);
    event EntityLinked(string did, address dao);
    event TreasuryUpdated(string did, uint256 value, string period);
    event ReputationUpdated(string did, uint256 oldRep, uint256 newRep);
    
    modifier onlyRepresentative(string memory _did) {
        require(repToEntity[msg.sender] == _did, "Not authorized representative");
        _;
    }
    
    modifier onlyLinkedDAO(string memory _did) {
        require(entities[_did].linkedDAO == msg.sender, "Only linked DAO can call");
        _;
    }
    
    constructor(address _wisdomOracle) {
        owner = msg.sender;
        wisdomOracle = _wisdomOracle;
    }
    
    /**
     * @notice Register a traditional company as an on-chain entity
     * @param _did Unique identifier for the entity
     * @param _name Legal name
     * @param _jurisdiction Where it's registered
     * @param _operatingAgreement IPFS hash of legal documents
     */
    function registerEntity(
        string memory _did,
        string memory _name,
        string memory _jurisdiction,
        string memory _operatingAgreement
    ) external {
        require(entities[_did].registrationDate == 0, "Entity already exists");
        require(repToEntity[msg.sender] == "", "Address already represents an entity");
        
        entities[_did] = Entity({
            did: _did,
            name: _name,
            jurisdiction: _jurisdiction,
            operatingAgreement: _operatingAgreement,
            legalRepresentative: msg.sender,
            linkedDAO: address(0),
            registrationDate: block.timestamp,
            active: true,
            reputation: 50 // Start neutral
        });
        
        repToEntity[msg.sender] = _did;
        
        emit EntityRegistered(_did, _name, _jurisdiction, msg.sender);
    }
    
    /**
     * @notice Link an entity to a DAO (called by representative)
     * @param _did Entity DID
     * @param _daoAddress Address of the DAO contract
     */
    function linkToDAO(string memory _did, address _daoAddress) external onlyRepresentative(_did) {
        Entity storage entity = entities[_did];
        require(entity.active, "Entity not active");
        require(entity.linkedDAO == address(0), "Already linked");
        
        entity.linkedDAO = _daoAddress;
        
        emit EntityLinked(_did, _daoAddress);
    }
    
    /**
     * @notice Update treasury information (called by linked DAO)
     * @param _did Entity DID
     * @param _reportHash IPFS hash of financial report
     * @param _totalValue Total value in wei/cents
     * @param _period Reporting period
     */
    function updateTreasury(
        string memory _did,
        string memory _reportHash,
        uint256 _totalValue,
        string memory _period
    ) external onlyLinkedDAO(_did) {
        treasuryHistory[_did].push(TreasuryUpdate({
            timestamp: block.timestamp,
            reportHash: _reportHash,
            totalValue: _totalValue,
            period: _period
        }));
        
        emit TreasuryUpdated(_did, _totalValue, _period);
    }
    
    /**
     * @notice Update entity reputation (called by oracle or DAO)
     * @param _did Entity DID
     * @param _newRep New reputation score (0-100)
     */
    function updateReputation(string memory _did, uint256 _newRep) external {
        // Can be called by wisdom oracle or the linked DAO
        require(
            msg.sender == wisdomOracle || 
            msg.sender == entities[_did].linkedDAO,
            "Not authorized"
        );
        require(_newRep <= 100, "Reputation must be 0-100");
        
        uint256 oldRep = entities[_did].reputation;
        entities[_did].reputation = _newRep;
        
        emit ReputationUpdated(_did, oldRep, _newRep);
    }
    
    /**
     * @notice Deactivate an entity (called by representative)
     */
    function deactivate(string memory _did) external onlyRepresentative(_did) {
        entities[_did].active = false;
    }
    
    // ============================================================
    // VIEW FUNCTIONS
    // ============================================================
    
    function getEntity(string memory _did) external view returns (Entity memory) {
        return entities[_did];
    }
    
    function getTreasuryHistory(string memory _did) external view returns (TreasuryUpdate[] memory) {
        return treasuryHistory[_did];
    }
    
    function getLatestTreasury(string memory _did) external view returns (TreasuryUpdate memory) {
        TreasuryUpdate[] storage history = treasuryHistory[_did];
        require(history.length > 0, "No treasury data");
        return history[history.length - 1];
    }
    
    function getEntityByRepresentative(address _rep) external view returns (Entity memory) {
        string memory did = repToEntity[_rep];
        require(bytes(did).length > 0, "Address not a representative");
        return entities[did];
    }
}
