// API Configuration - 通义千问
const API_KEY = 'sk-9fe20e18ec704475b63fbb27c7f7b32f';
const API_ENDPOINT = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
const MODEL = 'qwen-plus';

// Initialize PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const uploadText = document.getElementById('uploadText');
const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const hologramBox = document.getElementById('hologramBox');
const uploadState = document.getElementById('uploadState');
const terminalOverlay = document.getElementById('terminalOverlay');
const terminalLines = document.getElementById('terminalLines');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const accessBtn = document.getElementById('accessBtn');

let selectedFile = null;
let radarChart = null;

// Upload area click handler
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        if (selectedFile.type === 'application/pdf') {
            analyzeBtn.disabled = false;
            uploadText.textContent = `Selected: ${selectedFile.name}`;
            hideError();
        } else {
            showError('Please upload a PDF file');
            analyzeBtn.disabled = true;
        }
    }
});

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
        uploadArea.style.borderColor = 'rgba(212, 175, 55, 0.6)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'rgba(212, 175, 55, 0.3)';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-gold/60');
    
    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        if (selectedFile.type === 'application/pdf') {
            analyzeBtn.disabled = false;
            uploadText.textContent = `Selected: ${selectedFile.name}`;
            hideError();
        } else {
            showError('Please upload a PDF file');
            analyzeBtn.disabled = true;
        }
    }
});

// Analyze button click handler
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        showError('Please select a PDF file first');
        return;
    }

    try {
        // Hide upload state, show terminal
        uploadState.classList.add('hidden');
        terminalOverlay.classList.remove('hidden');
        analyzeBtn.disabled = true;
        hideError();
        resultsSection.classList.add('hidden');

        // 3秒"假装分析"延迟，展示Terminal动画
        await showCinematicAnalysis();

        // Extract text from PDF
        const resumeText = await extractTextFromPDF(selectedFile);
        
        if (!resumeText || resumeText.trim().length === 0) {
            throw new Error('Unable to extract text from PDF. Please ensure the PDF contains extractable text.');
        }

        // Call 通义千问 API
        const analysisResult = await callQwenAPI(resumeText);

        // Hide terminal, show results
        terminalOverlay.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        // Render results with animations
        await renderResults(analysisResult);

        analyzeBtn.disabled = false;

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An error occurred during analysis. Please try again.');
        terminalOverlay.classList.add('hidden');
        uploadState.classList.remove('hidden');
        analyzeBtn.disabled = false;
    }
});

/**
 * 电影级分析过程 - Terminal 动画
 */
async function showCinematicAnalysis() {
    terminalLines.innerHTML = '';
    const messages = [
        '> Connecting to Global 500 HR Database...',
        '> Scanning Target School List (QS/USNews)...',
        '> Detecting \'Water\' Experience...',
        '> Calculating ATS Match Rate...',
        '> Analyzing Peer Competition Pool...',
        '> Generating Executive Assessment...',
        '> Finalizing Report...'
    ];
    
    for (const msg of messages) {
        await typeTerminalLine(msg, 400);
    }
    
    // 额外等待1秒增加价值感
    await new Promise(resolve => setTimeout(resolve, 1000));
}

/**
 * Terminal typing effect
 */
async function typeTerminalLine(text, delay = 500) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.innerHTML = `<span class="text-blue-400">$</span> <span>${text}</span><span class="terminal-cursor"></span>`;
            terminalLines.appendChild(line);
            resolve();
        }, delay);
    });
}

/**
 * Extract text from PDF file
 */
async function extractTextFromPDF(file) {
    try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        
        let fullText = '';
        
        // Extract text from all pages
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
        }
        
        return fullText.trim();
    } catch (error) {
        console.error('PDF extraction error:', error);
        throw new Error('PDF parsing failed. Please ensure the file format is correct.');
    }
}

/**
 * Call 通义千问 API with the resume text - 教父级校招专家评估
 */
