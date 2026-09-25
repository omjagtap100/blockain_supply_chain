#!/usr/bin/env python3
"""
SIT728 Task 10.2HD report generator.
Builds SIT728_10.2HD_Report.docx from plain text content below.
Run: .venv/bin/python3 report/generate_10HD_report.py
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FIG_DIR = "report/figures"
OUTPUT = "SIT728_10.2HD_Report.docx"

GITHUB_LINK = "PASTE_YOUR_GITHUB_REPO_LINK_HERE"
VIDEO_LINK = "https://deakin.au.panopto.com/Panopto/Pages/Viewer.aspx?id=3d5eb804-6dab-45b9-8b74-b4d000e7731a"

HEADING_COLOR = RGBColor(0x1F, 0x2A, 0x44)


def set_cell_shading(cell, color_hex):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    cell._tc.get_or_add_tcPr().append(shd)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_shading(hdr_cells[i], "1F2A44")
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                r.font.size = Pt(10)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for p in cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
    doc.add_paragraph()
    return table


def add_figure(doc, path, caption, width=5.8):
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width))
        last_paragraph = doc.paragraphs[-1]
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].italic = True
    cap.runs[0].font.size = Pt(9)
    doc.add_paragraph()


def add_screenshot_placeholder(doc, label):
    p = doc.add_paragraph()
    run = p.add_run(f"[ Screenshot placeholder — {label} ]")
    run.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x33, 0x33)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()


def h1(doc, text):
    doc.add_heading(text, level=1)


def h2(doc, text):
    doc.add_heading(text, level=2)


def p(doc, text, bold=False, italic=False):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    return para


def bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style='List Bullet')


def build():
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # ---------------- Title page ----------------
    title = doc.add_heading('Priority Shipment Tracker DApp', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run('A decentralised application for multi-party supply chain tracking')
    r.italic = True
    r.font.size = Pt(13)

    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lines = [
        'SIT728 — Blockchain Technologies and Real-World Applications',
        'High Distinction Task 10.2HD — Decentralised App Features',
        '',
        'Om Santosh Jagtap',
        'Student ID: s225435163',
        'Tutor: Shantanu Pal',
        '',
        f'GitHub repository: {GITHUB_LINK}',
        f'Video demonstration: {VIDEO_LINK}',
    ]
    for line in lines:
        info.add_run(line + '\n')

    doc.add_page_break()

    # ---------------- 1. Position statement ----------------
    h1(doc, '1. Introduction and Position')
    p(doc, (
        'This report covers the Priority Shipment Tracker, a decentralised application built on '
        'Ethereum for tracking shipments across a supply chain. The app started as a simple todo '
        'list contract and was extended for this task with three features that matter most for a real '
        'supply chain: security, privacy and scalability.'
    ))
    p(doc, (
        'The position taken in this report is straightforward. A public blockchain is a good fit for '
        'supply chain tracking when the parties involved do not trust each other but still need to agree '
        'on a shared history of events. The chain does not need to hold every detail of a shipment. It '
        'only needs to hold enough to prove who did what and when, while keeping commercially sensitive '
        'information off-chain. That is the design used here, and the rest of this report explains how '
        'each part of the contract supports it.'
    ))

    # ---------------- 2. The problem ----------------
    h1(doc, '2. The Supply Chain Problem')
    p(doc, (
        'A shipment usually passes through several independent parties before it reaches a customer: a '
        'manufacturer, one or more freight carriers, customs, and a retailer or end client. Each of these '
        'parties keeps its own records. When a dispute comes up, for example a shipment marked as delivered '
        'that the retailer says never arrived, there is no single shared record both sides trust. Paper '
        'trails and PDFs get lost, timestamps get edited, and a party with more market power can simply '
        'insist their version of events is correct.'
    ))
    p(doc, (
        'A blockchain fixes the trust problem because no single party can quietly edit a past record. But a '
        'naive blockchain design creates two new problems. First, if every shipment detail is written to a '
        'public chain, competitors and the public can read commercial data like pricing and supplier names. '
        'Second, if the app has to scan the entire chain to answer a simple question like "what are my open '
        'shipments", it becomes slow and expensive as the number of shipments grows. The three features in '
        'this project were chosen to directly address these two problems, on top of the basic trust '
        'guarantee a blockchain already gives.'
    ))

    # ---------------- 3. System overview ----------------
    h1(doc, '3. System Overview')
    p(doc, (
        'The app is a browser front end (index.html and app.js) that talks to MetaMask, which signs '
        'transactions and forwards them to a local Ganache blockchain running the TodoList smart contract. '
        'All shipment data lives in the contract. The front end only reads and writes through Web3 and '
        'TruffleContract, it holds no state of its own.'
    ))
    add_figure(doc, f'{FIG_DIR}/architecture_hd.png', 'Figure 1 — System architecture: browser, MetaMask, Ganache and the smart contract')

    add_table(doc, ['Item', 'Value'], [
        ['Smart contract language', 'Solidity ^0.5.0'],
        ['Development framework', 'Truffle v5'],
        ['Local blockchain', 'Ganache, http://127.0.0.1:8545'],
        ['Chain ID', '1337'],
        ['Front end', 'HTML5 / CSS3 / jQuery, Web3.js 0.20.x, TruffleContract'],
        ['Wallet', 'MetaMask'],
    ])

    p(doc, (
        'The diagram below shows what happens when a user creates a new shipment step. The important '
        'part is that nothing is written to the chain until the user approves the transaction in MetaMask, '
        'so a shipment record can never be created without the sender knowingly signing it.'
    ))
    add_figure(doc, f'{FIG_DIR}/tx_flow.png', 'Figure 2 — Transaction flow when a shipment step is created')

    # ---------------- 4. Security ----------------
    h1(doc, '4. Feature One: Security (Access Control)')
    p(doc, (
        'The contract uses an Ownable pattern written directly into TodoList.sol rather than importing '
        'OpenZeppelin, because the project targets Solidity 0.5 and keeps the dependency count low. The '
        'deployer of the contract becomes the owner, and an onlyOwner modifier guards the functions that '
        'should not be open to the public.'
    ))
    bullets(doc, [
        'deleteTask() — only the owner can remove a shipment record.',
        'updatePriority() — only the owner can re-prioritise a shipment.',
        'updateAssignee() — only the owner can reassign a shipment to a different carrier.',
        'transferOwnership() — only the current owner can hand control to a new address, and the new '
        'address cannot be the zero address, which stops the contract from being locked out by accident.',
    ])
    p(doc, (
        'One function needed a mixed rule rather than a strict owner-only check. Marking a shipment step as '
        'completed should be doable by the logistics manager (the owner) or by the carrier the step was '
        'assigned to, since the carrier is the one who actually knows the parcel arrived. This is enforced '
        'with a single require statement: msg.sender must equal owner or the assignee stored on that task. '
        'Anyone else calling toggleCompleted() gets reverted.'
    ))
    add_figure(doc, f'{FIG_DIR}/access_control.png', 'Figure 3 — Which caller can reach which function')
    p(doc, (
        'This was tested directly rather than assumed. The test suite creates an "attacker" account that '
        'is neither the owner nor an assignee, and confirms that updatePriority, deleteTask and '
        'toggleCompleted all revert when called from that account. A live version of this check is also in '
        'the screenshot below, where the attacker account is used in MetaMask to try to delete a task.'
    ))
    add_screenshot_placeholder(doc, 'attacker account rejected when calling a protected function')

    # ---------------- 5. Privacy ----------------
    h1(doc, '5. Feature Two: Privacy (Assignee Addressing and Content Hashing)')
    p(doc, (
        'The original Task struct only stored a description, a priority and a completed flag. For a supply '
        'chain use case that is not enough and it is also too much, in different ways. It is not enough '
        'because there is no way to say which carrier is responsible for a step. It is too much because if '
        'the full cargo manifest, price, or customer details were stored as plain text in the description, '
        'anyone watching the chain could read it.'
    ))
    p(doc, (
        'Three fields were added to the struct to fix this: address assignee, uint deadline, and bytes32 '
        'contentHash. The assignee is the carrier or party responsible for that step. The deadline is a '
        'plain SLA timestamp, useful for the UI, and not sensitive. The contentHash is where the privacy '
        'design lives: the full shipment document (manifest, invoice, customs declaration) is kept off-chain, '
        'for example on IPFS, and only its keccak256 hash is written to the contract.'
    ))
    add_figure(doc, f'{FIG_DIR}/privacy_model.png', 'Figure 4 — Sensitive data stays off-chain, only a hash fingerprint goes on-chain')
    p(doc, (
        'This gives two things at once. First, non-repudiation: if a document is later produced, anyone can '
        'hash it and compare it to the on-chain value to prove it has not been altered since the shipment '
        'step was recorded. Second, privacy: a competitor reading the public chain sees a 32-byte hash and '
        'learns nothing about the contents.'
    ))
    p(doc, (
        'Assignee addressing is also guarded on the read side. getTasksByAssignee(address) requires the '
        'caller to be either the owner or the assignee being looked up. A third party calling this function '
        'for another company\'s address is reverted, so a competing carrier cannot enumerate what shipments '
        'a rival carrier has been assigned.'
    ))

    # ---------------- 6. Scalability ----------------
    h1(doc, '6. Feature Three: Scalability (Indexed Events and Batch Queries)')
    p(doc, (
        'Two changes were made here, both aimed at cutting down the number of calls the front end has to '
        'make as the number of shipment records grows.'
    ))
    h2(doc, '6.1 Indexed event parameters')
    p(doc, (
        'TaskCreated, TaskCompleted, PriorityUpdated and AssigneeUpdated all mark key fields (id, priority, '
        'assignee) as indexed. Ethereum nodes store indexed values in a Bloom filter attached to each block, '
        'so a front end asking "show me every high priority shipment" can filter directly through the node '
        'instead of downloading and scanning every event in every block.'
    ))
    add_figure(doc, f'{FIG_DIR}/event_indexing.png', 'Figure 5 — Filtering indexed events skips the full scan')
    h2(doc, '6.2 Batch querying with getActiveTaskIds()')
    p(doc, (
        'The original app pattern loops from 1 to taskCount and makes one JSON-RPC call per task to check '
        'if it still exists. For N tasks that is 1 + N network round trips. getActiveTaskIds() moves that '
        'loop on-chain and returns a single array of the IDs that still exist, so the front end makes one '
        'call no matter how many shipments are in the system.'
    ))
    p(doc, (
        'This is a genuine trade-off worth being honest about. The loop inside getActiveTaskIds() still runs '
        'in O(n) gas cost, it is just paid once at read time rather than as N separate round trips. For a '
        'small class demo with a handful of shipments this is a clear win. At production scale, with '
        'thousands of shipments, the better answer is off-chain indexing (for example, The Graph) reading '
        'events straight from the chain, and this is noted as future work in Section 10.'
    ))

    # ---------------- 7. Comparative analysis ----------------
    h1(doc, '7. Comparative Analysis: How This Fits the Wider Landscape')
    p(doc, (
        'Blockchain-based supply chain tracking is not a new idea, and looking at how larger projects have '
        'handled it helps explain some of the choices made here.'
    ))
    add_table(doc, ['Platform', 'Chain type', 'Privacy approach', 'Where it stands'], [
        ['IBM Food Trust', 'Permissioned (Hyperledger Fabric)', 'Data shared only with channel members', 'Still running, used by retailers such as Walmart for produce tracking'],
        ['TradeLens (IBM/Maersk)', 'Permissioned', 'Access controlled per participant', 'Shut down in 2023 after failing to get enough competing carriers to join'],
        ['VeChain ToolChain', 'Public, purpose-built L1', 'Product data on-chain, hashed where sensitive', 'Active, used for anti-counterfeiting and provenance'],
        ['This project', 'Public (Ethereum-style, local Ganache)', 'Off-chain content + on-chain hash, address-gated queries', 'Local demo, same pattern scales to testnet or mainnet'],
    ])
    p(doc, (
        'The TradeLens shutdown is a useful data point. It was technically solid but it was owned and run '
        'by one shipping line, and rival carriers were reluctant to put their data on a platform controlled '
        'by a competitor. That is exactly the trust problem described in Section 2, and it shows that the '
        'choice of who controls the chain matters as much as the technology itself. A permissioned chain '
        'run by IBM Food Trust survives because it positions itself as a neutral consortium tool rather than '
        'a single company\'s platform.'
    ))
    p(doc, (
        'This project leans toward the public-chain end of that spectrum rather than a private consortium '
        'chain like Fabric. The trade-off is deliberate. A public chain like Ethereum removes the "who runs '
        'the server" trust question entirely, no single company can be accused of favouring itself, but it '
        'means privacy has to be designed in at the application layer instead of relying on network-level '
        'access control. That is the reasoning behind keeping cargo documents off-chain and only publishing '
        'a hash, the same privacy outcome as a permissioned chain, without needing a consortium to agree on '
        'who is allowed to join the network.'
    ))
    p(doc, (
        'The wider trend in the industry over the last few years has moved toward this hybrid model, public '
        'settlement combined with off-chain or hashed data, rather than either fully public or fully closed '
        'systems. This design sits in that middle ground.'
    ))

    # ---------------- 8. Testing ----------------
    h1(doc, '8. Automated Testing')
    p(doc, (
        'The contract is covered by 16 automated Truffle tests in test/TodoList.test.js, run against a '
        'local Ganache instance. They fall into two groups.'
    ))
    add_table(doc, ['Group', 'Count', 'What it checks'], [
        ['Functional', '6', 'Deployment, listing tasks, creating tasks, toggling completion, updating priority, deleting a task'],
        ['Security & privacy invariants', '10', 'Owner set correctly on deploy, non-owner rejected on updatePriority and deleteTask, task creation with an assignee, assignee can toggle their own task, non-assignee rejected on toggleCompleted, getActiveTaskIds only returns existing tasks, getTasksByAssignee returns the right tasks for the assignee, a non-owner/non-assignee is rejected by getTasksByAssignee, and ownership can be safely transferred'],
    ])
    add_screenshot_placeholder(doc, 'truffle test output, 16 passing')

    # ---------------- 9. Security scanning ----------------
    h1(doc, '9. Security Scanning and Penetration Testing')
    p(doc, (
        'The contract was scanned with Slither, a real static analysis tool for Solidity, run against '
        'solc 0.5.0 to match the contract pragma. The full raw output is kept in '
        'security/slither_raw_output.txt and the interpreted findings are in security/slither_report.txt. '
        'The summary is below.'
    ))
    add_table(doc, ['Severity', 'Count', 'Notes'], [
        ['Critical', '0', '—'],
        ['High', '0', '—'],
        ['Medium', '0', 'Was 1 before this review (see front-end finding below), fixed in this codebase.'],
        ['Low', '2', 'controlled-array-length on tasksByAssignee (low impact, grows one address-scoped entry per call, not attacker-controllable in size); transferOwnership() changes owner without emitting the existing OwnershipTransferred event.'],
        ['Info / gas', '24', '18 naming-convention notices (parameters use a leading underscore rather than mixedCase, style only), outdated compiler notice, 2 external-function/calldata gas suggestions.'],
    ])
    p(doc, (
        'Slither did not flag re-entrancy, unprotected self-destruct, arbitrary sends, tx.origin use or '
        'delegatecall, because none of these patterns exist in the contract: no ETH is ever transferred and '
        'there are no external calls at all. What Slither cannot check is whether the right address is '
        'allowed to call the right function, since that depends on the contract\'s own business rules rather '
        'than a generic pattern. That was checked by hand: every owner-only function was matched against its '
        'modifier, and the mixed owner-or-assignee rule on toggleCompleted() was confirmed against the tests '
        'in test/TodoList.test.js. This matches Figure 3 in Section 4.'
    ))
    p(doc, (
        'The front end was checked manually, since Slither only covers Solidity. This review found one real '
        'issue: src/app.js was rendering task descriptions with jQuery\'s .html(), which does not escape '
        'HTML, so a task description containing a script tag would run in the browser of anyone viewing the '
        'list. This was fixed during this review by switching to .text(). CSRF does not apply here because '
        'there is no session cookie or server-side login, every write goes through a MetaMask signature. '
        'Replay attacks are handled by Ethereum\'s own nonce mechanism through MetaMask. The app runs on '
        'localhost during the demo, so man-in-the-middle risk is noted as a production concern (use HTTPS '
        'and a trusted RPC endpoint) rather than a current issue.'
    ))
    add_screenshot_placeholder(doc, 'terminal output of the slither scan')

    # ---------------- 10. Limitations ----------------
    h1(doc, '10. Limitations and Future Work')
    bullets(doc, [
        'Solidity 0.5 was kept for compatibility with the base project; a production version should move to '
        '0.8.x for built-in overflow protection and clearer revert reasons.',
        'getActiveTaskIds() is O(n) in gas. At real-world scale this should be replaced with off-chain event '
        'indexing, for example The Graph, instead of an on-chain loop.',
        'Content hashes assume the off-chain file (IPFS or similar) is actually pinned and available; the '
        'contract only proves what the hash was, not that the file still exists somewhere.',
        'The current deployment is local Ganache only. Moving to a public testnet (Sepolia) would be the '
        'next step toward a real deployment, with the same contract logic unchanged.',
    ])

    # ---------------- 11. Documentation ----------------
    h1(doc, '11. In-App Documentation')
    p(doc, (
        'The web page includes a built-in wiki panel using collapsible sections, covering the security '
        'model, the privacy/hashing approach, the scalability changes, how to run the project locally, how '
        'the features map onto a real supply chain, and a short summary of the security scan. This satisfies '
        'the requirement that the page itself explain the features and how they were implemented, not just '
        'the code.'
    ))
    add_screenshot_placeholder(doc, 'wiki / tutorial panel expanded in the browser')

    # ---------------- 12. Demonstration ----------------
    h1(doc, '12. Demonstration')
    p(doc, (
        'The app was run end to end on a local Ganache chain: contract deployed with Truffle, front end '
        'served locally, and MetaMask connected to http://127.0.0.1:8545 (chain ID 1337). A full walkthrough '
        'is recorded in the video linked below, covering creating a shipment, assigning it to a carrier, '
        'completing it, and the attacker account being rejected.'
    ))
    p(doc, f'Video demonstration: {VIDEO_LINK}')
    p(doc, f'Source code repository: {GITHUB_LINK}')
    add_screenshot_placeholder(doc, 'ganache running with the 3 demo accounts')
    add_screenshot_placeholder(doc, 'truffle migrate — contract deployed')
    add_screenshot_placeholder(doc, 'dashboard with metrics and sample shipments')
    add_screenshot_placeholder(doc, 'task creation form filled in, before submitting')
    add_screenshot_placeholder(doc, 'MetaMask transaction confirmation popup')
    add_screenshot_placeholder(doc, 'a shipment step marked as completed')

    h2(doc, 'Local Ganache demo accounts')
    p(doc, (
        'These are Ganache\'s own deterministic test accounts, used only on the local chain for this demo. '
        'They hold no real funds and the keys are not secrets.'
    ))
    add_table(doc, ['Role', 'Address'], [
        ['Owner / logistics manager', '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'],
        ['Alice / carrier (assignee)', '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'],
        ['Attacker / unauthorised account', '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'],
    ])

    # ---------------- 13. Conclusion ----------------
    h1(doc, '13. Conclusion')
    p(doc, (
        'This project takes a plain todo list contract and turns it into something closer to a real supply '
        'chain tool, by adding three things a real deployment would actually need: proper access control, a '
        'way to keep sensitive shipment details private while still proving they are genuine, and a way to '
        'query the chain that does not fall over as the number of shipments grows. None of these three ideas '
        'work well on their own, a private chain without indexing is still slow, and an indexed public chain '
        'without hashing is still exposed, they only add up to something usable when combined, which is what '
        'this contract does.'
    ))

    doc.save(OUTPUT)
    print(f'Saved {OUTPUT}')


if __name__ == '__main__':
    build()
