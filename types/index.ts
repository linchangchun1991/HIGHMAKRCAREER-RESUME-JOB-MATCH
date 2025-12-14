// 学员/简历类型
export interface Student {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  education: string;           // 学历
  major: string;               // 专业
  graduationYear: string;      // 毕业年份
  skills: string[];            // 技能列表
  experience: string;          // 工作/实习经历
  targetPosition: string;      // 目标岗位
  targetCity: string;          // 目标城市
  salaryExpectation?: string;  // 薪资期望
  rawContent: string;          // 原始简历内容
  createdAt: Date;
  updatedAt: Date;
}

// 岗位类型
export interface Job {
  id: string;
  company: string;             // 公司名称
  position: string;            // 岗位名称
  department?: string;         // 部门
  city: string;                // 工作城市
  salaryRange: string;         // 薪资范围
  education: string;           // 学历要求
  experience: string;          // 经验要求
  skills: string[];            // 技能要求
  description: string;         // 岗位描述
  requirements: string;        // 任职要求
  benefits?: string;           // 福利待遇
  status: 'active' | 'closed'; // 状态
  createdAt: Date;
  updatedAt: Date;
}

// 匹配结果类型
export interface MatchResult {
  id: string;
  studentId: string;
  jobId: string;
  score: number;               // 匹配分数 0-100
  dimensions: {
    skills: number;            // 技能匹配度
    education: number;         // 学历匹配度
    experience: number;        // 经验匹配度
    location: number;          // 地点匹配度
    salary: number;           // 薪资匹配度
  };
  aiAnalysis: string;          // AI 分析说明
  recommendation: string;      // 推荐理由
  createdAt: Date;
}