async function callQwenAPI(resumeText) {
    const systemPrompt = `你是一位毒舌但极其专业的中国顶尖校招专家，也是海马职加（HIGHMARK CAREER）的首席产品架构师。你拥有"简历 X 光眼"，一眼就能看穿简历里的"水分"和"伪装"。

请基于 2025-2026 年最严峻的就业形势，对这份留学生简历进行残酷的"拆解"。

**角色定位**：你是中国校招领域的"教父级"专家，阅人无数，以严苛、客观、数据导向著称。

**分析维度要求**：

1. **'含水量'检测 (X-Ray Vision)**：
   - 找出简历中那些**看起来高大上但实际没用的'水'描述**（例如：'参与了某项目'、'负责资料收集'、'协助经理整理文档'）。
   - 识别**真正的'硬核'描述**（例如：'使用 Python 清洗 10w+ 数据'、'独立撰写行研报告'、'负责运营，转化率提升 30%'）。
   - 输出格式：引用原句 -> 毒舌点评 -> 修改建议。

2. **同辈残酷对标 (Peer Ranking)**：
   - 基于候选人的学校（如 QS Top 50）和专业，将其放入**同类竞争池**中进行排名。
   - 估算他在'海马人才库'中的百分位（例如：'在 1000 名 NYU/哥大/UCL 的竞争者中，你排在后 30%'）。
   - 给出扎心评价（如：'和你同校的竞争对手平均都有 2 段大厂实习，而你只有校内社团。'）

3. **职业时间轴 (Timeline Strategy)**：
   - 根据当前时间（假设是校招季前夕），倒推未来 6-12 个月的月度规划。
   - 必须精确到：几月刷题、几月做 PTA、几月投递提前批。

4. **海马产品精准匹配 (Commercial Logic)**：
   - **逻辑判断**：
     - 如果经历空白/大一大二 -> 推荐 **'PTA 远程项目实训'** (补充核心经历)。
     - 如果有经历但缺乏 Big Name/想进大厂 -> 推荐 **'名企远程/实地人事实习'** (大厂背书)。
     - 如果迷茫/不仅缺经历还缺面试技巧 -> 推荐 **'千里马求职全案'** (保姆级陪跑)。
     - 如果目标是顶尖投行/咨询/核心大厂且基础尚可 -> 推荐 **'千里马至尊版 (Diamond)'** (冲刺顶薪)。
   - 输出：推荐产品名称 + 推荐理由（必须结合他的短板说）+ 预计提升效果。

**输出格式**：必须且只能返回纯 JSON 格式，不要包含 Markdown 标记（\`\`\`json ... \`\`\`）。

**JSON 结构（必须严格遵循）**：
{
  "candidate_profile": {
    "tier_label": "青铜 / 白银 / 黄金 / 钻石 / 王者 (选一个)",
    "school_tier": "Target School / Semi-Target / Non-Target",
    "ranking_percentile": "前 5% / 后 40% (具体数字)",
    "ranking_comment": "一句话扎心评价（如：和你同校的竞争对手平均都有 2 段大厂实习，而你只有校内社团。）"
  },
  "score": 75, // 综合竞争力打分 (0-100)
  "ats_pass_rate": 65, // 预估在字节/腾讯/高盛 ATS 系统的关键词命中率 (0-100%)
  "radar_scores": [80, 60, 70, 90, 50, 65], // 对应：学历硬核度, 经历垂直度, 技能稀缺性, 国际化视野, 领导力潜质, 商业Sense
  "executive_summary": "100字以内的毒舌点评（或者淘汰理由）",
  "water_content_detection": [
    {
      "original_text": "简历原句（如：协助经理整理文档）",
      "verdict": "太水了/无效经历/通用废话",
      "expert_comment": "HR 不在乎你帮谁整理了文档，只在乎你从文档里分析出了什么结论。",
      "suggestion": "修改建议（如：改为：通过分析 500+ 份文档，提炼出 3 个核心业务洞察，为团队决策提供数据支撑）"
    }
  ],
  "hard_core_highlights": [
    "识别出的真正亮点1（如：使用 Python 清洗 10w+ 数据，准确率 99.5%）",
    "识别出的真正亮点2"
  ],
  "gap_analysis": {
    "hard_skills": "缺失的硬技能 (SQL/Python/建模等)",
    "soft_skills": "缺失的软素质 (Leadership/Communication)",
    "experience_gap": "与目标岗位的经历差距"
  },
  "career_timeline": [
    { "month": "Current - Month 1", "action": "动作指令（如：立刻补充一段 PTA）" },
    { "month": "Month 2 - Month 3", "action": "动作指令（如：刷完 LeetCode 200 题）" },
    { "month": "Month 4+", "action": "动作指令（如：投递提前批，目标 20 家公司）" }
  ],
  "highmark_solution": {
    "recommended_product": "千里马至尊版 / PTA实训 / 名企实地实习 / 千里马求职全案",
    "reasoning": "为什么推荐这个？（如：你的短板是缺乏名企背书，我们的实地实习能直接给你大厂转正机会。）",
    "expected_outcome": "预计提升效果（如：简历通过率从 10% 提升至 80%）"
  },
  "target_roles": ["建议岗位1", "建议岗位2", "建议岗位3"]
}`;

    const userPrompt = `这是候选人简历内容：\n\n${resumeText}`;

    const requestBody = {
        model: MODEL,
        messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 3000
    };

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error?.message || `API request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        
        // Extract text from response
        let responseText = '';
        if (data.choices && data.choices[0] && data.choices[0].message) {
            responseText = data.choices[0].message.content;
        }

        if (!responseText) {
            throw new Error('API returned invalid data format');
        }

        // Clean the response text
        responseText = responseText.trim();
        if (responseText.startsWith('```json')) {
            responseText = responseText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
        } else if (responseText.startsWith('```')) {
            responseText = responseText.replace(/^```\s*/, '').replace(/\s*```$/, '');
        }

        // Parse JSON
        const analysisResult = JSON.parse(responseText);
        
        // Validate the structure
        if (!analysisResult.candidate_profile && !analysisResult.score) {
            throw new Error('API returned incomplete data structure');
        }

        return analysisResult;

    } catch (error) {
        console.error('API call error:', error);
        if (error instanceof SyntaxError) {
            throw new Error('AI returned invalid data format. Please try again.');
        }
        throw error;
    }
}

