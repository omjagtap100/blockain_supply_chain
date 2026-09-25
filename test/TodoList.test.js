const TodoList = artifacts.require('./TodoList.sol')

contract('TodoList', (accounts) => {
  const owner     = accounts[0]
  const alice     = accounts[1]
  const attacker  = accounts[2]

  before(async () => {
    this.todoList = await TodoList.deployed()
  })

  it('deploys successfully', async () => {
    const address = await this.todoList.address
    assert.notEqual(address, 0x0)
    assert.notEqual(address, '')
    assert.notEqual(address, null)
    assert.notEqual(address, undefined)
  })

  it('lists tasks', async () => {
    const taskCount = await this.todoList.taskCount()
    const task      = await this.todoList.tasks(taskCount)
    assert.equal(task.id.toNumber(), taskCount.toNumber())
    assert.equal(task.content,    'Check out dappuniversity.com')
    assert.equal(task.completed,  false)
    assert.equal(task.priority.toNumber(), 2)
    assert.equal(task.exists,     true)
    assert.equal(taskCount.toNumber(), 1)
  })

  it('creates tasks', async () => {
    const result    = await this.todoList.createTask('A new task', 3, { from: owner })
    const taskCount = await this.todoList.taskCount()
    assert.equal(taskCount, 2)
    const event = result.logs[0].args
    assert.equal(event.id.toNumber(),      2)
    assert.equal(event.content,           'A new task')
    assert.equal(event.completed,          false)
    assert.equal(event.priority.toNumber(), 3)
  })

  it('toggles task completion', async () => {
    const result = await this.todoList.toggleCompleted(1, { from: owner })
    const task   = await this.todoList.tasks(1)
    assert.equal(task.completed, true)
    const event = result.logs[0].args
    assert.equal(event.id.toNumber(), 1)
    assert.equal(event.completed,     true)
  })

  it('updates task priority', async () => {
    const result = await this.todoList.updatePriority(2, 1, { from: owner })
    const task   = await this.todoList.tasks(2)
    assert.equal(task.priority.toNumber(), 1)
    const event = result.logs[0].args
    assert.equal(event.id.toNumber(),       2)
    assert.equal(event.priority.toNumber(), 1)
  })

  it('deletes a task', async () => {
    const result = await this.todoList.deleteTask(2, { from: owner })
    const task   = await this.todoList.tasks(2)
    assert.equal(task.exists, false)
    const event = result.logs[0].args
    assert.equal(event.id.toNumber(), 2)
  })

  it('owner is set to deployer', async () => {
    const contractOwner = await this.todoList.owner()
    assert.equal(contractOwner.toLowerCase(), owner.toLowerCase())
  })

  it('non-owner cannot update priority', async () => {
    await this.todoList.createTask('Attacker target', 2, { from: owner })
    const taskCount = await this.todoList.taskCount()
    const taskId    = taskCount.toNumber()

    let reverted = false
    try {
      await this.todoList.updatePriority(taskId, 3, { from: attacker })
    } catch (e) {
      reverted = e.message.includes('not the owner') || e.message.includes('revert')
    }
    assert.equal(reverted, true, 'Expected revert for non-owner updatePriority')
  })

  it('non-owner cannot delete task', async () => {
    const taskCount = await this.todoList.taskCount()
    const taskId    = taskCount.toNumber()

    let reverted = false
    try {
      await this.todoList.deleteTask(taskId, { from: attacker })
    } catch (e) {
      reverted = e.message.includes('not the owner') || e.message.includes('revert')
    }
    assert.equal(reverted, true, 'Expected revert for non-owner deleteTask')
  })

  it('creates task with assignee', async () => {
    const content     = 'Ship parcel to warehouse B'
    const priority    = 3
    const deadline    = Math.floor(Date.now() / 1000) + 86400
    const contentHash = web3.utils.keccak256('ipfs://QmExampleHash')

    const result    = await this.todoList.methods['createTask(string,uint8,address,uint256,bytes32)'](
      content, priority, alice, deadline, contentHash, { from: owner }
    )
    const taskCount = await this.todoList.taskCount()
    const task      = await this.todoList.tasks(taskCount)

    assert.equal(task.content,              content)
    assert.equal(task.assignee.toLowerCase(), alice.toLowerCase())
    assert.equal(task.deadline.toNumber(),   deadline)
    assert.notEqual(task.contentHash, '0x' + '00'.repeat(32))
  })

  it('assignee can toggle their own task', async () => {
    const taskCount = await this.todoList.taskCount()
    const taskId    = taskCount.toNumber()

    const result = await this.todoList.toggleCompleted(taskId, { from: alice })
    const task   = await this.todoList.tasks(taskId)
    assert.equal(task.completed, true)
  })

  it('non-assignee non-owner cannot toggle task', async () => {
    const taskCount = await this.todoList.taskCount()
    const taskId    = taskCount.toNumber()

    await this.todoList.toggleCompleted(taskId, { from: owner })

    let reverted = false
    try {
      await this.todoList.toggleCompleted(taskId, { from: attacker })
    } catch (e) {
      reverted = e.message.includes('Not authorised') || e.message.includes('revert')
    }
    assert.equal(reverted, true, 'Expected revert for non-authorised toggleCompleted')
  })

  it('getActiveTaskIds returns only existing task ids', async () => {
    const ids = await this.todoList.getActiveTaskIds()
    for (let i = 0; i < ids.length; i++) {
      const task = await this.todoList.tasks(ids[i].toNumber())
      assert.equal(task.exists, true)
    }
    assert.isAbove(ids.length, 0)
  })

  it('getTasksByAssignee returns correct tasks for alice', async () => {
    const ids = await this.todoList.getTasksByAssignee(alice, { from: alice })
    assert.isAbove(ids.length, 0)
  })

  it('non-owner non-assignee cannot query getTasksByAssignee', async () => {
    let reverted = false
    try {
      await this.todoList.getTasksByAssignee(alice, { from: attacker })
    } catch (e) {
      reverted = e.message.includes('Not authorised') || e.message.includes('revert')
    }
    assert.equal(reverted, true, 'Expected revert for privacy violation')
  })

  it('owner can transfer ownership', async () => {
    const newOwner   = accounts[3]
    await this.todoList.transferOwnership(newOwner, { from: owner })
    const currentOwner = await this.todoList.owner()
    assert.equal(currentOwner.toLowerCase(), newOwner.toLowerCase())
    await this.todoList.transferOwnership(owner, { from: newOwner })
  })
})
