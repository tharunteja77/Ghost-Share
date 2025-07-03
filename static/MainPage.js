document.addEventListener('DOMContentLoaded', () => {
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
    function addItem(name, type, size = 0, num, modified, cloudinary_url){
        if (!modified) {
            modified = new Date().toLocaleString();
        }
        console.log(`Adding item: ${name}, Modified: ${modified}`);
        console.log("ADDED FILE:", { name, type, size, num, modified, cloudinary_url });
        let currentDir = getCurrentDir();
        currentDir.items.push({ name, type, size, num, modified, cloudinary_url });
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
                event.preventDefault();
                event.stopPropagation();

                if (!item.num) {
                    alert(`Invalid file identifier for ${item.name}`);
                    return;
                }

                fetch("/delete/" + item.name + "/" + item.num, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    }
                }).then(res => {
                    if (!res.ok) throw new Error(`Failed to delete file: ${res.status}`);
                    currentDir.items = currentDir.items.filter(i => i !== item);
                    renderItems();
                }).catch(err => {
                    alert(err.message);
                });
            }

            const shareBtn = row.querySelector('.share');
                 shareBtn.onclick = function () {
                 const downloadUrl = item.cloudinary_url;

                        share_box.style.display = 'block';
                        share_box.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px;color: white;">
                            <span style="padding-bottom: 10px;">Copy Link:</span>
                            <button id="copy-btn" style="display:inline; background: none; border: none; cursor: pointer; color: white; font-size: 18px;">
                                    <i class="fas fa-copy"></i>
                                </button>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <a href="${downloadUrl}" target="_blank">${downloadUrl}</a>
                                
                            </div>
                        `;

                        sharing.style.display = 'block';

                        const copyBtn = document.getElementById("copy-btn");
                        copyBtn.onclick = function () {
                            navigator.clipboard.writeText(downloadUrl).then(() => {
                                toast.success("Copied to clipboard");
                            }).catch(() => {
                                toast.error("Failed to copy");
                            });
                        };

                        // Detect click outside
                        const handleClickOutside = (event) => {
                            if (!share_box.contains(event.target) && event.target !== shareBtn) {
                                share_box.style.display = 'none';
                                sharing.style.display = 'none';
                                document.removeEventListener("click", handleClickOutside);
                            }
                        };

                        setTimeout(() => {
                            document.addEventListener("click", handleClickOutside);
                        }, 0);
                    };

            
           
          const downloadBtn = row.querySelector('.download');
                downloadBtn.onclick = function () {
                const url = item.cloudinary_url;
                const modifiedUrl = url.includes("fl_attachment")
                    ? url
                    : url.replace("/upload/", "/upload/fl_attachment/");

                const link = document.createElement('a');
                link.href = modifiedUrl;
                link.download = item.name;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            };

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
                   const fixedUrl = item.cloudinary_url.replace("/upload/", "/upload/fl_attachment/");
                   addItem(item.filename, item.file_type, item.file_size, item.file_code, item.time, fixedUrl);            });
        } catch (error) {
            console.error("Error fetching user data:", error);
        }
    }
    fetchUserData();
    // renderItems();
});
