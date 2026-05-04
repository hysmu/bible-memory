import sys
import re

file_path = r'E:\0503\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS
new_css = """
        /* 관리자 UI 스타일 */
        .management-ui {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #f4f6f8;
            z-index: 2000;
            overflow-y: auto;
            color: #333;
            font-family: 'Noto Sans KR', sans-serif;
            padding: 20px;
        }
        .management-ui.active {
            display: block;
        }
        .mgmt-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .mgmt-header h2 { margin: 0; color: #2c3e50; }
        .btn {
            padding: 8px 16px; border: none; border-radius: 5px;
            cursor: pointer; font-weight: bold; font-size: 14px;
            transition: all 0.2s;
        }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-danger:hover { background: #c0392b; }
        .btn-secondary { background: #95a5a6; color: white; }
        .btn-secondary:hover { background: #7f8c8d; }
        
        .verse-table-container {
            background: white; border-radius: 10px; padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        tr:hover { background: #f1f2f6; }
        
        /* 모달 스타일 */
        .modal-overlay {
            display: none; position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 3000;
            justify-content: center; align-items: center;
        }
        .modal-overlay.active { display: flex; }
        .modal-content {
            background: white; padding: 25px; border-radius: 10px;
            width: 500px; max-width: 90%; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;
            font-family: inherit; font-size: 14px;
        }
        .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
        
        .top-right-btns {
            position: fixed; top: 20px; left: 20px; z-index: 1001;
            display: flex; gap: 10px;
        }
"""
content = content.replace('</style>', new_css + '\n    </style>')

# 2. Add HTML
new_html = """
    <div class="top-right-btns">
        <button class="nav-button" onclick="toggleManagementUI()" style="padding: 8px 16px; font-size:14px;">⚙️ 관리자 모드</button>
    </div>

    <!-- 관리자 UI -->
    <div class="management-ui" id="managementUI">
        <div class="mgmt-header">
            <h2>성경 암송 자료 관리</h2>
            <div style="display:flex; gap: 10px;">
                <button class="btn btn-secondary" onclick="exportData()">JSON 백업</button>
                <input type="file" id="importFile" style="display:none;" accept=".json" onchange="importData(event)">
                <button class="btn btn-secondary" onclick="document.getElementById('importFile').click()">JSON 복원</button>
                <button class="btn btn-primary" onclick="openModal('add')">+ 새 구절 추가</button>
                <button class="btn btn-secondary" onclick="toggleManagementUI()">닫기 ✖</button>
            </div>
        </div>
        
        <div class="verse-table-container">
            <div style="margin-bottom: 15px; display:flex; gap: 10px; align-items:center;">
                <label>카테고리 필터:</label>
                <select id="categoryFilter" onchange="renderTable()" style="padding: 5px; border-radius: 5px; border: 1px solid #ccc;">
                    <option value="all">전체보기</option>
                </select>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">순번</th>
                        <th style="width: 80px;">분류</th>
                        <th style="width: 100px;">장절</th>
                        <th>구절</th>
                        <th style="width: 50px;">아이콘</th>
                        <th style="width: 120px;">관리</th>
                    </tr>
                </thead>
                <tbody id="verseTableBody">
                    <!-- JS로 채워짐 -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- 추가/수정 모달 -->
    <div class="modal-overlay" id="verseModal">
        <div class="modal-content">
            <h3 id="modalTitle" style="margin-top:0; margin-bottom: 20px; color:#2c3e50;">구절 추가</h3>
            <input type="hidden" id="editId">
            <div class="form-group">
                <label>장절 (예: 창 1:1)</label>
                <input type="text" id="inputRef" placeholder="성경 장절 입력">
            </div>
            <div class="form-group">
                <label>구절 내용 (엔터로 줄바꿈 구분)</label>
                <textarea id="inputLines" rows="5" placeholder="구절을 입력하세요. 줄바꿈을 하면 화면에서도 줄바꿈이 됩니다."></textarea>
            </div>
            <div class="form-group">
                <label>카테고리</label>
                <input type="text" id="inputCategory" placeholder="예: 구원, 창조, 믿음 등">
            </div>
            <div class="form-group">
                <label>아이콘 (이모지)</label>
                <input type="text" id="inputIcon" placeholder="예: 🌍✨">
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="closeModal()">취소</button>
                <button class="btn btn-primary" onclick="saveVerse()">저장</button>
            </div>
        </div>
    </div>
"""
content = content.replace('<div class="progress-bar" id="progressBar"></div>', new_html + '\n    <div class="progress-bar" id="progressBar"></div>')

# 3. Modify JS Data
content = content.replace('const verses = [', 'const defaultVerses = [')

