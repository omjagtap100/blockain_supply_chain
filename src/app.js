App = {
    loading: false,
    processing: false,
    contracts: {},

    load: async () => {
        await App.loadWeb3();
        await App.loadAccount();
        await App.loadContract();
        await App.render();
    },

    loadWeb3: async () => {
        if (window.ethereum) {
            App.web3Provider = window.ethereum;
            window.web3 = new Web3(window.ethereum);
            try {
                await window.ethereum.request({ method: 'eth_requestAccounts' });
            } catch (error) {
                console.error('User denied account access');
            }
            window.ethereum.on('accountsChanged', () => {
                window.location.reload();
            });
        } else if (typeof window.web3 !== 'undefined') {
            App.web3Provider = window.web3.currentProvider;
            window.web3 = new Web3(window.web3.currentProvider);
        } else {
            window.alert('Please install MetaMask and connect to the local Ganache network.');
        }
    },

    loadAccount: async () => {
        if (window.ethereum) {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            App.account = accounts[0];
        } else {
            const accounts = await new Promise((resolve, reject) => {
                web3.eth.getAccounts((err, accs) => (err ? reject(err) : resolve(accs)));
            });
            App.account = accounts[0];
        }
        console.log('Using account', App.account);
    },

    loadContract: async () => {
        const todoList = await $.getJSON('TodoList.json');
        App.contracts.TodoList = TruffleContract(todoList);
        App.contracts.TodoList.setProvider(App.web3Provider);
        App.todoList = await App.contracts.TodoList.deployed();
    },

    render: async () => {
        if (App.loading) return;
        App.setLoading(true);

        $('#account').html(App.account);
        $('#taskList').children().not('.taskTemplate').remove();
        $('#completedTaskList').empty();

        await App.renderTasks();

        App.setLoading(false);
    },

    priorityLabel: (priority) => {
        const labels = { 1: 'Low', 2: 'Medium', 3: 'High' };
        return labels[priority] || 'Medium';
    },

    priorityClass: (priority) => {
        const classes = { 1: 'priority-low', 2: 'priority-medium', 3: 'priority-high' };
        return classes[priority] || 'priority-medium';
    },

    shortAddr: (addr) => {
        if (!addr || addr === '0x0000000000000000000000000000000000000000') return null;
        return addr.slice(0, 6) + '…' + addr.slice(-4);
    },

    renderTasks: async () => {
        let total = 0, pending = 0, completed = 0, highPriority = 0;

        let taskIds = [];
        try {
            const ids = await App.todoList.getActiveTaskIds();
            taskIds = ids.map(id => id.toNumber ? id.toNumber() : Number(id));
        } catch (e) {
            const taskCount = await App.todoList.taskCount();
            for (let i = 1; i <= taskCount; i++) taskIds.push(i);
        }

        const $taskTemplate = $('.taskTemplate');

        for (const taskId of taskIds) {
            const task = await App.todoList.tasks(taskId);

            const id = task[0].toNumber ? task[0].toNumber() : Number(task[0]);
            const content = task[1];
            const taskCompleted = task[2];
            const taskPriority = task[3].toNumber ? task[3].toNumber() : Number(task[3]);
            const taskExists = task[4];
            const assignee = task[5] || null;
            const deadline = task[6] ? (task[6].toNumber ? task[6].toNumber() : Number(task[6])) : 0;

            if (!taskExists) continue;

            total++;
            if (taskCompleted) completed++;
            else pending++;
            if (taskPriority === 3) highPriority++;

            const $item = $taskTemplate.clone();
            $item.removeClass('taskTemplate');
            $item.find('.content').text(content);
            $item.find('.priority-badge')
                .text(App.priorityLabel(taskPriority))
                .addClass(App.priorityClass(taskPriority));

            const shortAssignee = App.shortAddr(assignee);
            if (shortAssignee) {
                $item.find('.assignee-chip')
                    .text(shortAssignee)
                    .attr('title', assignee)
                    .css('display', 'inline-block');
            }

            if (deadline > 0) {
                const d = new Date(deadline * 1000);
                const label = d.toLocaleDateString();
                const isOverdue = !taskCompleted && Date.now() / 1000 > deadline;
                $item.find('.content').append(
                    ' <span style="font-size:0.7rem;color:' +
                    (isOverdue ? 'var(--high)' : 'var(--muted)') +
                    ';margin-left:4px">Due: ' + label + '</span>'
                );
            }

            $item.find('input[type="checkbox"]')
                .prop('name', id)
                .prop('checked', taskCompleted)
                .on('change', App.toggleCompleted);

            const $sel = $item.find('.priority-select');
            $sel.html(
                '<option value="1">Low</option>' +
                '<option value="2">Medium</option>' +
                '<option value="3">High</option>'
            );
            $sel.val(String(taskPriority));
            $sel.prop('name', id);
            $sel.on('change', App.updatePriority);

            $item.find('.btn-delete').prop('name', id).on('click', App.deleteTask);

            if (taskCompleted) {
                $('#completedTaskList').append($item);
            } else {
                $('#taskList').append($item);
            }
            $item.show();
        }

        $('#statTotal').text(total);
        $('#statPending').text(pending);
        $('#statCompleted').text(completed);
        $('#statHigh').text(highPriority);
    },

    createTask: async () => {
        if (App.processing) return;
        App.processing = true;
        App.setLoading(true);

        const content = $('#newTask').val().trim();
        const priority = parseInt($('#newPriority').val(), 10);
        const assignee = $('#newAssignee').val().trim();
        const deadlineStr = $('#newDeadline').val();

        let deadline = 0;
        if (deadlineStr) {
            deadline = Math.floor(new Date(deadlineStr).getTime() / 1000);
        }

        try {
            const isAddr = (addr) => {
                if (!addr) return false;
                if (window.web3 && window.web3.isAddress) return window.web3.isAddress(addr);
                if (window.web3 && window.web3.utils && window.web3.utils.isAddress) return window.web3.utils.isAddress(addr);
                return /^0x[a-fA-F0-9]{40}$/.test(addr);
            };

            if (assignee && isAddr(assignee)) {
                let contentHash = '0x' + '00'.repeat(32);
                if (window.web3 && window.web3.sha3) {
                    contentHash = window.web3.sha3(content);
                } else if (window.web3 && window.web3.utils && window.web3.utils.keccak256) {
                    contentHash = window.web3.utils.keccak256(content);
                }

                if (App.todoList.createShipment) {
                    await App.todoList.createShipment(content, priority, assignee, deadline, contentHash, { from: App.account });
                } else if (App.todoList.methods && App.todoList.methods['createTask(string,uint8,address,uint256,bytes32)']) {
                    await App.todoList.methods['createTask(string,uint8,address,uint256,bytes32)'](
                        content, priority, assignee, deadline, contentHash,
                        { from: App.account }
                    );
                } else {
                    await App.todoList.createTask(content, priority, assignee, deadline, contentHash, { from: App.account });
                }
            } else {
                await App.todoList.createTask(content, priority, { from: App.account });
            }
            App.showToast('Task added to blockchain');
        } catch (err) {
            console.error(err);
            App.showToast('Transaction failed: ' + (err.message || err));
            App.processing = false;
        }
        window.location.reload();
    },

    toggleCompleted: async (e) => {
        if (e) e.stopPropagation();
        if (App.processing) return;
        App.processing = true;
        App.setLoading(true);

        const taskId = e.target.name;
        try {
            await App.todoList.toggleCompleted(taskId, { from: App.account });
            App.showToast('Task status updated');
        } catch (err) {
            console.error(err);
            App.showToast('Not authorised or transaction failed');
            App.processing = false;
        }
        window.location.reload();
    },

    updatePriority: async (e) => {
        if (e) e.stopPropagation();
        if (App.processing) return;
        App.processing = true;
        App.setLoading(true);

        const taskId = e.target.name;
        const priority = parseInt(e.target.value, 10);
        try {
            await App.todoList.updatePriority(taskId, priority, { from: App.account });
            App.showToast('Priority updated');
        } catch (err) {
            console.error(err);
            App.showToast('Only owner can update priority');
            App.processing = false;
        }
        window.location.reload();
    },

    deleteTask: async (e) => {
        if (e) e.stopPropagation();
        if (App.processing) return;
        App.processing = true;
        App.setLoading(true);

        const taskId = e.target.name;
        try {
            await App.todoList.deleteTask(taskId, { from: App.account });
            App.showToast('Task deleted');
        } catch (err) {
            console.error(err);
            App.showToast('Only owner can delete tasks');
            App.processing = false;
        }
        window.location.reload();
    },

    setLoading: (boolean) => {
        App.loading = boolean;
        const loader = $('#loader');
        const content = $('#content');
        if (boolean) {
            loader.show();
            content.hide();
        } else {
            loader.hide();
            content.show();
        }
    },

    showToast: (msg) => {
        const $toast = $('#toast');
        $toast.text(msg).fadeIn(200);
        setTimeout(() => $toast.fadeOut(400), 3000);
    },
};

$(() => {
    $(window).load(() => {
        App.load();
    });
});