/**
 * Render analysis results to the UI - 教父级校招专家报告
 */
async function renderResults(data) {
    // Card A: 核心身价 - 计步器动画
    await animateCounter('scoreNumber', data.score || 0, 1000);

    // Card B: 同辈残酷排位 - Gauge动画
    const percentileText = data.candidate_profile?.ranking_percentile || '-';
    document.getElementById('percentileDisplay').textContent = percentileText;
    
    // 计算百分位数字
    const percentileMatch = percentileText.match(/(\d+)%/);
    let percentile = 50;
    if (percentileMatch) {
        percentile = parseInt(percentileMatch[1]);
        const isBackward = percentileText.includes('后');
        percentile = isBackward ? (100 - percentile) : percentile;
    }
    
    // 更新状态文字
    let statusText = 'Neutral Zone';
    let statusColor = 'text-yellow-400';
    if (percentile >= 80) {
        statusText = 'Offer Zone (Top 20%)';
        statusColor = 'text-green-400';
    } else if (percentile <= 40) {
        statusText = 'Elimination Zone (Bottom 40%)';
        statusColor = 'text-red-400';
    }
    document.getElementById('rankingStatus').textContent = statusText;
    document.getElementById('rankingStatus').className = `text-sm ${statusColor}`;
    
    // 更新Gauge
    await animateGauge(percentile, 1500);
    
    // 更新排名评价
    if (data.candidate_profile?.ranking_comment) {
        // 可以在这里添加排名评价显示
    }

    // Card C: 简历含水量 X-Ray
    const waterContentContainer = document.getElementById('waterContentDetection');
    waterContentContainer.innerHTML = '';
    if (data.water_content_detection && Array.isArray(data.water_content_detection)) {
        data.water_content_detection.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'code-review rounded-lg p-6 mb-4';
            card.innerHTML = `
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <div class="text-red-400 font-semibold mb-2 font-['JetBrains_Mono'] text-sm">ORIGINAL TEXT</div>
                        <div class="text-white/90 mb-4 font-['JetBrains_Mono'] text-sm">
                            <span class="red-underline">${item.original_text || '-'}</span>
                        </div>
                        <div class="text-yellow-400 font-semibold mb-2 font-['JetBrains_Mono'] text-sm">VERDICT</div>
                        <div class="text-white/80 mb-4">${item.verdict || '-'}</div>
                    </div>
                    <div>
                        <div class="font-semibold mb-2 font-['JetBrains_Mono'] text-sm" style="color: #D4AF37;">EXPERT COMMENT</div>
                        <div class="text-white/70 mb-4">${item.expert_comment || '-'}</div>
                        <div class="text-green-400 font-semibold mb-2 font-['JetBrains_Mono'] text-sm">SUGGESTION</div>
                        <div class="text-white/70">${item.suggestion || '-'}</div>
                    </div>
                </div>
            `;
            waterContentContainer.appendChild(card);
        });
    } else {
        waterContentContainer.innerHTML = '<div class="text-white/50 text-center py-8">No water content detected</div>';
    }

    // Card D: 六维能力雷达
    renderRadarChart(data.radar_scores || data.radar || []);

    // Card E: 职业时间轴
    const careerTimelineContainer = document.getElementById('careerTimeline');
    careerTimelineContainer.innerHTML = '';
    if (data.career_timeline && Array.isArray(data.career_timeline)) {
        data.career_timeline.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = `timeline-item ${index === 0 ? 'active' : ''}`;
            div.innerHTML = `
                <div class="font-semibold mb-1 font-['JetBrains_Mono'] text-sm" style="color: #D4AF37;">${item.month || '-'}</div>
                <div class="text-white/80 text-sm">${item.action || '-'}</div>
            `;
            careerTimelineContainer.appendChild(div);
        });
    }

    // Card F: 海马处方签
    if (data.highmark_solution) {
        document.getElementById('recommendedProduct').textContent = data.highmark_solution.recommended_product || '-';
        document.getElementById('productReasoning').textContent = data.highmark_solution.reasoning || '-';
        document.getElementById('expectedOutcome').textContent = data.highmark_solution.expected_outcome || '-';
    }

    // Access button click handler
    accessBtn.onclick = () => {
        // 这里可以链接到销售页面或联系表单
        alert('Redirecting to Highmark Career Solutions...');
        // window.location.href = 'https://your-sales-page.com';
    };
}