js_logic = """
        let appData = [];
        const STORAGE_KEY = 'bible_memory_verses_data';

        // 데이터 초기화
        function loadData() {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                try {
                    appData = JSON.parse(saved);
                } catch (e) {
                    console.error('Data parse error', e);
                    initDefaultData();
                }
            } else {
                initDefaultData();
            }
            
            let modified = false;
            appData.forEach((v, index) => {
                if (!v.id) { v.id = Date.now() + index; modified = true; }
                if (!v.category) { v.category = '기본'; modified = true; }
            });
            if(modified) saveData();
            
            createSlides();
            showSlide(0);
        }

        function initDefaultData() {
            appData = JSON.parse(JSON.stringify(defaultVerses));
            appData.forEach((v, i) => {
                v.id = Date.now() + i;
                v.category = '기본';
            });
            saveData();
        }

        function saveData() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(appData));
        }

        // ================= 관리자 기능 =================
        function toggleManagementUI() {
            const ui = document.getElementById('managementUI');
            if (ui.classList.contains('active')) {
                ui.classList.remove('active');
                createSlides();
                showSlide(0);
            } else {
                ui.classList.add('active');
                updateCategoryFilter();
                renderTable();
            }
        }

        function updateCategoryFilter() {
            const categories = [...new Set(appData.map(v => v.category))];
            const select = document.getElementById('categoryFilter');
            const currentVal = select.value;
            select.innerHTML = '<option value="all">전체보기</option>';
            categories.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                select.appendChild(opt);
            });
            if(categories.includes(currentVal)) select.value = currentVal;
        }

        function renderTable() {
            const tbody = document.getElementById('verseTableBody');
            tbody.innerHTML = '';
            
            const filter = document.getElementById('categoryFilter').value;
            let displayData = appData;
            if (filter !== 'all') {
                displayData = appData.filter(v => v.category === filter);
            }

            displayData.forEach((v, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td><span style="background:#eee; padding:2px 6px; border-radius:4px; font-size:12px;">${v.category || '기본'}</span></td>
                    <td><b>${v.ref}</b></td>
                    <td style="white-space:pre-wrap; font-size:13px;">${v.lines.join('\\n')}</td>
                    <td>${v.icon || ''}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" onclick="openModal('edit', ${v.id})">수정</button>
                        <button class="btn btn-danger" style="padding:4px 8px; font-size:12px;" onclick="deleteVerse(${v.id})">삭제</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function openModal(mode, id = null) {
            const modal = document.getElementById('verseModal');
            document.getElementById('modalTitle').textContent = mode === 'add' ? '새 구절 추가' : '구절 수정';
            
            if (mode === 'edit') {
                const verse = appData.find(v => v.id === id);
                if(verse) {
                    document.getElementById('editId').value = verse.id;
                    document.getElementById('inputRef').value = verse.ref;
                    document.getElementById('inputLines').value = verse.lines.join('\\n');
                    document.getElementById('inputCategory').value = verse.category || '';
                    document.getElementById('inputIcon').value = verse.icon || '';
                }
            } else {
                document.getElementById('editId').value = '';
                document.getElementById('inputRef').value = '';
                document.getElementById('inputLines').value = '';
                document.getElementById('inputCategory').value = '새 분류';
                document.getElementById('inputIcon').value = '✨';
            }
            
            modal.classList.add('active');
        }

        function closeModal() {
            document.getElementById('verseModal').classList.remove('active');
        }

        function saveVerse() {
            const id = document.getElementById('editId').value;
            const ref = document.getElementById('inputRef').value.trim();
            const linesStr = document.getElementById('inputLines').value.trim();
            const category = document.getElementById('inputCategory').value.trim() || '기본';
            const icon = document.getElementById('inputIcon').value.trim();
            
            if(!ref || !linesStr) {
                alert('장절과 구절 내용을 입력해주세요.');
                return;
            }
            
            const lines = linesStr.split('\\n').map(l => l.trim()).filter(l => l);
            
            if (id) {
                const idx = appData.findIndex(v => v.id == id);
                if(idx !== -1) {
                    appData[idx] = { ...appData[idx], ref, lines, category, icon };
                }
            } else {
                const newId = Date.now();
                appData.push({ id: newId, num: appData.length + 1, ref, lines, category, icon });
            }
            
            saveData();
            closeModal();
            updateCategoryFilter();
            renderTable();
        }

        function deleteVerse(id) {
            if(confirm('정말 이 구절을 삭제하시겠습니까?')) {
                appData = appData.filter(v => v.id !== id);
                saveData();
                updateCategoryFilter();
                renderTable();
            }
        }

        function exportData() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href",     dataStr);
            downloadAnchorNode.setAttribute("download", "bible_verses_backup.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }

        function importData(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const imported = JSON.parse(e.target.result);
                    if(Array.isArray(imported)) {
                        appData = imported;
                        saveData();
                        updateCategoryFilter();
                        renderTable();
                        alert('데이터가 성공적으로 복원되었습니다.');
                    } else {
                        alert('잘못된 형식의 파일입니다.');
                    }
                } catch(err) {
                    alert('파일을 읽는 중 오류가 발생했습니다.');
                }
                event.target.value = '';
            };
            reader.readAsText(file);
        }
"""
content = content.replace('let currentSlide = 0;', js_logic + '\n        let currentSlide = 0;')

content = content.replace('verses.forEach((verse, index) => {', 'appData.forEach((verse, index) => {')

content = re.sub(r'<p>73개 핵심 성경 구절</p>', '<p id="titleSubtitle">핵심 성경 구절</p>', content)

create_slide_patch = """function createSlides() {
            const presentation = document.getElementById('presentation');
            const existingSlides = presentation.querySelectorAll('.slide:not(.title-slide)');
            existingSlides.forEach(s => s.remove());
            
            const subtitle = document.getElementById('titleSubtitle');
            if(subtitle) subtitle.textContent = `${appData.length}개 핵심 성경 구절`;
"""
content = content.replace("""function createSlides() {
            const presentation = document.getElementById('presentation');""", create_slide_patch)

content = content.replace('createSlides();\n        showSlide(0);', 'loadData();')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully!")
