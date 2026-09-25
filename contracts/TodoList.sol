pragma solidity ^0.5.0;

contract TodoList {
  address public owner;

  constructor() public {
    owner = msg.sender;
    createTask("Check out dappuniversity.com", 2, address(0), 0, bytes32(0));
  }

  modifier onlyOwner() {
    require(msg.sender == owner, "Caller is not the owner");
    _;
  }

  function transferOwnership(address _newOwner) public onlyOwner {
    require(_newOwner != address(0), "New owner is the zero address");
    owner = _newOwner;
  }

  uint public taskCount = 0;

  struct Task {
    uint     id;
    string   content;
    bool     completed;
    uint8    priority;
    bool     exists;
    address  assignee;
    uint     deadline;

    bytes32  contentHash;  }

  mapping(uint => Task) public tasks;
  mapping(address => uint[]) private tasksByAssignee;

  event TaskCreated(
    uint    indexed id,
    string          content,
    bool            completed,
    uint8   indexed priority,
    address indexed assignee
  );

  event TaskCompleted(
    uint    indexed id,
    bool            completed
  );

  event TaskDeleted(
    uint    indexed id
  );

  event PriorityUpdated(
    uint    indexed id,
    uint8           priority
  );

  event AssigneeUpdated(
    uint    indexed id,
    address indexed assignee
  );

  event OwnershipTransferred(
    address indexed previousOwner,
    address indexed newOwner
  );

  function createTask(
    string  memory _content,
    uint8          _priority,
    address        _assignee,
    uint           _deadline,
    bytes32        _contentHash
  ) public {
    require(_priority >= 1 && _priority <= 3, "Priority must be 1, 2, or 3");
    taskCount++;
    tasks[taskCount] = Task(
      taskCount,
      _content,
      false,
      _priority,
      true,
      _assignee,
      _deadline,
      _contentHash
    );
    if (_assignee != address(0)) {
      tasksByAssignee[_assignee].push(taskCount);
    }
    emit TaskCreated(taskCount, _content, false, _priority, _assignee);
  }

  function createTask(string memory _content, uint8 _priority) public {
    createTask(_content, _priority, address(0), 0, bytes32(0));
  }

  function createShipment(
    string  memory _content,
    uint8          _priority,
    address        _assignee,
    uint           _deadline,
    bytes32        _contentHash
  ) public {
    createTask(_content, _priority, _assignee, _deadline, _contentHash);
  }

  function toggleCompleted(uint _id) public {
    require(tasks[_id].exists, "Task does not exist");
    require(
      msg.sender == owner || msg.sender == tasks[_id].assignee,
      "Not authorised to toggle this task"
    );
    Task memory _task = tasks[_id];
    _task.completed = !_task.completed;
    tasks[_id] = _task;
    emit TaskCompleted(_id, _task.completed);
  }

  function updatePriority(uint _id, uint8 _priority) public onlyOwner {
    require(tasks[_id].exists, "Task does not exist");
    require(_priority >= 1 && _priority <= 3, "Priority must be 1, 2, or 3");
    tasks[_id].priority = _priority;
    emit PriorityUpdated(_id, _priority);
  }

  function deleteTask(uint _id) public onlyOwner {
    require(tasks[_id].exists, "Task does not exist");
    delete tasks[_id];
    emit TaskDeleted(_id);
  }

  function updateAssignee(uint _id, address _assignee) public onlyOwner {
    require(tasks[_id].exists, "Task does not exist");
    tasks[_id].assignee = _assignee;
    tasksByAssignee[_assignee].push(_id);
    emit AssigneeUpdated(_id, _assignee);
  }

  function getTasksByAssignee(address _assignee)
    public
    view
    returns (uint[] memory)
  {
    require(
      msg.sender == owner || msg.sender == _assignee,
      "Not authorised to view these tasks"
    );
    return tasksByAssignee[_assignee];
  }

  function getActiveTaskIds() public view returns (uint[] memory) {
    uint[] memory temp = new uint[](taskCount);
    uint count = 0;
    for (uint i = 1; i <= taskCount; i++) {
      if (tasks[i].exists) {
        temp[count] = i;
        count++;
      }
    }
    uint[] memory result = new uint[](count);
    for (uint j = 0; j < count; j++) {
      result[j] = temp[j];
    }
    return result;
  }
}