/**
 * 计步器动画
 */
async function animateCounter(elementId, targetValue, duration) {
    const element = document.getElementById(elementId);
    const startValue = 0;
    const startTime = performance.now();
    
    return new Promise((resolve) => {
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用easeOut缓动函数
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOut);
            
            element.textContent = currentValue;
            element.classList.add('count-up');
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = targetValue;
                resolve();
            }
        }
        requestAnimationFrame(update);
    });
}

/**
 * Gauge 仪表盘动画
 */
async function animateGauge(percentile, duration) {
    const arc = document.getElementById('gaugeArc');
    const circumference = 2 * Math.PI * 80; // r = 80
    const targetOffset = circumference - (circumference * percentile / 100);
    
    const startOffset = circumference;
    const startTime = performance.now();
    
    return new Promise((resolve) => {
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用easeOut缓动函数
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentOffset = startOffset - (startOffset - targetOffset) * easeOut;
            
            arc.style.strokeDashoffset = currentOffset;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                arc.style.strokeDashoffset = targetOffset;
                resolve();
            }
        }
        requestAnimationFrame(update);
    });
}

/**
 * Render radar chart using Chart.js - 金色主题
 */
function renderRadarChart(radarData) {
    const ctx = document.getElementById('radarChart');
    
    // Destroy existing chart if it exists
    if (radarChart) {
        radarChart.destroy();
    }

    const labels = ['学历硬核度', '经历垂直度', '技能稀缺性', '国际化视野', '领导力潜质', '商业Sense'];
    
    // Ensure we have 6 data points
    const data = radarData.slice(0, 6);
    while (data.length < 6) {
        data.push(0);
    }

    const goldColor = '#D4AF37';
    const blueColor = '#3B82F6';

    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: '竞争力评分',
                data: data,
                backgroundColor: 'rgba(212, 175, 55, 0.15)',
                borderColor: goldColor,
                borderWidth: 2,
                pointBackgroundColor: goldColor,
                pointBorderColor: '#020617',
                pointHoverBackgroundColor: '#020617',
                pointHoverBorderColor: goldColor,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: 'rgba(255, 255, 255, 0.4)',
                        font: {
                            size: 11,
                            family: 'Inter'
                        }
                    },
                    pointLabels: {
                        color: '#ffffff',
                        font: {
                            size: 13,
                            weight: '600',
                            family: 'Inter'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(2, 6, 23, 0.95)',
                    titleColor: goldColor,
                    bodyColor: '#ffffff',
                    borderColor: goldColor,
                    borderWidth: 1,
                    padding: 12,
                    titleFont: {
                        family: 'Inter',
                        weight: '600'
                    },
                    bodyFont: {
                        family: 'Inter'
                    },
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.r + ' 分';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Show error message
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
}
