document.addEventListener('DOMContentLoaded', () => {
    // const createFolderBtn = document.getElementById('createFolderBtn');
    const modal = document.getElementById('modal');
    const closeModal = document.getElementsByClassName('close')[0];
    const itemsTableBody = document.getElementById('itemsTableBody');
    const fileSection = document.getElementById('fileSection');
    const share_box=document.getElementById('share_box');
    const sharing=document.getElementById('sharing');
    let currentPath = [];
    let fileSystem = { items: [] };

    closeModal.onclick = function() {
        modal.style.display = 'none';
    }
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
        if (event.target == sharing) {
            sharing.style.display = 'none';
        }
    }
    uploadFileBtn.onclick = function() {
        fileSection.style.display = 'block';
        modal.style.display = 'block';
    }
    function addItem(name, type, size = 0,num, modified) {
        if (!modified) {
            modified = new Date().toLocaleString();
        }
        console.log(`Adding item: ${name}, Modified: ${modified}`);
        let currentDir = getCurrentDir();
        currentDir.items.push({ name, type, size, modified,num });
        renderItems();
    }

    function getCurrentDir() {
        let dir = fileSystem;
        for (let i = 0; i < currentPath.length; i++) {
            dir = dir.items.find(item => item.name === currentPath[i]);
        }
        return dir;
    }

    function renderItems() {
        itemsTableBody.innerHTML = '';
        let currentDir = getCurrentDir();
        currentDir.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.type}</td>
                <td>${item.modified}</td>
                <td>${item.size ? formatSize(item.size) : '-'}</td>
                <td>
                    <div class="action-menu">
                        <button style="width:60px;">⋮</button>
                        <div class="action-menu-content">
                            <a href="#" class="delete">Delete</a>
                            <a href="#" class="share">Share</a>
                            <a href="#" class="download">Download</a>
                        </div>
                    </div>
                </td>
            `;
           
            const deleteBtn = row.querySelector('.delete');
            deleteBtn.onclick = function(event) {
                const response =  fetch("/delete/"+item.name+"/"+item.num, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    }
                });
                event.preventDefault();
                event.stopPropagation();
                currentDir.items = currentDir.items.filter(i => i !== item);
                renderItems();
            }
            const shareBtn = row.querySelector('.share');
            shareBtn.onclick = function() {
                share_box.style.display = 'block';
                share_box.innerHTML=`<p style=" padding-bottom:10px ;">Copy Link:</p> <a href="http://127.0.0.1:8000/download/${item.num}" target="_blank">http://127.0.0.1:8000/download/${item.num}</a>`;
                sharing.style.display = 'block';
            }
            document.addEventListener('DOMContentLoaded', () => {
                const shareBox = document.getElementById('share_box');
            
                function hideOnClickOutside(element) {
                    document.addEventListener('click', function(_event) {
                        if (share_box.style.display === 'block') {
                            share_box.style.display = 'none';
                        }
                    });
                }
            
                hideOnClickOutside(shareBox);
            });
            
            const downloadBtn = row.querySelector('.download');
            downloadBtn.onclick = function() {
                const link = document.createElement('a');
                link.href ="http://127.0.0.1:8000/download/"+item.num; 
                link.click();
                
            }
            itemsTableBody.appendChild(row);
        });
    }

    function formatSize(size) {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let unit = 0;
        while (size >= 1024 && unit < units.length - 1) {
            size /= 1024;
            unit++;
        }
        return size.toFixed(1) + ' ' + units[unit];
    }

    async function fetchUserData() {
        try {
            const response = await fetch("/userdata", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(data);
            data.forEach(item => {
                addItem(item.filename, item.file_type, item.file_size,item.num, item.time);
            });
        } catch (error) {
            console.error("Error fetching user data:", error);
        }
    }
    fetchUserData();
    renderItems();
});
